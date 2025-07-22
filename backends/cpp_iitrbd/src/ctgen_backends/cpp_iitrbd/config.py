import pathlib
import sympy.printing
import ctgen_backends.cpp_iitrbd as thisBackend

from ctgen.pyutils import open_utf8_reading

class Configurator:
    '''
    Configurator object for the code generator of this package.
    '''

    def __init__(self, ctModel, path_config_override=None, cmdline_overrides=None):
        '''
        Arguments:
        - `ctModel`: the current model given as input to `ctgen`
        - `outer_config`: configuration dictionary coming from the main module
        - `cmdline_overrides`: command line switches (the object returned by
        `argparser.parse_args()`)
        '''
        self.ctModel = ctModel

        with open_utf8_reading(pathlib.Path(__file__).parent.joinpath("configuration.lua")) as cfgFile:
            self.textgen_cfg = thisBackend.luaRuntime.execute(cfgFile.read())

        if path_config_override is not None :
            try :
                istream  = open_utf8_reading(path_config_override)
                user_config = thisBackend.luaRuntime.execute(istream.read())
                istream.close()
                f = thisBackend.luaRuntime.execute('return ctgen__common.table_override')
                f(self.textgen_cfg, user_config)
            except OSError as exc :
                core.logger.warning("Could not read configuration file '{0}': {1}".format(path_config_override, exc.strerror))

        # The option for C++ templates generation
        templates = self.textgen_cfg['tpl']['template_all'] or False
        if cmdline_overrides is not None :
            templates = cmdline_overrides.template or templates
        # Reset the config value, to make sure a value is there (and to consider
        # the command-line override, if any)
        self.textgen_cfg['tpl']['template_all'] = templates

        # Add to the Lua configuration the function to stringify Sympy
        # expressions
        self.textgen_cfg['sympy_to_text'] = sympy.printing.cxxcode


    def getOutputFileNames(self):
        #if self.generateTemplates() :
        #    impl = impl + '.h'
        return self.textgen_cfg.files

    def getHeadersPath(self):
        path = pathlib.Path(self.textgen_cfg.files.include_basedir)
        dirs = self.textgen_cfg.files.include_dirs(self.ctModel)
        for i in dirs :
            path = path.joinpath(dirs[i]) # need the stupid i because it is a Lua table (dont know how to iterate over the values)
        return path

    def getTextGeneratorsConfiguration(self):
        return self.textgen_cfg

    def generateTemplates(self):
        return self.textgen_cfg['tpl']['template_all']


