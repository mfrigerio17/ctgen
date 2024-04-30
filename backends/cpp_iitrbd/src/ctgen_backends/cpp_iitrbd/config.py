import pathlib
import sympy.printing
import ctgen_backends.cpp_iitrbd as thisBackend


class Configurator:
    '''
    Configurator object for the code generator of this package.
    '''

    def __init__(self, ctModel, outer_config=None, cmdline_overrides=None):
        '''
        Arguments:
        - `ctModel`: the current model given as input to `ctgen`
        - `outer_config`: configuration dictionary coming from the main module
        - `cmdline_overrides`: command line switches (the object returned by
        `argparser.parse_args()`)
        '''
        self.ctModel = ctModel

        with open(pathlib.Path(__file__).parent.joinpath("configuration.lua"), "r") as cfgFile:
            self.textgen_cfg = thisBackend.luaRuntime.execute(cfgFile.read())

        if outer_config is not None :
            self.outdir = outer_config['outDir'] if 'outDir' in outer_config else  '_gen'
            if 'textConfig' in outer_config :
                user_config = outer_config['textConfig']
                if user_config is not None :
                    try :
                        istream  = open(user_config, 'r')
                        user_config = thisBackend.luaRuntime.execute(istream.read())
                        istream.close()
                        f = thisBackend.luaRuntime.execute('return ctgen__common.table_override')
                        f(self.textgen_cfg, user_config)
                    except OSError as exc :
                        core.logger.warning("Could not read configuration file '{0}': {1}".format(user_config, exc.strerror))

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

    def getOutputDirectory(self):
        '''
        The root folder where to place generated code
        '''
        return self.outdir

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


