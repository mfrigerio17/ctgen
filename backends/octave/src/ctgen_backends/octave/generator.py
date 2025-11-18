import logging, pathlib

import ctgen_backends.octave as thisBackend
import ctgen.common
from ctgen.pyutils import open_utf8_reading
from ctgen.pyutils import open_utf8_writing
from kgprim.ct.repr.mxrepr import MatrixRepresentation

logger = logging.getLogger(__name__)


class Generator:
    def __init__(self, lua_configuration_table):
        self.lua_codegen_cfg = lua_configuration_table

        pathToHere   = pathlib.Path(__file__).parent
        pathToTempls = pathToHere

        self._luaExec(pathToTempls.joinpath("tests_tpl.lua")) # loads a global
        self.luaGeneratorsF = self._luaExec(pathToHere.joinpath("generator.lua"))

        backend_lua = self._luaExec(pathToHere.joinpath("backend.lua"))
        self.backendSpecifics = backend_lua.getSpecifics(self.lua_codegen_cfg)

    def _luaExec(self, sourcefile) :
        luaCodeSrc = open_utf8_reading(sourcefile)
        luaret = thisBackend.luaRuntime.execute(luaCodeSrc.read())
        luaCodeSrc.close()
        return luaret

    def generate_code(self, ctModelMetadata, matricesMetadata):
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


    def generate(self, ctModelMetadata, matricesMetadata, outputDirectory):
        allCode, constants, tests = self.generate_code(ctModelMetadata, matricesMetadata)

        def fwrite(ok, filename, text) :
            fpath = outputDirectory / filename
            if ok :
                with open_utf8_writing(fpath) as f:
                    f.write(text)
            else :
                logger.info("Skipping file '{f}', as code generation failed".format(f=fpath))


        for repr in allCode.keys() :
            mxsMeta = matricesMetadata[repr]
            codeDict= allCode[repr]
            for mxName in mxsMeta.keys() :
                mxMeta  = mxsMeta[mxName]
                ok,codeOrError = codeDict[mxName]
                filename = self.lua_codegen_cfg.meta.tf_class.class_name(mxMeta) + ".m"
                fwrite(ok, filename, codeOrError)

        ok, codeOrError = constants[:]
        filename = self.lua_codegen_cfg.meta.constants_class.class_name(ctModelMetadata) + ".m"
        fwrite(ok, filename, codeOrError)

        ok, codeOrError = tests[:]
        fwrite(ok, "tests.m", codeOrError)

    def _logerr(self, ok, errmsg, model, tr ):
        if not ok :
            logger.error("Code generation failed - model '{model}', transform '{tr}': {err}"
                         .format(model=model, tr=tr, err=errmsg) )


