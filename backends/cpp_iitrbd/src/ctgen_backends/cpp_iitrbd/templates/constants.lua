local common = ctgen__common

local template_containers = [[
@if ctrl.constants.generate_local_defs then
/**
 * The numerical constants as they appear in the source model
 */
struct «ctrl.constants.local_defs_container_name»
{
@   for i, constant in ipairs(constants) do
    «model_constant_declaration(ids.model_property_to_varname(constant), constant.value)»
@   end
};
@end

/**
 * Derived constant expressions
 */
struct «ids.locals.constants_container»
{
    $<derived_constants>
};]]


local template_definitions = [[
@if ctrl.constants.generate_local_defs then
@   ccontainer = ctrl.constants.local_defs_container_name -- dont use local, need to affect the env
@   for _, constant in ipairs(constants) do
«model_constant_definition(ids.model_property_to_varname(constant), constant.value)»
@   end
@end

@ccontainer = ids.locals.constants_container
$<derived_constants>]]


local template_derived_constants_generic = [[
@for _, constant in ipairs(constants) do
@   for _, expression in ipairs(const_expressions[constant]) do
@       local arg   = expression.toCode( code_for_constant_reference(expression.expression.arg) )
@       if expression.isRotation() then
@           local value = ids.locals.scalar_traits .. '::sin(' .. arg ..')'
«declare_or_define(ids.locals.sinVarName(expression), value)»
@           value = ids.locals.scalar_traits .. '::cos(' .. arg ..')'
«declare_or_define(ids.locals.cosVarName(expression), value)»
@       elseif not expression.isIdentity() then
«declare_or_define(ids.locals.varName(expression), arg)»
@       end
@   end
@end]]


local function constants_generators(given_env)

    -- shallow copy the evaluation environment, and adds required entries
    local env = {}
    for k,v in pairs(given_env) do
        env[k] = v
    end

    -- The sub-templates for the declaration/definition of a constant
    local declaration = 'static constexpr «ids.locals.scalar_t» «identifier»{«value»};'
    local definition  = ''
    if not env.ctrl.constants.use_constexpr then
        declaration = 'static const «ids.locals.scalar_t» «identifier»;'
        if env.template_all then
            definition = '«tpl.heading» const «ids.locals.scalar_t» «ids.ns.qualifier»::«tpl.container.in_qualifier»::«ccontainer»::«identifier»{«value»};'
        else
            definition = 'const «ids.locals.scalar_t» «ids.ns.qualifier»::«ccontainer»::«identifier»{«value»};'
        end
    end
    -- Pre-load them, so we can evaluate them multiple times
    local declaration_template_loaded = common.template_load(declaration, env)
    local definition_template_loaded  = common.template_load(definition , env)

    local model_constant_declaration = function(identifier, value)
        return common.template_evaluate(declaration_template_loaded, {},
                    {identifier = identifier,
                     value      = value} )
        end
    local model_constant_definition = function(identifier, value)
        return common.template_evaluate(definition_template_loaded, {},
                    {identifier = identifier,
                     value      = value} )
        end

    -- internal, default policy
    local code_for_constant_reference = function(constant)
        return env.ctrl.constants.local_defs_container_name ..'::'.. env.ids.model_property_to_varname(constant)
    end
    if not env.ctrl.constants.generate_local_defs then
        -- user-supplied policy
        code_for_constant_reference = env.ctrl.constants.value_expression
    end

    env.model_constant_declaration  = model_constant_declaration
    env.model_constant_definition   = model_constant_definition
    env.code_for_constant_reference = code_for_constant_reference

    local options  = {returnTable=true}
    local included = {derived_constants=template_derived_constants_generic}

    local function containers()
        env.declare_or_define = model_constant_declaration
        return common.tpleval_failonerror(template_containers, env, options, included)
    end
    local function definitions()
        env.declare_or_define = model_constant_definition
        return common.tpleval_failonerror(template_definitions, env, options, included)
    end

    return {
        containers = containers,
        definitions= definitions,
    }
end


ctgen__cpp_constants_generators = constants_generators
