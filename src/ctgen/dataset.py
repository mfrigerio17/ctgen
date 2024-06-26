import os, sys, struct, logging, random
import numpy.random

import motiondsl.motiondsl as motdsl
import kgprim.ct as ct
import kgprim.ct.frommotions
import kgprim.ct.repr.mxrepr as mxrepr
import kgprim.ct.metadata
import ctgen.common


logger = logging.getLogger(__name__)

def addEntryCSVDataset(q, params, mx, out_stream):
    parts = []
    if len(q)>0:
        parts.append( ','.join(map(str,q)) ) # comma separated print of the q array
    if len(params)>0:
        parts.append( ','.join(map(str,params)) )
    # The position vector
    parts.append( ','.join(map(str,mx[0:3,3])) )
    # The rotation matrix, row major
    parts.append( ','.join(map(str,mx[0,0:3])) )
    parts.append( ','.join(map(str,mx[1,0:3])) )
    parts.append( ','.join(map(str,mx[2,0:3])) )

    out_stream.write(','.join(parts) + '\n')

def addEntryBinDataset(q, params, mx, out_stream):
    for qi in q :
        out_stream.write( struct.pack("f", qi ) )

    for pi in params:
        out_stream.write( struct.pack("f", pi) )

    # The position vector
    out_stream.write( struct.pack("fff", * mx[0:3, 3]) )

    # The rotation matrix, row-major
    for vec in [0,1,2] :
        for r in range(3):
            out_stream.write( struct.pack("f", mx[vec,r]) )


def generateDataset(tr_info, matrix, datasetSize, whichone, path='.'):
    '''
    Create a dataset file with the coefficients of the given homogeneous
    transformation matrix.

    The dataset can be used to test the implementation of the same matrix in
    different languages.

    A dataset is a sequence of entries, each entry a sequence of floating point
    values. The first values correspond to the variables the matrix depends on,
    then to the coefficients of the position vector, then to the coefficients
    of the rotation matrix, in row-major order.

    If the matrix is constant, there will not be any value for the variables.
    '''

    outfile = None
    addItem = None
    filen = os.path.join(path, "dataset_{0}".format(tr_info.name))
    if whichone == 'csv' :
        outfile = open(filen+'.csv', "w")
        addItem = addEntryCSVDataset
    elif whichone == "bin":
        outfile = open(filen+'.bin', "bw")
        addItem = addEntryBinDataset
    else :
        print("Unrecognized format '{}'".format(whichone), file=sys.stderr)
        return
    for _ in range(datasetSize) :
        q = numpy.random.rand( len(tr_info.variables) )
        pvalues_list = []
        pvalues_dict = {}
        for p in tr_info.parameters: # this is a ordered set
            value = random.random()
            pvalues_dict[p] = value
            pvalues_list.append(value)
        matrix.setParametersValue(pvalues_dict)
        mx = matrix.eval(*q)
        addItem(q, pvalues_list, mx, outfile)

    logger.debug("Generated dataset '{0}' with {1} entries, for matrix '{2}' ({3} variable(s))"
                 .format(outfile.name, datasetSize, tr_info.name, len(tr_info.vars)) )
    outfile.close()



def main():
    '''
    A sample demonstrating the creation of a numerical dataset
    '''

    modelpath    = os.path.join(os.path.dirname(__file__), '../../sample/model.motdsl')
    motionsModel = motdsl.dsl.modelFromFile(modelpath)
    posesModel   = motdsl.toPosesSpecification(motionsModel)
    ctModel      = ct.frommotions.motionsToCoordinateTransforms(posesModel)

    tr = ctModel.transforms[0]
    H  = mxrepr.hCoordinatesSymbolic.matrix_repr(tr)
    tr_info = kgprim.ct.metadata.TransformMetadata(tr)

    generateDataset(tr_info, H, 100, 'bin')


if __name__ == '__main__':
    main()
