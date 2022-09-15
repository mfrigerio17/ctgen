local common = common





local function ns_utils(ns_names)
  local nsopen  = function(name) return 'namespace ' .. name .. ' {' end
  local nsclose = function(name) return '}' end
  return {
    open  = common.decorated_names_iterator(ns_names, nsopen),
    close = common.decorated_names_iterator(ns_names, nsclose),
    qualifier = table.concat(ns_names, '::')
  }
end



local function scalar_tpl_utils(scalar_t, container)
    return {
        heading  = 'template<typename ' .. scalar_t .. '>',
        scalar_t = scalar_t,
        container= {
            name = container,
            in_qualifier = container .. '<'..scalar_t..'>'
        },
        suffix = '<'..scalar_t..'>'
    }
end

--- The configuration table with most of the identifiers used in the generated code.
-- @param ctModelMetadata the object with the coordinate-transforms model and
--                        the related metadata.
-- @param config the user configuration for the text-generation; this must be a
--               table like the one in config_table.lua
local function ids(ctModelMetadata, config)
    local const = 'const'
    if config.constants.use_constexpr then
        const = 'constexpr'
    end
    local ret = {

    model_property_to_varname = config.model_property_to_varname,

    include_path = table.concat( config.files.include_dirs(ctModelMetadata), '/' ),

    locals = {
      variables_status_t = config.internal.variables_status_t,
      scalar_t     = config.internal.scalar_t,
      scalar_traits= config.internal.scalar_traits,
      varName      = config.internal.cached_value_identifier,
      sinVarName   = config.internal.cached_sinvalue_identifier,
      cosVarName   = config.internal.cached_cosvalue_identifier,
      constants_container = config.internal.constants_container,
      formalParams = {
        varsStatus = config.variables.status_formal_parameter,
        parsStatus = config.parameters.status_formal_parameter
      }
    },

    types   = {
        const_var_modifier = const,
        variables_status = config.variables.status_type,
        parameters_status= config.parameters.status_type,
        scalar_traits    = config.scalar_traits.type_name
    },

    container_class = config.container_class,
    transform_class = config.transform_class,

    class_names = {
      tf_base    = config.internal.transform_base_class,
      internal_parameters = config.parameters.internal_type
    },

    inherited = {
      members = {
        ct = config.external.iit_rbd.inherited_members.ct
      }
    },

    external = {
      transform_base_class = config.external.iit_rbd.base_class,
      ns = ns_utils(config.external.iit_rbd.namespaces),
      default_scalar_traits_instantiation = config.external.iit_rbd.double_traits,
      scalar_traits = config.external.iit_rbd.scalar_traits,
      scalar_t = config.external.iit_rbd.scalar_type_name,
    },

    ns = ns_utils(config.namespaces(ctModelMetadata)),
  }

    ret.container_class.class_name = config.container_class.class_name(ctModelMetadata)

    return ret
end


local function constants_stuff(env)
    local decl = ''
    local def  = ''
    if env.ctrl.constants.use_constexpr then
        decl = 'static constexpr «scalar» «name»{«value»};'
        def  = '«tpl»constexpr «scalar» «ns»::«container»::«name»;'
    else
        decl = 'static const «scalar» «name»;'
        def  = '«tpl»const «scalar» «ns»::«container»::«name»{«value»};'
    end
    local tpl= ''
    local ns = env.ids.ns.qualifier
    if env.template_all then
        ns  = ns .. '::' .. env.tpl.container.in_qualifier
        tpl = env.tpl.heading .. '\n'
    end

    local lenv = {
        scalar = env.ids.locals.scalar_t, ns= ns, tpl= tpl
    }
    local function code(whichtpl, name, value, container)
        lenv.name  = name
        lenv.value = value
        lenv.container = container or ''
        return common.tpleval_failonerror(whichtpl, lenv)
    end
    local function declare(name, value, container) return code(decl, name, value, container) end
    local function define (name, value, container) return code(def , name, value, container) end

    local function values(expr)
        local constant = expr.expression.arg
        local const_value_code_expr
        if env.ctrl.constants.generate_local_defs then
            -- my policy
            const_value_code_expr = env.ctrl.constants.local_defs_container_name
                .. '::' .. env.ids.model_property_to_varname(constant)
        else
            -- user specific
            const_value_code_expr = env.ctrl.constants.value_expression(constant)
        end
        local codearg = expr.toCode( const_value_code_expr )
        return {
            plain = codearg,
            sine  = env.ids.locals.scalar_traits .. '::sin(' .. codearg ..')',
            cosine= env.ids.locals.scalar_traits .. '::cos(' .. codearg ..')'
        }
    end

    local tpl_foreach_expr = [[
@local container = ids.locals.constants_container
@for constant, expressions in pairs(constants) do
@   for i, expr in pairs(expressions) do
@       local values = values(expr)
@       if expr.isRotation() then
«statement(ids.locals.sinVarName(expr), values.sine, container)»
«statement(ids.locals.cosVarName(expr), values.cosine, container)»
@       else
@           if not expr.isIdentity() then
«statement(ids.locals.varName(expr), values.plain, container)»
@           end
@       end
@   end
@end
]]
    local function foreach_expr(statement_gen)
        env.statement = statement_gen
        env.values    = values
        return common.tpleval_failonerror(tpl_foreach_expr, env, {returnTable=true})
    end

    local tpl_containers = [[
@if ctrl.constants.generate_local_defs then
struct «ctrl.constants.local_defs_container_name» {
@ for constant, _ in pairs(constants) do
    «declare(ids.model_property_to_varname(constant), constant.value)»
@ end
};
@end

struct «ids.locals.constants_container» {
    ${each_expr_declaration}
};

]]
    local tpl_definitions = [[
@local container = ctrl.constants.local_defs_container_name
@if ctrl.constants.generate_local_defs then
    @ for constant, _ in pairs(constants) do
«define(ids.model_property_to_varname(constant), constant.value, container)»
    @ end
@end

${each_expr_definition}
]]

    env.declare = declare
    env.define  = define

    local function containers()
        env.each_expr_declaration = foreach_expr(declare)
        return common.tpleval_failonerror(tpl_containers, env, {returnTable=true})
    end
    local function definitions()
        env.each_expr_definition = foreach_expr(define)
        return common.tpleval_failonerror(tpl_definitions, env, {returnTable=true})
    end
    return {
        containers = containers,
        definitions= definitions
    }
end


local function main_generator(env)
    local tpl=[[
#include <iostream>
#include <«ids.include_path»/«files.header»>

using namespace «ids.ns.qualifier»;

int main()
{
@if ctrl.container_class.generate_it then
    «ids.container_class.class_name» tf;
@end
    return 0;
}
]]
    return common.tpleval(tpl, env)
end


--- Returns the two functions generating the content of the header and source
-- files.
--
local function generators(ctModelMetadata, homCoordRepresentationMetadata, statementsGenerator, config)
  local ids = ids(ctModelMetadata, config)
  local transforms = {}
  for tf in python.iter(ctModelMetadata.transformsMetadata) do
    table.insert(transforms, tf)
  end
  local env = {
    python          = python,      -- global object from Lupa. Not clear what it contains besides 'iter()'
    common          = common,
    ids             = ids,         -- configuration for the identifiers in the generated code
    ctModelMetadata = ctModelMetadata, -- metadata for the whole model
    transforms      = transforms,      -- metadata for each coordinate-transform
    matrixMetadata  = homCoordRepresentationMetadata,      -- metadata for the matrix representation of the coordinate transforms
    ctrl            = {
        variables = config.variables,
        parameters= config.parameters,
        constants = config.constants,
        scalar_traits = config.scalar_traits,
        container_class = config.container_class,
    },
    parameters = common.python_dictOfSets_to_table(ctModelMetadata.parameters),
    constants  = common.python_dictOfSets_to_table(ctModelMetadata.constants),
    files = config.files,
    print = print,
    require = require,
  }

    env.template_all = config.tpl.template_all
    env.tpl = scalar_tpl_utils(ids.locals.scalar_t, config.tpl.dummy_container)

    local constants_code = constants_stuff(env)
    env.constants_code = constants_code

    local function transform_class_ctor_arguments(tf)
      if tf.parametric then
        return "const " .. ids.class_names.internal_parameters .. "& params"
      end
      return ""
    end

    return {
        headerFileCode = function()
            return header_file_generator(env, transform_class_ctor_arguments, config)
        end,
        sourceFileCode = function()
            return source_file_generator(env, statementsGenerator, homCoordRepresentationMetadata, transform_class_ctor_arguments)
        end,
        tests = tests_generator(env),
        cmake = function() return cmake_generator(env) end,
        main = function() return main_generator(env) end,
    }
end


return {
  generators = generators
}
