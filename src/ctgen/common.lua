local tplmodule = require('template-text')
local math = require('math')


--- Template evaluation function
-- Just a wrapper of the actual function in `template-text`, defaulting to
-- Xtend-style templates
local function tpleval(text, env, opts)
  local options = opts or {}
  options.xtendStyle = true
  options.verbose = true
  return tplmodule.template_eval(text, env, options)
end

local function tpleval_failonerror(tpl, env, opts)
    local ok, text = tpleval(tpl, env, opts)
    if not ok then error(text) end
    return text
end

--- Like `ipairs`, but `decorator` is applied to each string of the given list
local function decorated_names_iterator(names, decorator)
  return function()
    local iter, inv, ctrl = ipairs(names)
    return function()
      local i, name = iter(inv, ctrl)
      ctrl = i
      if name ~= nil then
        return i, decorator( name )
      end
    end, inv, ctrl
  end
end

local function python_dictOfSets_to_table( dict )
    local ret = {}
    for key in python.iter( dict ) do
        local set = {}
        for item in python.iter( dict[key] ) do
            table.insert(set, item)
        end
        ret[key] = set
    end
    return ret
end

--- Convert one container returned by `kgprim.ct.metadata.symbolicArgumentsOf()`
-- (from the Python package `kgprim`) into two tables.
-- The given container is expected to be a dictionary in which every value is
-- itself a container.
--
-- The first returned table is the array of all the keys of the given
-- dictionary.
-- The second table is keyed with such keys, and every value is the array
-- with the same items of the corresponding value of the given dictionary.
--
-- This conversion is done to preserve the iteration order of the dictionary
-- keys, AND of the items inside the dictionary values.
local function python_unique_expressions_dict_to_tables( dict )
    local symbols = {}
    local expressions_map = {}
    for symbol in python.iter( dict ) do
        table.insert(symbols, symbol) -- save the keys, ordered
        local expressions = {}
        for expression in python.iter( dict[symbol] ) do
            table.insert(expressions, expression)
        end
        expressions_map[symbol] = expressions
    end
    return symbols, expressions_map
end

--- A custom iterator over a python iterable
local function myiter( python_iterable )
    local it, inv, ctrl = python.iter( python_iterable )
    local i = 0
    return function()
      local item = it(inv, ctrl)
      ctrl = item
      if item ~= nil then
        i = i + 1
        return i, item
      end
      return nil
    end, inv, ctrl
end

--- Replace the values in `dest` with those from `src`, if they have the same
-- key. Works recursively for nested tables.
local function table_override(dest, src)
    for k,v in pairs(src) do
        if type(v) == 'table' then
            table_override(dest[k], v)
        else
            dest[k] = v
        end
    end
end

local function pylen(seq)
  return math.floor( python.builtins.len(seq) )
end

local function py_matrix_coeff(mx)
    local accessor = python.eval("lambda mx,r,c : mx[r,c]")
    return function(r,c)
        return accessor(mx, r, c)
    end
end

common = {
    tpleval = tpleval,
    tpleval_failonerror = tpleval_failonerror,
    decorated_names_iterator = decorated_names_iterator,
    lineDecorator = tplmodule.lineDecorator,
    python_dictOfSets_to_table = python_dictOfSets_to_table,
    python_unique_expressions_dict_to_tables = python_unique_expressions_dict_to_tables,
    myiter = myiter,
    table_override = table_override,
    pylen = pylen,
    py_matrix_coeff = py_matrix_coeff,
}

ctgen__common = common
