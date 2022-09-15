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


common = {
    tpleval = tpleval,
    tpleval_failonerror = tpleval_failonerror,
    decorated_names_iterator = decorated_names_iterator,
    lineDecorator = tplmodule.lineDecorator,
    python_dictOfSets_to_table = python_dictOfSets_to_table,
    myiter = myiter,
    table_override = table_override,
    pylen = pylen,
}
