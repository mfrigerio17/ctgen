This is the Coordinate-Transform code-generation tool (`ctgen`).

`ctgen` is a command line program that generates source code implementing a
user-defined set of coordinate transformation matrices.

The language of the generated source code depends on the selected "backend".
At the moment Octave and C++ are supported.

The purpose of this tool is to spare the user from boring and error prone
development. The main input of `ctgen` is a simple specification of the
relative poses between some frames, which describe the user's problem.
[`This file`](sample/model.motdsl) is a documented sample input.

The output is source code which implements some transforms between the same
frames, i.e., code that defines the right matrices with the right coefficients.
More specific features of the generated code depend on the selected backend.

# Installation
```sh
pip install ctgen
```

Alternatively, from a clone of the source tree:

```sh
git clone <this repo> ctgen
cd ctgen/
pip install .
```

## Requirements

Python >= 3.9 **and** Lua >= 5.2.

Lua and Lua packages must be installed manually (i.e. they are not
handled by `pip`). I suggest to follow the docs of
[Luarocks](https://luarocks.org/) (the Lua package manager), to make
sure to install matching versions of Lua and Luarocks itself.

Then install my [template engine](https://github.com/mfrigerio17/lua-template-engine),
which I use for code generation:

```
luarocks install template-text
```

## Sample installation sequence
Using a Python3 virtual environment:

```sh
# Virtual environment
mkdir myvenv && python3 -m venv myvenv/
source myvenv/bin/activate
#pip install wheel    # may also be needed to prepare the environment

# The actual program
git clone <this repo> ctgen
cd ctgen/
pip install .   # will also fetch other dependencies

# Lua dependencies
# install Lua and Luarocks ... then
luarocks install template-text
```

## Docker

There is a sample [Dockerfile](etc/Dockerfile) to build a minimal image with
Python, Lua, and the template engine. In a corresponding container you will be
able to install CtGen with pip and launch it right away.

# Usage
```
ctgen <input file>
```
Refer to the command line help `ctgen --help` for the options.

See [`sample/basic/model.motdsl`](sample/basic/model.motdsl) for the input file
format (a "MotionsDSL" model).

See [`sample/basic/config.yaml`](sample/basic/config.yaml) for the configuration
file format.
The configuration file is optional. Most of the options can be specified on the
command line as well. Command line options override matching entries in the
configuration file.


## Examples
Use the given sample model and all the defaults:
```
ctgen sample/basic/model.motdsl
```

Use the C++ backend shipped with the tool:
```
ctgen -l cpp_iitrbd sample/basic/model.motdsl
```

Use the sample configuration file:
```
ctgen -c sample/config.yaml sample/basic/model.motdsl
```

Use explicit command line switches to set the language backend, the output
folder, and to request the homogeneous coordinates representation only:
```
ctgen --lang octave --output /tmp/ctgen/octave -xH sample/basic/model.motdsl
```


## Generated code
See the readme file of the chosen backend, in the `backends/` folder.


# Testing
There are no specific unit tests for `ctgen` itself.

On the other hand, testing the generated code can essentially be done only by
comparison with ground truth numerical data.

To facilitate this task, `ctgen`
can generate numerical datasets with the coefficients of the same matrices it
can generate code for (see the command line help). These datasets can then be
used by backend-specific testing code, if available.

The C++ and Octave backends shipped with `ctgen` do provide such
testing code, check their readme for further details.

## Numerical datasets
`ctgen` generates one binary dataset per matrix, with a variable number
of entries, depending on the command line argument.
E.g.:

```
ctgen --output /tmp/ctgen -s 100 sample/basic/model.motdsl
```

The format of the dataset is documented in the `dataset.py` module.


# License
© 2020 Marco Frigerio

Distributed under the BSD 3-clause license. See the `LICENSE` file for more
details.
