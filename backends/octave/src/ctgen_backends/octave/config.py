import os
from kgprim.ct.repr.mxrepr import MatrixRepresentation
import ctgen_backends.octave.generator as generator

lua_config_file = os.path.join( os.path.dirname(__file__), "config.lua")
luaCodeSrc = open( lua_config_file, "r")
defaultTextGeneratorsConfiguration = generator.lua.execute(luaCodeSrc.read())
luaCodeSrc.close()

strbit = {
    MatrixRepresentation.homogeneous : 'xh',
    MatrixRepresentation.spatial_motion : 'xm',
    MatrixRepresentation.spatial_force : 'xf',
    MatrixRepresentation.pure_rotation : 'rot'
}


class Configurator:
    def __init__(self, ctModel, outer_config, cmdline_overrides):
        self.ctModel = ctModel
        self.textgen_cfg = defaultTextGeneratorsConfiguration
        self.outdir = outer_config['outDir'] or '_gen/octave'

        user_config = outer_config['textConfig']
        if user_config is not None :
            try :
                istream  = open(user_config, 'r')
                user_config = generator.lua.execute(istream.read())
                istream.close()
                f = generator.lua.execute('return common.table_override')
                f(self.textgen_cfg, user_config)
            except OSError as exc :
                generator.logger.warning("Could not read configuration file '{0}': {1}".format(user_config, exc.strerror))


    def getOutputDirectory(self):
        return self.outdir

    def getTextGeneratorsConfiguration(self):
        return self.textgen_cfg

    def getClassName(self, matrixMetadata):
        # we just relay what the Lua config says
        return self.textgen_cfg.mx_class_name(matrixMetadata)


