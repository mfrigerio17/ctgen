backend_name = 'C++ iit-rbd'
backend_tag  = 'cpp_iitrbd'
backend_description = '''C++ generator, using the compact transform type defined
in the iit-rbd library. Use the language tag '{0}' '''.format(backend_tag)


def add_cmdline_arguments(args):
    # I want given flags to result in a True field, but non-given flags must
    # result in None fields (not False!).
    # Otherwise I cannot distinguish when the user does not pass anything.
    # This is relevant because in CtGen, command line options override the
    # defaults in the config file.

    args.add_argument('--template', dest='template',
                      action='store_const', const=True, default=None,
                      help='force generation of code templated on the scalar type')

def get_generator(ctModel, path_config_override, cmdline_args):
    import ctgen_backends.cpp_iitrbd as cpp
    import ctgen_backends.cpp_iitrbd.generator
    import ctgen_backends.cpp_iitrbd.config

    config = cpp.config.Configurator(ctModel, path_config_override, cmdline_args)
    return cpp.generator.Generator(config)
