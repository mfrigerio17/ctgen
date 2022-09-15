#!/usr/bin/env python3

# This script allows to run the tool without installing it. Just execute it
# from the current directory. Note that you will still need to install the tool
# dependencies though.

import sys, os

if __name__ == '__main__':
    basedir = os.path.dirname(__file__)
    path_backends = os.path.join(basedir, '../backends/cpp_iitrbd/src/')
    sys.path.append(path_backends)
    path_backends = os.path.join(basedir, '../backends/octave/src/')
    sys.path.append(path_backends)
    import ctgen.gen
    ctgen.gen.main()