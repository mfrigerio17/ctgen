
-- local-ize the expected global objects

local templates = ctgen_plaintext_templates
local assignments = ctgen__matrix_coeff_assignments
local common = common


--- Main code-generation function in the Lua sources.
-- This is the entry point for the generation algorithm implemented in Lua,
-- and it is invoked by the generation function in python.
--
-- Arguments:
-- * `backend`: the table returned by `getSpecifics()` in the backend.lua
--    module
-- * `ctModelMetadata`: the python container for the coordinate transform model
--   and its metadata. This must be an instance of `kgprim.ct.metadata.TransformsModelMetadata`
-- * `matricesMetadata`: a python mapping from matrix name to corresponding
--   `kgprim.ct.repr.mxrepr.MatrixReprMetadata` object, for each matrix whose
--   implementation has to be generated
-- * `resolvedMatrices`: similar python mapping as above, but the values must be
--   matrices whose coefficients are the textual representation of the
--   expression that resolves to the value (TODO clarify)
local function generate(backend, ctModelMetadata, matricesMetadata, resolvedMatrices)

    local langSpecs = backend.languageSpecifics
    local generators = {}
    local matrices_names = {}
    for name in python.iter(matricesMetadata) do
        local mxMeta = matricesMetadata[name]
        local assignmentsGen = assignments.getMatrixSpecificGenerators(
            langSpecs, mxMeta, resolvedMatrices[name])
        --for statement in assignmentsGen.constantCoefficientsAssignments(mxMeta.ctMetadata.name) do
        --    print(statement)
        --end
        generators[name] = assignmentsGen
        table.insert(matrices_names, name)
    end

    local tpl_evaluation_env = {
        assignments_generators = generators,
    }

    local root_tpl_evaluation_env = {
        assignments_constant_coeffs = common.tpleval_failonerror(
            templates.constant_coefficients_assignments,
            tpl_evaluation_env,
            {returnTable=true}),
        assignments_variable_coeffs = common.tpleval_failonerror(
            templates.variable_coefficients_assignments,
            tpl_evaluation_env,
            {returnTable=true}),
        matrices_names = matrices_names
    }

    local code = common.tpleval_failonerror(
        templates.root,
        root_tpl_evaluation_env)

    return true, code
end


return {
    generate = generate
}
