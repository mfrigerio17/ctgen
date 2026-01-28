import pathlib
import sympy.printing
import lupa
import ctgen_backends.cpp_iitrbd as thisBackend

from ctgen.pyutils import open_utf8_reading

class Configurator:
    '''
    Configurator object for the code generator of this package.
    '''

    def __init__(self, ctModel, path_config_override=None, cmdline_overrides=None,
                           lua_runtime = lupa.LuaRuntime(unpack_returned_tuples=True) ):
        '''
        Arguments:
        - `ctModel`: the current model given as input to `ctgen`
        - `path_config_override`: path to the lua configuration file meant to
          override (some of) the values of the default configuration of this
          backend. Optional.
        - `cmdline_overrides`: command line switches (the object returned by
          `argparser.parse_args()`). Optional.
        - `lua_runtime`: the instance of `lupa.LuaRuntime` which will be used
          to load and execute the Lua modules of this backend.
          It MUST have been created with the option `unpack_returned_tuples=True`.
          Optional.
        '''
        self.ctModel = ctModel
        self.lua = lua_runtime

        with open_utf8_reading(pathlib.Path(__file__).parent.joinpath("configuration.lua")) as cfgFile:
            self.textgen_cfg = self.lua.execute(cfgFile.read())
            # Keep in mind this is NOT a python dictionary, but a Lua table
            # get(..) will not work, but querying for missing keys does not
            # error an yields nil (None)

        if path_config_override is not None :
            try :
                istream  = open_utf8_reading(path_config_override)
                user_config = self.lua.execute(istream.read())
                istream.close()
                f = self.lua.execute('return ctgen__common.table_override')
                f(self.textgen_cfg, user_config)
            except OSError as exc :
                core.logger.warning("Could not read configuration file '{0}': {1}".format(path_config_override, exc.strerror))

        # Check for command-line overrides.
        # We assume that the command line optional flags are None when
        # not given by the user, and True otherwise; never False.

        templates = self.textgen_cfg['tpl']['template_all'] or False
        constexpr = self.textgen_cfg['constants']['use_constexpr'] # I want it to default to true, but cannot use 'or True' !!!
        if constexpr is None: constexpr = True  # defaults to True if missing in the dictionary

        NOconstexpr = not constexpr
        if cmdline_overrides is not None :
            templates   = cmdline_overrides.template or templates
            NOconstexpr = cmdline_overrides.noconstexpr or NOconstexpr

        # Reset the config values, to make sure a value is there (possibly the
        # command-line flag)
        self.textgen_cfg['tpl']['template_all'] = templates
        self.textgen_cfg['constants']['use_constexpr'] = (not NOconstexpr)

        # Add to the Lua configuration the function to stringify Sympy
        # expressions
        self.textgen_cfg['sympy_to_text'] = sympy.printing.cxxcode

    @property
    def LuaRuntime(self):
        return self.lua

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


