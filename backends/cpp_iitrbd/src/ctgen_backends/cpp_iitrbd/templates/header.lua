local common = common

local header_template = [[
@local ext_ns   = ids.external.ns.qualifier
@local scalar_t = ids.locals.scalar_t
#ifndef «include_guard»
#define «include_guard»

${include_directives}

${ids.ns.open}



@if template_all then
«tpl.heading»
struct «tpl.container.name» {

    @if ctrl.scalar_traits.use_default then
using «ids.locals.scalar_traits» = «ext_ns»::«ids.external.scalar_traits»«tpl.suffix»;
    @else
using «ids.locals.scalar_traits» = «ids.types.scalar_traits»«tpl.suffix»;
    @end
@else
    @if ctrl.scalar_traits.use_default then
using «ids.locals.scalar_traits» = «ext_ns»::«ids.external.default_scalar_traits_instantiation»;
    @end
using «scalar_t» = typename «ids.locals.scalar_traits»::Scalar;
@end


${constants_code.containers()}


@if ctrl.parameters.generate_local_status_type then
struct «ids.types.parameters_status»
{
@for param, _ in pairs(parameters) do
    «scalar_t» «ids.model_property_to_varname(param)»;
@end
};
@end


${parameters_struct_definition}

@if ctrl.variables.generate_local_status_type then
struct «ids.types.variables_status» {
@if template_all then
    using «ids.external.scalar_t» = «scalar_t»; // required by the matrix infrastructure
@else
    using «ids.external.scalar_t» = «ids.ns.qualifier»::«scalar_t»; // required by the matrix infrastructure
@end
@for var in python.iter(ctModelMetadata.variables) do
    «scalar_t» «ids.model_property_to_varname(var)»;
@end
};
@end

@local varstate_t = ids.locals.variables_status_t
using «varstate_t» = «ids.types.variables_status»;

template<typename ACTUAL>
struct «ids.class_names.tf_base» : public «ext_ns»::«ids.external.transform_base_class»<«varstate_t», ACTUAL>
{
    using Base = «ext_ns»::«ids.external.transform_base_class»<«varstate_t», ACTUAL>;
    «ids.class_names.tf_base»() : Base(0) {} // calls explicit constructor setting data to 0
};

@local cast_t
@cast_t = ids.inherited.members.ct.cast_type.motion(true)
using «cast_t» = «ext_ns»::«cast_t»< «scalar_t» >;
@cast_t = ids.inherited.members.ct.cast_type.motion(false)
using «cast_t» = «ext_ns»::«cast_t»< «scalar_t» >;
@cast_t = ids.inherited.members.ct.cast_type.force(true)
using «cast_t» = «ext_ns»::«cast_t»< «scalar_t» >;
@cast_t = ids.inherited.members.ct.cast_type.force(false)
using «cast_t» = «ext_ns»::«cast_t»< «scalar_t» >;
@cast_t = ids.inherited.members.ct.cast_type.homog(true)
using «cast_t» = «ext_ns»::«cast_t»< «scalar_t» >;
@cast_t = ids.inherited.members.ct.cast_type.homog(false)
using «cast_t» = «ext_ns»::«cast_t»< «scalar_t» >;


@for i, tf in ipairs(transforms) do
${transform_class_definition(tf)}

@end

@if ctrl.container_class.generate_it then
${container_class_definition}
@end

@if template_all then
};

    @if ctrl.parameters.generate_local_status_type then
«tpl.heading»
using «ids.types.parameters_status» = typename «tpl.container.in_qualifier»::«ids.types.parameters_status»;
    @end
    @if ctrl.variables.generate_local_status_type then
«tpl.heading»
using «ids.types.variables_status» = typename «tpl.container.in_qualifier»::«ids.types.variables_status»;
    @end
    @if ctrl.container_class.generate_it then
«tpl.heading»
using «ids.container_class.class_name» = typename «tpl.container.in_qualifier»::«ids.container_class.class_name»;
    @end
    @for i, tf in ipairs(transforms) do
«tpl.heading»
@local cname = ids.transform_class.class_name(tf)
using «cname» = typename «tpl.container.in_qualifier»::«cname»;
    @end
@end

${ids.ns.close}

@if template_all then
#include "«files.source».h"
@end

#endif
]]




local container_class_definition_template = [[
@local META = ids.container_class
struct «META.class_name»
{
    «META.class_name»();
@if ctModelMetadata.isParametric() then
    void «META.members.update_params»(const «ids.types.parameters_status»& mp) {
        «META.members.parameters» = mp;
    }
@end

    void «META.members.update»(const «ids.locals.variables_status_t»&);

@for i, tf in ipairs(transforms) do
    «ids.transform_class.class_name(tf)» «META.members.transform(tf)»;
@end

@if ctModelMetadata.isParametric() then
protected:
    «ids.class_names.internal_parameters» «META.members.parameters»;
@end
};
]]



local transform_class_definition_template = [[
@local META  = ids.transform_class
@local CLASS = META.class_name(tfMetadata)
struct «CLASS» : public «ids.class_names.tf_base»<«CLASS»>
{
    «CLASS»(«ctor_args»);
    const «CLASS»& «META.members.update»(const «ids.locals.variables_status_t»&);

@local cast_t, method
@cast_t = ids.inherited.members.ct.cast_type.motion(true)
@method = META.members.view_as.motion(tfMetadata,true)
    inline «cast_t» «method»() const {
        return this->template as<«cast_t»>();
    }
@cast_t = ids.inherited.members.ct.cast_type.motion(false)
@method = META.members.view_as.motion(tfMetadata,false)
    inline «cast_t» «method»() const {
        return this->template as<«cast_t»>();
    }
@cast_t = ids.inherited.members.ct.cast_type.force(true)
@method = META.members.view_as.force(tfMetadata,true)
    inline «cast_t» «method»() const {
        return this->template as<«cast_t»>();
    }
@cast_t = ids.inherited.members.ct.cast_type.force(false)
@method = META.members.view_as.force(tfMetadata,false)
    inline «cast_t» «method»() const {
        return this->template as<«cast_t»>();
    }
@cast_t = ids.inherited.members.ct.cast_type.homog(true)
@method = META.members.view_as.homog(tfMetadata,true)
    inline «cast_t» «method»() const {
        return this->template as<«cast_t»>();
    }
@cast_t = ids.inherited.members.ct.cast_type.homog(false)
@method = META.members.view_as.homog(tfMetadata,false)
    inline «cast_t» «method»() const {
        return this->template as<«cast_t»>();
    }

@if tfMetadata.parametric then
protected:
    const «ids.class_names.internal_parameters»& «META.members.parameters»;
@end
};
]]


local parameters_class_definition_template = [[
@local scalar_t = ids.locals.scalar_t
@local CLASS = ids.class_names.internal_parameters
struct «CLASS»
{
@for param, expressions in pairs(parameters) do
@   for i, expr in pairs(expressions) do
@       if expr.isRotation() then
    «scalar_t» «ids.locals.sinVarName(expr)»;
    «scalar_t» «ids.locals.cosVarName(expr)»;
@       else
    «scalar_t» «ids.locals.varName(expr)»;
@       end
@   end
@end

    «CLASS»() {}
    «CLASS»(const «ids.types.parameters_status»& «ids.locals.formalParams.parsStatus») {
        ${parametersAssignments}
    }

    «CLASS»& operator=(const «ids.types.parameters_status»& «ids.locals.formalParams.parsStatus») {
        ${parametersAssignments}
        return *this;
    }
};
]]

local parameters_assignments_template = [[
@for param, expressions in pairs(parameters) do
@   for i, expr in pairs(expressions) do
@       local codearg = expr.toCode( ctrl.parameters.value_expression(param) )
@       if expr.isRotation() then
«ids.locals.sinVarName(expr)» = «ids.locals.scalar_traits»::sin( «codearg» );
«ids.locals.cosVarName(expr)» = «ids.locals.scalar_traits»::cos( «codearg» );
@       else
«ids.locals.varName(expr)» = «codearg»;
@       end
@   end
@end
]]


local function header_file_code(env, transform_class_ctor_arguments, config)
    local function to_code_table(template)
        return common.tpleval(template, env, {returnTable=true})
    end
    local ok, code

    -- The code defining the container class. It is a table with text
    ok, code = to_code_table(container_class_definition_template)
    if not ok then  return ok, code  end
    env.container_class_definition = code

    -- A function returning the definition of a transform class.
    -- Returns a table with text; for nested evaluation within a template.
    local transform_class_def = function(tfMetadata)
      env.ctor_args  = transform_class_ctor_arguments(tfMetadata)
      env.tfMetadata = tfMetadata
      return common.tpleval_failonerror(transform_class_definition_template, env, {returnTable=true})
    end
    env.transform_class_definition = transform_class_def

    -- Tables with the code related to parameters
    ok, code = to_code_table(parameters_assignments_template)
    if not ok then  return ok, code  end
    env.parametersAssignments = code
    ok, code = to_code_table(parameters_class_definition_template)
    if not ok then  return ok, code  end
    env.parameters_struct_definition = code -- a table with text


    local includes = {}
    for i,file in ipairs(config.external.includes) do
      table.insert(includes, file)
    end
    for i,file in ipairs(config.external.iit_rbd.includes) do
      table.insert(includes, file)
    end
    env.include_directives = common.decorated_names_iterator(
                        includes, function(inc) return '#include '..inc end)

    env.include_guard = env.ctModelMetadata.name:gsub('-','_'):upper() .. "_TRANSFORMS_GEN_H"
    return common.tpleval(header_template, env)
end



header_file_generator = header_file_code
