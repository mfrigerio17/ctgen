--- The functions of this module must reflect the backend-specific policies for
--- the code generated to deal with variables, parameters and constants.
---
--- Other functions reflect some misc backend-specific details, e.g. what is the
--- code expression to assign a value to a coefficient of a matrix (which depends
--- on the target language, libraries used, etc.)
---
--- The functions of this module do NOT affect the code generation
--- templates of the backend. In fact, they must _reflect_ the policies
--- of the templates, encoding some relevant features of the backend.
--- These functions can then be given to generic code-generators, in order to
--- generate code consistent with the backend.
---
--- Most functions in this module are generators of code-expressions (text) that
--- shall evaluate (in the runtime of the target language!) to the value of the
--- given math-expressions.
---
--- For example, if the backend's behavior is to generate a global container
--- with a field for every constant in the input model (think of a C struct),
--- then the code-expression that resolve to the value of a constant will have
--- to be something in the form `<container name>.<constant name>`.
--- The code-expression evaluating expressions like `2 * <constant>` will be
--- something like `2 * <container name>.<constant name>`.




local function getSpecifics(config)

    local ret = {}

    ret.languageSpecifics = {
        matrixAssignment = function(varname,r,c,value)
            return varname .. "["..r..","..c.."] = " .. value .. ";"
        end,
        sympyExpressionToString = function(expr)
            return tostring(expr)
        end,
    }


    ret.variableAccess = {
        valueExpression = function(expr)
            return "<ref to <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
        sineValueExpression = function(expr)
            return "<sine of <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
        cosineValueExpression = function(expr)
            return "<cosine of <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
    }

    ret.parameterAccess = {
        valueExpression = function(expr)
            return "<ref to <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
        sineValueExpression = function(expr)
            return "<sine of <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
        cosineValueExpression = function(expr)
            return "<cosine of <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
    }

    ret.constantAccess = {
        valueExpression = function(expr)
            return "<ref to <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
        sineValueExpression = function(expr)
            return "<sine of <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
        cosineValueExpression = function(expr)
            return "<cosine of <" .. tostring(expr.symbolicExpr) .. "> >"
        end,
    }

    return ret
end

ctgen__plaintext_backend = {
    getSpecifics = getSpecifics
}

return ctgen__plaintext_backend
