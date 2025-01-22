'''
This the python package of the "cpp_iitrbd" backend for the CtGen tool
'''

import pathlib
import lupa

import ctgen.common
from ctgen.pyutils import open_utf8_reading

luaRuntime = lupa.LuaRuntime(unpack_returned_tuples=True)

pathToCommon = pathlib.Path(ctgen.common.__file__).parent
with open_utf8_reading(pathToCommon.joinpath("common.lua")) as luasource:
    luaRuntime.execute(luasource.read())
with open_utf8_reading(pathToCommon.joinpath("assignments.lua")) as luasource:
    luaRuntime.execute(luasource.read())
