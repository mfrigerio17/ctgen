--- See the documentation of backend.lua in the plaintext backend

local function getSpecifics(config, ctModel)
    local ret = {}
    local p_prefix = config.this_obj_ref .. "." .. config.parameters.member_name
    local c_prefix = config.constants.container_name(ctModel)

    ret.languageSpecifics = {
        matrixAssignment = function(varname,r,c,value)
            return varname .. "(".. (r+1) ..",".. (c+1) ..") = " .. value
        end,
        sympyExpressionToString = function(expr)
            return tostring(expr)
        end,
    }

    ret.variableAccess = {
        valueExpression = function(expr)
            local argValue = config.variables.value_expression(expr.expression.arg)
            return expr.toCode( argValue )
        end,
        sineValueExpression = function(expr)
            return config.internal.cached_sinvalue_identifier(expr)
        end,
        cosineValueExpression = function(expr)
            return config.internal.cached_cosvalue_identifier(expr)
        end,
    }

    ret.parameterAccess = {
        valueExpression = function(expr)
            return  p_prefix .. "." .. config.internal.cached_value_identifier(expr)
        end,
        sineValueExpression = function(expr)
            return p_prefix .. "." .. config.internal.cached_sinvalue_identifier(expr)
        end,
        cosineValueExpression = function(expr)
            return p_prefix .. "." .. config.internal.cached_cosvalue_identifier(expr)
        end,
    }

    ret.constantAccess = {
        valueExpression = function(expr)
            return c_prefix .. "." .. config.internal.cached_value_identifier(expr)
        end,
        sineValueExpression = function(expr)
            return c_prefix .. "." .. config.internal.cached_sinvalue_identifier(expr)
        end,
        cosineValueExpression = function(expr)
            return c_prefix .. "." .. config.internal.cached_cosvalue_identifier(expr)
        end,
    }

    return ret
end

ctgen__octave_backend = {
    getSpecifics = getSpecifics
}

return ctgen__octave_backend
