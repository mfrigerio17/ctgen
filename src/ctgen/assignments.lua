-- This module contains common functions to generate the code for the
-- assignments of matrix coefficients.
--
-- These are the functions that actually transform the Sympy expressions (every
-- matrix coefficient is in general a Sympy expression) into text.
--
-- The generators of this module require to be given matrices where all the
-- referenced symbols (variables, parametes, constants) are "resolved". See the
-- Python module `ctgen.common.SymbolicCoefficientsResolver`.
--
-- With resolved matrices, turning the Sympy expressions to text is usually as
-- simple as tostring-ing the expression.


local common = ctgen__common


--- Factory for the functions that generate the assignments of the matrix
--- coefficients.
--
--
local getMatrixSpecificGenerators = function(lang, matrixMetadata, resolvedMatrix)
    -- resolvedMatrix must have all reference to symbols resolved
    local ret = {}
    local coefficient = common.py_matrix_coeff(resolvedMatrix)

    ret.constantCoefficientsAssignments = function(matrixVarName)
        local it, inv, ctrl = python.iter(matrixMetadata.constantCoefficients)
        return function()
            local r,c = it(inv, ctrl) -- run the iterator once
            ctrl = r
            if r ~= nil then
                -- we do not generate assignments of zeros, assuming the matrix is initialized
                local value = coefficient(r, c)
                if value ~= 0.0 then
                    -- even though it is constant, it may still be an expression
                    -- hence we use the dedicated toString function
                    local value_expr = lang.sympyExpressionToString( value )
                    return lang.matrixAssignment(matrixVarName,r,c,value_expr)
                end
            end
            return nil
        end, inv, ctrl
    end

    ret.variableCoefficientsAssignments = function(matrixVarName)
        local it, inv, ctrl = python.iter(matrixMetadata.variableCoefficients)
        return function()
            local r,c = it(inv, ctrl) -- run the iterator once
            ctrl = r
            if r ~= nil then
                local value = lang.sympyExpressionToString( coefficient(r,c) )
                return lang.matrixAssignment(matrixVarName,r,c, value)
            end
            return nil
        end, inv, ctrl
    end

    return ret
end


-- The global table with the functions of this module
ctgen__matrix_coeff_assignments = {
    getMatrixSpecificGenerators = getMatrixSpecificGenerators,
}

return ctgen__matrix_coeff_assignments
