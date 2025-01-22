'''
The main module of the Plaintext backend.

Any CtGen backend implementation must have the "backend.py" module, like
this one.

The module shall define the strings `backend_name` `backend_tag` and
`backend_description`, which are sort of metadata.

The module shall also define at least two functions, documented below.
'''

backend_name = 'Plaintext'
backend_tag  = 'plaintext'
backend_description = '''Plaintext generator for debugging/reference.
Select with the language tag '{0}' '''.format(backend_tag)


def add_cmdline_arguments(args):
    '''
    Possibly add command line arguments specific to the backend.
    Arguments:
      - `args` an "arguments group" from the `argparse` standard library
    '''
    pass

def get_generator(ct_model, path_config_override, cmdline_args):
    '''
    Return the code generator of this plugin.
    This is the "entry point" of the backend, and it is invoked by the
    main of CtGen.
    Arguments:
      - `ct_model`: the coordinate transforms model container
        (`kgprim.ct.models.CTransformsModel`) for the current run of the
        tool
      - `path_config_override`: optional path to a Lua configuration file,
        which will override matching entries of the default configuration of
        the backend. This argument corresponds to the "backend-config" option
        of CtGen
      - `cmdline_args`: the original command line switches given to the
        main (the object returned by `argparser.parse_args()`)

    The configuration and the command line switches are passed here for
    the backend to honour the user's request (e.g. the output directory)
    as well as to give the backend the chance of creating its own
    configuration.
    '''

    import ctgen_backends.plaintext.generator as here

    return here.Generator()
