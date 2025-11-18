import pathlib
import ctgen_backends.octave
from ctgen.pyutils import open_utf8_reading

backend_name = 'Octave'
backend_tag  = 'octave'
backend_description = '''Octave generator, using Octave classes.
Select with the language tag '{0}' '''.format(backend_tag)


def add_cmdline_arguments(args):
    pass

def get_codegen_configuration(path_config_override=None):
    '''
    Return the Lua table with the configuration used by the code generators of
    this backend.

    The configuration is read from `config.lua` in this package. If the path to
    another Lua file is given to this function, such file will be read to
    override matching entries in the default configuration.
    '''
    #By default, the Lua runtime managed by this package is used to load the
    #configuration, unless another runtime is passed to this function. This can
    #be useful when using this package as an API from another application,
    #since Lua tables from different runtimes cannot be used together.
    # TODO: cant really take another runtime, at the moment, because it will not
    # have the table_override function

    lua = ctgen_backends.octave.luaRuntime
    with open_utf8_reading(pathlib.Path(__file__).parent.joinpath("config.lua")) as cfgFile:
        lua_config = lua.execute(cfgFile.read())
        if path_config_override is not None :
            with open_utf8_reading(path_config_override) as cfgFile:
                lua_config_override = lua.execute(cfgFile.read())
                f = lua.eval('common.table_override')
                f(lua_config, lua_config_override)
    return lua_config

def get_generator(ctModel, path_config_override, cmdline_args):
    import ctgen_backends.octave.generator

    lua_config = get_codegen_configuration(path_config_override)
    return ctgen_backends.octave.generator.Generator(lua_config)
