import logging, os, pathlib

import ctgen_backends.octave as thisBackend
import ctgen.common
from kgprim.ct.repr.mxrepr import MatrixRepresentation

logger = logging.getLogger(__name__)


class Generator:
    def __init__(self, configurator):
        self.config  = configurator
        self.lua_codegen_cfg = configurator.getTextGeneratorsConfiguration()

        pathToHere   = pathlib.Path(__file__).parent
        pathToTempls = pathToHere

        self._luaExec(pathToTempls.joinpath("tests_tpl.lua")) # loads a global
        self.luaGeneratorsF = self._luaExec(pathToHere.joinpath("generator.lua"))

        backend_lua = self._luaExec(pathToHere.joinpath("backend.lua"))
        self.backendSpecifics = backend_lua.getSpecifics(self.lua_codegen_cfg, configurator.ctModel)

    def _luaExec(self, sourcefile) :
        luaCodeSrc = open( sourcefile, "r")
        luaret = thisBackend.luaRuntime.execute(luaCodeSrc.read())
        luaCodeSrc.close()
        return luaret

    def _generate_code(self, ctModelMetadata, matricesMetadata):
        '''
        Returns a dictionary of dictionaries of the same shape as the given
        `matricesMetadata`: the outer dictionary is indexed with a
        `MatrixRepresentation` value, and it has as many values as the given
        `matricesMetadata`. The inner dictionary is indexed by the name of a
        transform. Any value of the nested dictionaries is a tuple with a
        boolean success flag and the generated code.
        This function returns a second value, which is itself a tuple, with
        the success flag and the generated code for the model constants.
        '''
        if not self._consistentArgs(ctModelMetadata) :
            return None

        # Resolve the symbols of every matrix, put them in a map keyed in the
        # same way as the matrices-metadata argument
        resolver = ctgen.common.SymbolicCoefficientsResolver(self.backendSpecifics)

        ret = {}
        for repr in matricesMetadata.keys() :
            mxsMeta = matricesMetadata[repr]

            resolvedMatrices = {}
            for name, meta in mxsMeta.items():
                res = resolver.resolveSymbols(meta)
                resolvedMatrices[name] = res

            self.luaGen = self.luaGeneratorsF(self.backendSpecifics,
                ctModelMetadata, resolvedMatrices, self.lua_codegen_cfg)

            code = {}
            for mxName in mxsMeta.keys() :
                mxMeta = mxsMeta[mxName]
                ok, codeOrError = self.luaGen.matrixFunction(mxMeta)
                self._logerr(ok, codeOrError, ctModelMetadata.name, mxMeta.ctMetadata.name)
                code[mxName] = (ok, codeOrError)
            ret[repr] = code

        ok, codeOrError = self.luaGen.modelConstants()
        if not ok :
            logger.error("Code generation of the constants of model '{0}' failed: {1}".format(ctModelMetadata.name, codeOrError))

        okt = False
        testscode = ""
        if MatrixRepresentation.homogeneous in matricesMetadata.keys():
            okt, testscode = self.luaGen.tests(matricesMetadata[MatrixRepresentation.homogeneous])
            if not okt :
                logger.error("Code generation of the tests of model '{0}' failed: {1}".format(ctModelMetadata.name, testscode))
        else :
            errmsg = "Test generation only available for homogeneous transforms"
            logger.warning(errmsg)
            okt = False
            testscode = errmsg

        return ret, (ok, codeOrError), (okt, testscode)


    def generate(self, ctModelMetadata, matricesMetadata):
        if not self._consistentArgs(ctModelMetadata) :
            return None

        allCode, constants, tests = self._generate_code(ctModelMetadata, matricesMetadata)

        odir = self.config.getOutputDirectory()
        def fwrite(ok, filename, text) :
            fpath = os.path.join(odir, filename)
            if ok :
                f = open(fpath, 'w')
                f.write(text)
                f.close()
            else :
                logger.info("Skipping file '{f}', as code generation failed".format(f=fpath))


        for repr in allCode.keys() :
            mxsMeta = matricesMetadata[repr]
            codeDict= allCode[repr]
            for mxName in mxsMeta.keys() :
                mxMeta  = mxsMeta[mxName]
                ok,codeOrError = codeDict[mxName]
                filename = self.config.getClassName(mxMeta) + ".m"
                fwrite(ok, filename, codeOrError)

        ok, codeOrError = constants[:]
        filename = self.lua_codegen_cfg.constants.container_name(ctModelMetadata) + "_init.m"
        fwrite(ok, filename, codeOrError)

        ok, codeOrError = tests[:]
        fwrite(ok, "tests.m", codeOrError)

    def _logerr(self, ok, errmsg, model, tr ):
        if not ok :
            logger.error("Code generation failed - model '{model}', transform '{tr}': {err}"
                         .format(model=model, tr=tr, err=errmsg) )

    def _consistentArgs(self, ctModelMetadata):
        abort = False
        if self.config is None :
            logger.error("Configurator not set. Aborting")
            abort = True
        if self.config.ctModel != ctModelMetadata.ctModel :
             logger.warning("The coordinate transform model of the given metadata object does not match the one used to configure this generator")
             #abort = True
        #TODO more?
        if abort :
            logger.error("Inconsistent arguments - aborting")
        return not abort



