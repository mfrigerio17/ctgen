local common = common

local source_template = [[
@if not template_all then
#include <«ids.include_path»/«files.header»>

using «ids.ns.qualifier»::«ids.locals.scalar_t»;
@end

${constants_code.definitions()}


@for i, tf in ipairs(transforms) do
${transform_class_methods(tf)}

@end


@if ctrl.container_class.generate_it then
${container_class_methods}
@end


]]


local transform_class_methods_template = [[
@local META  = ids.transform_class
@local CLASS = META.class_name(tfMetadata)
@local fqn
@local heading = ''
@if template_all then
    @heading = tpl.heading
    @fqn = ids.ns.qualifier .. '::' .. tpl.container.in_qualifier .. '::' .. CLASS
@else
    @fqn = ids.ns.qualifier .. '::' .. CLASS
@end
«heading»
«fqn»::«CLASS»(«ctor_args»)
@if tfMetadata.parametric then
    : «META.members.parameters»(params)
@end
{
@local ctdata = ids.inherited.members.ct
@local access = 'this->'..ctdata.name
@for statement in python.iter(statementsGenerator.constantCoefficientsAssignments(access)) do
    «statement»
@end
}

«heading»
const typename «fqn»& «fqn»::«META.members.update»(const «ids.locals.variables_status_t»& «ids.locals.formalParams.varsStatus»)
{
@for var, expressions in pairs(variables) do
@   for k, expr in pairs(expressions) do
@       local codearg = expr.toCode( ctrl.variables.value_expression(var) )
@       if expr.isRotation() then
    «ids.locals.scalar_t» «ids.locals.sinVarName(expr)» = «ids.locals.scalar_traits»::sin( «codearg» );
    «ids.locals.scalar_t» «ids.locals.cosVarName(expr)» = «ids.locals.scalar_traits»::cos( «codearg» );
@       end
@   end
@end

@for statement in python.iter(statementsGenerator.variableCoefficientsAssignments(access) ) do
    «statement»
@end
    return *this;
}
]]


local function constructor_initializer_list(transforms, ids)
  local text = {}
  for i, tf in ipairs(transforms) do
    local args = ""
    if tf.parametric then
      args = ids.container_class.members.parameters
    end
    table.insert(text, ids.container_class.members.transform(tf) .. "(" .. args .. ")")
  end
  return table.concat(text, ",")
end


local function container_class_methods(env)
    local template = [[
«heading»
«qualifier»::«class»::«class»() :
«ctor_init_list»
{}

«heading»
void «qualifier»::«class»::«meta.members.update»(const «ids.locals.variables_status_t»& «ids.locals.formalParams.varsStatus»)
{
@for i, tf in ipairs(transforms) do
    «meta.members.transform(tf)».«ids.transform_class.members.update»(«ids.locals.formalParams.varsStatus»);
@end
}
]]
    local meta = env.ids.container_class
    local localenv = {
        ctor_init_list = constructor_initializer_list(env.transforms, env.ids),
        class     = meta.class_name,
        meta      = meta,
        qualifier = env.ids.ns.qualifier,
        heading   = '',
        ids = env.ids,
        transforms = env.transforms,
        python = python
    }
    if env.template_all then
        localenv.qualifier = env.ids.ns.qualifier .. '::' .. env.tpl.container.in_qualifier
        localenv.heading = env.tpl.heading
    end
    return common.tpleval(template, localenv, {returnTable=true})

end


local function source_file_code(env, statements_generator, matrices_metadata, transform_class_ctor_arguments)

    -- Generator of the implementation of the methods of a transform class
    -- For nested evaluation within a template
    local function transform_class_methods(tfMetadata)
        env.ctor_args  = transform_class_ctor_arguments(tfMetadata)
        env.tfMetadata = tfMetadata
        env.statementsGenerator = statements_generator.getMatrixSpecificGenerators(matrices_metadata[tfMetadata.name])
        env.variables = common.python_dictOfSets_to_table(tfMetadata.vars)
        return common.tpleval_failonerror(transform_class_methods_template, env, {returnTable=true})
    end

    local ok, code = container_class_methods(env)
    if not ok then  return ok, code  end
    env.container_class_methods = code
    env.transform_class_methods = transform_class_methods

    return common.tpleval(source_template, env)
  end



source_file_generator = source_file_code


