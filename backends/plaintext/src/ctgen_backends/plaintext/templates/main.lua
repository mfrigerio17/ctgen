local root =
[[
# Code generated by the "plaintext" backend of the CtGen tool.

# List of matrices
@for _,name in pairs(matrices_names) do
«name»
@end

# Costant coefficients assignments
${assignments_constant_coeffs}

# Variable coefficients assignments
${assignments_variable_coeffs}

]]

local assignments_costants = [[
@for mxname,generator in pairs(assignments_generators) do
@   for statement in generator.constantCoefficientsAssignments(mxname) do
«statement»
@   end
@end
]]

local assignments_variables = [[
@for mxname,generator in pairs(assignments_generators) do
@   for statement in generator.variableCoefficientsAssignments(mxname) do
«statement»
@   end
@end
]]



ctgen_plaintext_templates = {
    root = root,
    constant_coefficients_assignments = assignments_costants,
    variable_coefficients_assignments = assignments_variables,
}