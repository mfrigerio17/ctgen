import os, logging, copy, pathlib
import lupa
from kgprim.ct.repr.mxrepr import MatrixRepresentation

import ctgen_backends.cpp_iitrbd as thisBackend
import ctgen.common

logger = logging.getLogger(__name__)



class Generator:
    def __init__(self, config):
        self.config = config
        self.lua_codegen_cfg = config.getTextGeneratorsConfiguration()

        pathToHere   = pathlib.Path(__file__).parent
        pathToTempls = pathToHere.joinpath("templates")

        self.lua_generator = self._luaExec(pathToHere.joinpath("generator.lua"))
        self._luaExec(pathToTempls.joinpath("cmake.lua"))
        self._luaExec(pathToTempls.joinpath("header.lua"))
        self._luaExec(pathToTempls.joinpath("source.lua"))
        self._luaExec(pathToTempls.joinpath("tests.lua"))

        backend_lua = self._luaExec(pathToHere.joinpath("backend.lua"))
        self.backendSpecifics = backend_lua.getSpecifics(self.lua_codegen_cfg)

    def _luaExec(self, sourcefile) :
        luaCodeSrc = open( sourcefile, "r")
        luaret = thisBackend.luaRuntime.execute(luaCodeSrc.read())
        luaCodeSrc.close()
        return luaret

    def generate_code(self, ctModelMetadata, matricesMetadata):
        mxMetadata = None
        if MatrixRepresentation.homogeneous in matricesMetadata:
            mxMetadata = matricesMetadata[MatrixRepresentation.homogeneous]
        else :
            logger.error("This generator requires the metadata for the homogeneous coordinate representation of the transformation matrices")
            return (False,''), (False,'')

        # Resolve the symbols of every matrix, put them in a map keyed in the
        # same way as the matrices-metadata argument
        resolver = ctgen.common.SymbolicCoefficientsResolver(self.backendSpecifics)
        resolvedMatrices = {}
        for name, meta in mxMetadata.items():
            res = resolver.resolveSymbols(meta)
            resolvedMatrices[name] = res

        generators = self.lua_generator.generators(
            self.backendSpecifics,
            ctModelMetadata, mxMetadata, resolvedMatrices, self.lua_codegen_cfg)
        self.generators = generators

        okh, headerCode = generators.headerFileCode()
        if not okh :
            logger.error("Header code generation for model '{0}' failed".format(ctModelMetadata.name))
            logger.error(headerCode)

        oks, sourceCode = generators.sourceFileCode()
        if not oks :
            logger.error("Source code generation for model '{0}' failed:\n{1}"
                .format(ctModelMetadata.name, sourceCode))

        return (okh,headerCode), (oks,sourceCode)


    def generate(self, ctModelMetadata, matricesMetadata):
        outputDir = self.config.getOutputDirectory()
        def write_file(code, filepath):
            fpath = os.path.join( outputDir, filepath )
            f = open(fpath, 'w')
            f.write(code)
            f.close()

        fileNames = self.config.getOutputFileNames()
        #implext = '.h' if self.config.generateTemplates() else '.cpp'

        hpath = self.config.getHeadersPath()
        fullhpath = os.path.join(outputDir, hpath)
        if not os.path.exists(fullhpath):  # create it if it is not there
            os.makedirs(fullhpath)

        (okh,header), (oks,source) = self.generate_code(ctModelMetadata, matricesMetadata)
        if okh :
            write_file(header, os.path.join(hpath, fileNames.header) )
        if oks :
            fname = fileNames.source
            if self.config.generateTemplates() :
                fname = os.path.join(hpath, fname + ".h")
            write_file(source, fname)

        if (not okh) or (not oks) :
            return

        ok, code = self.generators.main()
        if not ok :
            logger.error("Failed to generate sample main file: " + code)
        else:
            write_file(code, 'main.cpp')

        # tests
        testsdir = fileNames.test.subdir
        # the test subdirectory for the sources
        fulldir = os.path.join( outputDir, testsdir )
        if not os.path.exists(fulldir) :
            os.makedirs(fulldir)
        # and now for the header file
        fulldir = os.path.join( fullhpath, testsdir )
        if not os.path.exists(fulldir) :
            os.makedirs(fulldir)

        ok, code = self.generators.tests.header()
        if not ok :
            logger.error("Failed to generate tests header: " + code)
        else:
            hpath_test = os.path.join(hpath, testsdir)
            write_file(code, os.path.join(hpath_test, fileNames.test.header))

        ok, code = self.generators.tests.source()
        if not ok :
            logger.error("Failed to generate tests source: " + code)
        else:
            write_file(code, os.path.join(testsdir, fileNames.test.source))

        for tf in ctModelMetadata.transformsMetadata :
            ok, code = self.generators.tests.per_tf_main(tf)
            if not ok :
                logger.error("Failed to generate test file: " + code)
            else:
                write_file(code, os.path.join(testsdir, fileNames.test.per_tf_source(tf)))

        ok, code = self.generators.cmake()
        if not ok :
            logger.error("Failed to generate cmake file: " + code)
        else:
            write_file(code, "CMakeLists.txt")
