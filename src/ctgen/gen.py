import os, sys, pkgutil, importlib, argparse, logging, pathlib
import yaml
import lupa

import kgprim.core as primitives
import kgprim.ct as ct
import kgprim.ct.frommotions
import kgprim.ct.repr.mxrepr as mxrepr
from kgprim.ct.metadata import TransformMetadata
from kgprim.ct.metadata import TransformsModelMetadata
from kgprim.ct.repr.mxrepr import MatrixReprMetadata
import motiondsl.motiondsl as motdsl

import ctgen_backends
import ctgen.common
import ctgen.dataset as dataset


logger = logging.getLogger(__package__) # use '__package__' to make this the root logger


def getDesiredTransforms(datain):
    dt = []
    for item in datain:
        rf = primitives.Frame(item['right_frame'])
        lf = primitives.Frame(item['left_frame'])
        dt.append( ct.models.CoordinateTransformPlaceholder(rightFrame=rf, leftFrame=lf))
    return dt



def printModelInfo(ctModel, ostream):
    ctModelMeta = TransformsModelMetadata( ctModel )
    ostream.write("Model name: '{0}'\n".format(ctModel.name))
    ostream.write("Variables:\n" + ctModelMeta.variables.__str__() )
    ostream.write("\nParameters:\n" + ctModelMeta.parameters.__str__() )
    ostream.write("\nTransforms count: " + str( len(ctModel.transforms) ) )


default_backend = 'octave'
fold_constants_str = 'fold-constants'
reify_floats_str = 'reify-floats'


def main():
    formatter = logging.Formatter('%(levelname)s (%(name)s) : %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.setLevel(logging.WARN)
    logger.addHandler(handler)
    ctlog = logging.getLogger('ct')
    ctlog.setLevel(logging.WARN)
    backendslog = logging.getLogger(ctgen_backends.__name__)
    backendslog.setLevel(logging.WARN)
    backendslog.addHandler(handler)
    #ctlog.addHandler(handler)

    argparser = argparse.ArgumentParser(prog='ctgen', description='Generates code for coordinate transformation matrices')
    argparser.add_argument('motdsl', metavar='poses-model', help='Motion-DSL file with the specification of relative poses')
    argparser.add_argument('-o', '--output', dest='output', metavar='DIR', help='destination folder (defaults to /tmp/ctgen)')
    argparser.add_argument('-l', '--lang', dest='lang', metavar='LANG', help='desired programming language (defaults to {0})'.format(default_backend))
    argparser.add_argument('-c', '--config', dest='cfg', metavar='FILE', help='YAML configuration for the command line tool; command line switches override entries in this file')
    argparser.add_argument('-cc', '--code-config', dest='code_cfg', metavar='FILE', help='LUA config file overriding the defaults of the selected code generator')
    argparser.add_argument('-s', '--gen-dataset', dest='dataset_size', type=int, metavar='COUNT', help='generate numerical datasets with COUNT entries (no code is generated)')
    argparser.add_argument('--fold-constants', dest='cfolding', action='store_const', const=fold_constants_str,  help='force constants folding')
    argparser.add_argument('--reify-floats'  , dest='cfolding', action='store_const', const=reify_floats_str  , help='prevent any constants folding')
    argparser.add_argument('-d', '--debug', action='store_true', help='print model information')
    argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='lower the logging level to DEBUG')

    group = argparser.add_argument_group('Representations', 'Choose the matrix representation to be generated. Defaults to homogeneous coordinates')
    group.add_argument('-xR', dest='reprs', action='append_const',
                       help='pure rotation matrices',
                       const=mxrepr.MatrixRepresentation.pure_rotation)
    group.add_argument('-xH', dest='reprs', action='append_const',
                       help='homogeneous coordinates',
                       const=mxrepr.MatrixRepresentation.homogeneous)
    group.add_argument('-xM', dest='reprs', action='append_const',
                       help='spatial coordinates for motion vectors',
                       const=mxrepr.MatrixRepresentation.spatial_motion)
    group.add_argument('-xF', dest='reprs', action='append_const',
                       help='spatial coordinates for force vectors',
                       const=mxrepr.MatrixRepresentation.spatial_force)

    # Dynamically load the available backends
    # This is a very simple plugin mechanism
    backends = {}
    for module_info in pkgutil.iter_modules( ctgen_backends.__path__ ):
        if module_info.ispkg :
            backend_module_absolute = "{ns}.{backend}.backend".format(
                ns=ctgen_backends.__name__, backend=module_info.name
            )
            logger.info("Attempt loading module {0}".format(backend_module_absolute))
            module = importlib.import_module(backend_module_absolute)
            argsgroup = argparser.add_argument_group(
                module.backend_name + ' backend', module.backend_description)
            module.add_cmdline_arguments(argsgroup) # backend-specific cmd line switches
            backends[ module.backend_tag ] = module
            logger.info("Loaded backend '{0}'".format(module.backend_name))

    args = argparser.parse_args()

    if args.verbose :
        logger.setLevel(logging.DEBUG)
        ctlog.setLevel(logging.DEBUG)
        backendslog.setLevel(logging.DEBUG)

    # Load the input model
    inpath = pathlib.Path(args.motdsl)
    if not inpath.exists():
        logger.error("Cannot find input file '%s'", inpath.resolve())
        return -1

    motionsModel = motdsl.dsl.modelFromFile(args.motdsl)
    posesModel   = motdsl.toPosesSpecification(motionsModel)

    # Parse the configuration options
    configIn = {}
    if args.cfg is not None :
        try :
            istream  = open(args.cfg, 'r')
            configIn = yaml.safe_load(istream)
            istream.close()
        except OSError as exc :
            logger.warning("Could not read configuration file '{0}': {1}".format(args.cfg, exc.strerror))


    if 'desired-transforms' in configIn :
        dt = getDesiredTransforms( configIn['desired-transforms'] )
        ctModel = ct.frommotions.motionsToCoordinateTransforms(posesModel, whichTransforms=dt, retModelName=posesModel.name)
        logger.debug("Found desired-transforms configuration")
    else :
        logger.debug("No desired-transforms configuration, generating default transforms")
        ctModel = ct.frommotions.motionsToCoordinateTransforms(posesModel)

    if args.debug :
        printModelInfo(ctModel, sys.stdout)
        return 0

    # Output directory
    #
    odir = configIn.get('output') # first choice
    if args.output is not None :  # command-line override
        odir = args.output
    odir = odir or '/tmp/ctgen'   # default value, if it is still unset
    if not os.path.exists(odir):  # create it if it is not there
        os.makedirs(odir)
    logger.debug("Output directory set to '{0}'".format(odir) )

    # Dataset generation
    if args.dataset_size is not None :
        for tr in ctModel.transforms :
            H  = mxrepr.hCoordinatesSymbolic(tr)
            tr_info = TransformMetadata(tr)
            dataset.generateDataset(tr_info, H, args.dataset_size, 'bin', odir)
        return 0


    # Figure out the desired representation
    # Command line has priority over configuration file
    reprs = set()
    reprs_cmdline = args.reprs
    if reprs_cmdline is not None :
        reprs.update( reprs_cmdline )
    else :
        reprs_cfgfile = configIn.get('representations')
        if reprs_cfgfile is not None :
            reprs.update( [mxrepr.MatrixRepresentation[r] for r in reprs_cfgfile] )
        else :
            # no input, fall back on default
            reprs.add(mxrepr.MatrixRepresentation.homogeneous)
    logger.debug("Chosen representations: {0}".format([r.name for r in reprs]))


    generatorConfig = {}
    generatorConfig['outDir'] = odir

    # Code generation backend
    #
    lang = configIn.get('backend') # from config file, may be None
    if args.lang is not None :     # command line switch overrides config file
        lang = args.lang
    if lang is None :
        lang = default_backend # default value, no cmdline switch nor config file entry
    if lang not in backends.keys() :
        logger.error("Unknown language tag '{0}'".format(lang))
        return -1

    code_config = configIn.get('backend-config')
    if args.code_cfg is not None :
        code_config = args.code_cfg
    generatorConfig['textConfig'] = code_config # may be None

    # Constant folding
    #
    cfold = configIn.get('constant-folding')
    if args.cfolding is not None : cfold = args.cfolding
    if cfold is None             : cfold = 'default'
    if cfold == fold_constants_str :
        logger.debug("Will force folding of the values of the model constants")
        transforms = []
        for tf in ctModel.transforms :
            transforms.append( ctgen.common.foldConstants(tf) )
        ctModel = kgprim.ct.models.CTransformsModel(ctModel.name, transforms)
    elif cfold == reify_floats_str :
        logger.debug("Will create named constants for the float-literals in the model")
        transforms = []
        for tf in ctModel.transforms :
            transforms.append( ctgen.common.floatLiteralsAsConstants(tf) )
        ctModel = kgprim.ct.models.CTransformsModel(ctModel.name, transforms)
    else:
        logger.debug("Adopting the default policy for constant folding")

    ctModelMeta = TransformsModelMetadata( ctModel )

    # Generate code
    generator = backends[ lang ].get_generator( ctModel, generatorConfig, args )

    allMetadata = {}
    for repr in reprs:
        metadata = {}
        for tf_info in ctModelMeta.transformsMetadata :
            MX = mxrepr.symbolic[repr].matrix_repr(tf_info.ct)
            meta = MatrixReprMetadata(tf_info, MX, repr)
            metadata[tf_info.name] = meta
        allMetadata[repr] = metadata

    generator.generate( ctModelMeta, allMetadata )


if __name__ == '__main__':
    main()
