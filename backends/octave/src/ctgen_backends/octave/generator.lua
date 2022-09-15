local common    = common



local function allGenerators(ctModelMetadata, statementsGenerator, config)

    local transforms = {}
    for tf in python.iter(ctModelMetadata.transformsMetadata) do
      table.insert(transforms, tf)
    end
    local env = {
        ctrl = {
            variables  = config.variables,
        },
        ids = {
            varName      = config.internal.cached_value_identifier,
            sinVarName   = config.internal.cached_sinvalue_identifier,
            cosVarName   = config.internal.cached_cosvalue_identifier,
            this         = config.this_obj_ref,
            varStateArgName = config.variables.status_formal_parameter,
            matrixMember = config.matrix_member_name,
            mxClassName  = config.mx_class_name,
            parameters   = config.parameters,
            transforms   = transforms,
        },
        modelConstantsGlobal=config.constants.container_name(ctModelMetadata),
        python = python,
        common = common,
    }
    local mxmember = env.ids.this .. '.' .. env.ids.matrixMember

    local init_statements = function(statements_generator)
        return function()
            return common.lineDecorator(
                function()
                    return common.myiter(statements_generator.constantCoefficientsAssignments(mxmember))
                end, '', ';')
        end
    end
    local update_statements = function(statements_generator)
        return function()
            return common.lineDecorator(
                function()
                    return common.myiter(statements_generator.variableCoefficientsAssignments(mxmember))
                end, '', ';')
        end
    end


local function modelConstants()
    local tpltext = [[
global «containerName» = struct();

@for cc, _ in pairs(constants) do
«containerName».«varname(cc)» = «cc.value»;
@end

@for constant, expressions in pairs(constants) do
@   local c_ref = containerName .. '.' .. varname(constant)
@   for i, expr in pairs(expressions) do
@       local expr_code = expr.toCode( c_ref )
@       if expr.isRotation() then
«containerName».«ids.sinVarName(expr)» = sin( «expr_code» );
«containerName».«ids.cosVarName(expr)» = cos( «expr_code» );
@       else
@           if not expr.isIdentity() then
«containerName».«ids.varName(expr)» = «expr_code»;
@           end
@       end
@   end
@end
]]
    local env2 = {
        ctModelMetadata = ctModelMetadata,
        ids = env.ids,
        constants  = common.python_dictOfSets_to_table( ctModelMetadata.constants ),
        containerName = config.constants.container_name(ctModelMetadata),
        varname = config.model_property_to_varname
    }
    return common.tpleval(tpltext, env2)
end

local function matrixFunction(matrixReprMeta)
   local tpltext = [[
@local TF = ids.mxClassName(matrixReprMeta)
classdef «TF» < handle

properties
@if tf.parametric then
    «ids.parameters.member_name» = struct();
@end
    «ids.matrixMember» = zeros(«matrixReprMeta.rows()»,«matrixReprMeta.cols()»);
endproperties

methods
function «ids.this» = «TF»()
    global «modelConstantsGlobal»;
    ${initStatements}

@if tf.parametric then
    % Initializes the parameters
@   local P = ids.parameters.member_name
@   for param, expressions in pairs(parameters) do
@       for i, expr in pairs(expressions) do
@           if expr.isRotation() then
    «ids.this».«P».«ids.sinVarName(expr)» = 0;
    «ids.this».«P».«ids.cosVarName(expr)» = 1;
@           else
    «ids.this».«P».«ids.varName(expr)» = 0;
@           end
@       end
@   end
@end
endfunction

function update(«ids.this», «ids.varStateArgName»)
    global «modelConstantsGlobal»;
@for var, expressions in pairs(variables) do
@   for k, expr in pairs(expressions) do
@       local codearg = expr.toCode( ctrl.variables.value_expression(var) )
@       if expr.isRotation() then
    «ids.sinVarName(expr)» = sin( «codearg» );
    «ids.cosVarName(expr)» = cos( «codearg» );
@       end
@   end
@end
    ${assignments}
endfunction


@if varcount > 0 then
function updateExplicit(«ids.this», «table.concat(varnames, ", ")»)
    @for var, _ in pairs(variables) do
    «ctrl.variables.value_expression(var)» = «var.name»;
    @end
    obj.update(«ids.varStateArgName»);
@else
function updateExplicit(«ids.this»)
    obj.update([]);
@end
endfunction

@if tf.parametric then
@   local P = ids.parameters.member_name
function updateParams(«ids.this», «table.concat(parnames, ", ")»)
@   for param, expressions in pairs(parameters) do
@       for i, expr in pairs(expressions) do
@           local codearg = expr.toCode( param.name )
@           if expr.isRotation() then
    «ids.this».«P».«ids.sinVarName(expr)» = sin( «codearg» );
    «ids.this».«P».«ids.cosVarName(expr)» = cos( «codearg» );
@           else
    «ids.this».«P».«ids.varName(expr)» = «codearg»;
@           end
@       end
@   end
endfunction
@end

endmethods

endclassdef

]]
    local ctMetadata = matrixReprMeta.ctMetadata
    local varnames = {}
    local varcount = 0
    for i,var in common.myiter(ctMetadata.vars) do
        table.insert(varnames, var.name)
        varcount = varcount + 1
    end
    local parnames = {}
    for i,par in common.myiter(ctMetadata.pars) do
        table.insert(parnames, par.name)
    end
    local statementsGen = statementsGenerator.getMatrixSpecificGenerators(matrixReprMeta)

    env.tf = ctMetadata
    env.parameters = common.python_dictOfSets_to_table( ctMetadata.pars )
    env.variables  = common.python_dictOfSets_to_table( ctMetadata.vars )
    env.varcount   = varcount
    env.matrixReprMeta = matrixReprMeta
    env.parnames = parnames
    env.varnames = varnames
    env.initStatements= init_statements(statementsGen)
    env.assignments   = update_statements(statementsGen)
    return common.tpleval(tpltext, env)
end

return {
  matrixFunction = matrixFunction,
  modelConstants = modelConstants,
  tests = tests_generator(env) --a global, defined in tests_tpl.lua
}

end

return allGenerators
