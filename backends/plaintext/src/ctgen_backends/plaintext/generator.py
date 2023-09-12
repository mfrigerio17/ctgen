import logging, pathlib
import lupa
import ctgen.common
from kgprim.ct.repr.mxrepr import MatrixRepresentation

logger = logging.getLogger(__name__)


class Generator:
    '''
    Main code generator class for this backend, exposing the public function to
    actually generate text.
    '''

    def __init__(self):
        '''
        Creates the Lua runtime and executes common Lua sources, to have the
        necessary global symbols available in the runtime.
        '''

        # The Lua environment used by this generator
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)

        # Load the common Lua code
        pathToCommon = pathlib.Path(ctgen.common.__file__).parent

        self._loadLuaCode( pathToCommon.joinpath("common.lua") )
        self._loadLuaCode( pathToCommon.joinpath("assignments.lua") )

        # Load the textual templates of this package.
        # Note the order matters, related to who needs who
        pathToHere = pathlib.Path(__file__).parent

        pathToTemplates = pathToHere.joinpath("templates")
        self._loadLuaCode( pathToTemplates.joinpath("main.lua") )

        backend = self._loadLuaCode( pathToHere.joinpath("backend.lua") )
        self.backendSpecifics = backend.getSpecifics( None )

        self.luaGenerator = self._loadLuaCode( pathToHere.joinpath("generator.lua") )


    def _loadLuaCode(self, sourceFilePath):
        luaCodeSrc = open( sourceFilePath, "r")
        ret = self.lua.execute(luaCodeSrc.read()) # loads a global
        luaCodeSrc.close()
        return ret

    def generate_code(self, ctModelMetadata, allMatricesMetadata):
        '''
        Generate the code(text) for the given coordinate transforms, according
        to the text templates of this package.
        '''

        matricesMetadata = allMatricesMetadata[MatrixRepresentation.homogeneous]

        # Resolve the symbols of every matrix, put them in a map keyed in the
        # same way as the matrices-metadata argument
        resolver = ctgen.common.SymbolicCoefficientsResolver(self.backendSpecifics)
        resolved = {}
        for name, meta in matricesMetadata.items():
            res = resolver.resolveSymbols(meta)
            resolved[name] = res

        ok, codeOrError = self.luaGenerator.generate(
            self.backendSpecifics,
            ctModelMetadata,
            matricesMetadata, resolved)

        return ok, codeOrError


    def generate(self, ctModelMetadata, allMatricesMetadata):
        ok, text = self.generate_code(ctModelMetadata, allMatricesMetadata)
        print(text)
        # TODO create the file
