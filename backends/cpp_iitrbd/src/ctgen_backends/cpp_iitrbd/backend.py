backend_name = 'C++ iit-rbd'
backend_tag  = 'cpp_iitrbd'
backend_description = '''C++ generator, using the compact transform type defined
in the iit-rbd library. Use the language tag '{0}' '''.format(backend_tag)


def add_cmdline_arguments(args):
    args.add_argument('--template', dest='template', action='store_true',
                      help='template the generated code on the scalar type')

def get_generator(ctModel, path_config_override, cmdline_args):
    import ctgen_backends.cpp_iitrbd as cpp
    import ctgen_backends.cpp_iitrbd.generator
    import ctgen_backends.cpp_iitrbd.config

    config = cpp.config.Configurator(ctModel, path_config_override, cmdline_args)
    return cpp.generator.Generator(config)
