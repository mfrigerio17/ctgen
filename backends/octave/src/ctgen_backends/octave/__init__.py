'''
This the package of the "Octave" backend for the CtGen tool
'''

import pathlib
import lupa
import ctgen.common

luaRuntime = lupa.LuaRuntime(unpack_returned_tuples=True)

pathToCommon = pathlib.Path(ctgen.common.__file__).parent
with open(pathToCommon.joinpath("common.lua")) as luasource:
    luaRuntime.execute(luasource.read())
with open(pathToCommon.joinpath("assignments.lua")) as luasource:
    luaRuntime.execute(luasource.read())
