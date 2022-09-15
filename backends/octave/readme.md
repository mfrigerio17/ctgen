This is an Octave backend for the `ctgen` tool.
Use the switch `--lang octave` to use it.

This document describes briefly the features of the generated Octave code.

# Overview
This backend uses Octave classes. A class is generated for each desired
transform in the input model.

Each class(transform) is independent of the others, they do not share common
values for the parameters nor for the variables.

See the sample script [`usage.m`](sample/usage.m) for more information about the
interface of the generated classes.

# Dependencies
None. The generated Octave code is standalone.

# Testing
Generate both the Octave code and the test datasets (see the main readme).
They have to be in the same folder. Move to that folder and launch Octave; then:

```octave
addpath('<ctgen root folder>/backends/octave/test/');
tests
```

# License
Copyright 2020-2022, Marco Frigerio

Distributed under the BSD 3-clause license. See the `LICENSE` file for more
details.

