import pathlib
from kgprim.ct.repr.mxrepr import MatrixRepresentation
import ctgen_backends.octave as thisBackend
import ctgen_backends.octave.generator as generator


class Configurator:
    def __init__(self, ctModel, outer_config, cmdline_overrides):
        self.ctModel = ctModel

        with open(pathlib.Path(__file__).parent.joinpath("config.lua"), "r") as cfgFile:
            self.textgen_cfg = thisBackend.luaRuntime.execute(cfgFile.read())

        self.outdir = outer_config['outDir'] or '_gen/octave'

        user_config = outer_config['textConfig']
        if user_config is not None :
            try :
                istream  = open(user_config, 'r')
                user_config = thisBackend.luaRuntime.execute(istream.read())
                istream.close()
                f = thisBackend.luaRuntime.execute('return common.table_override')
                f(self.textgen_cfg, user_config)
            except OSError as exc :
                generator.logger.warning("Could not read configuration file '{0}': {1}".format(user_config, exc.strerror))


    def getOutputDirectory(self):
        return self.outdir

    def getTextGeneratorsConfiguration(self):
        return self.textgen_cfg

    def getClassName(self, matrixMetadata):
        # we just rely on what the Lua config says
        return self.textgen_cfg.mx_class_name(matrixMetadata)


