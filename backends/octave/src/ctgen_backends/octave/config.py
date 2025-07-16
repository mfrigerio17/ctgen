import pathlib
from kgprim.ct.repr.mxrepr import MatrixRepresentation
import ctgen_backends.octave as thisBackend
import ctgen_backends.octave.generator as generator

from ctgen.pyutils import open_utf8_reading

class Configurator:
    def __init__(self, ct_model, path_config_override, cmdline_overrides):
        self.ctModel = ct_model

        with open_utf8_reading(pathlib.Path(__file__).parent.joinpath("config.lua")) as cfgFile:
            self.textgen_cfg = thisBackend.luaRuntime.execute(cfgFile.read())

        if path_config_override is not None :
            try :
                istream  = open_utf8_reading(path_config_override)
                path_config_override = thisBackend.luaRuntime.execute(istream.read())
                istream.close()
                f = thisBackend.luaRuntime.execute('return common.table_override')
                f(self.textgen_cfg, path_config_override)
            except OSError as exc :
                generator.logger.warning("Could not read configuration file '{0}': {1}".format(path_config_override, exc.strerror))

    def getTextGeneratorsConfiguration(self):
        return self.textgen_cfg

    def getClassName(self, matrixMetadata):
        # we just rely on what the Lua config says
        return self.textgen_cfg.meta.tf_class.class_name(matrixMetadata)


