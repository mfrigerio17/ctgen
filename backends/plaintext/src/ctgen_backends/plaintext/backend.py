backend_name = 'Plaintext'
backend_tag  = 'plaintext'
backend_description = '''Plaintext generator for debugging/reference.
Select with the language tag '{0}' '''.format(backend_tag)


def add_cmdline_arguments(args):
    pass

def get_generator(ctModel, outer_config, cmdline_args):
    '''
    Return the code generator of this plugin.
    This is the "entry point" of this package/plugin, and it is invoked by the
    main of CtGen.
    '''

    import ctgen_backends.plaintext.generator as here

    return here.Generator()
