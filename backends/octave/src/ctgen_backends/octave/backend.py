backend_name = 'Octave'
backend_tag  = 'octave'
backend_description = '''Octave generator, using Octave classes.
Select with the language tag '{0}' '''.format(backend_tag)


def add_cmdline_arguments(args):
    pass

def get_generator(ctModel, outer_config, cmdline_args):
    import ctgen_backends.octave as octave
    import ctgen_backends.octave.generator
    import ctgen_backends.octave.config

    config = octave.config.Configurator(ctModel, outer_config, cmdline_args)
    return octave.generator.Generator(config)