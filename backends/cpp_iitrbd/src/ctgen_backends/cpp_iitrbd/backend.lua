

local function getSpecifics(config)

    local ret = {}

    local iit_rbd = config.external.iit_rbd

    ret.languageSpecifics = {
        matrixAssignment = function(varname,r,c,value)
            local field_rot_mx = iit_rbd.inherited_members.ct.rot_mx
            local field_tr_vect= iit_rbd.inherited_members.ct.vector
            if c<3 and r<3 then -- the rotation matrix
                return string.format(
                    "%s.%s(%d,%d) = %s;",
                    varname, field_rot_mx, r, c, value)
            else  -- the translation vector
                if c==3 and r<3 then
                    return string.format(
                        "%s.%s(%d) = %s;",
                        varname, field_tr_vect, r, value)
                end
            end
            return ""
        end,
        sympyExpressionToString = function(expr)
            return config.sympy_to_text(expr)
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
            return config.transform_class.members.parameters .. "." ..
                config.internal.cached_value_identifier(expr)
        end,
        sineValueExpression = function(expr)
            return config.transform_class.members.parameters .. "." ..
                config.internal.cached_sinvalue_identifier(expr)
        end,
        cosineValueExpression = function(expr)
            return config.transform_class.members.parameters .. "." ..
                config.internal.cached_cosvalue_identifier(expr)
        end,
    }

    --- The generators of code-expressions that evaluate to the value of the
    -- given constant math-expressions.
    -- These functions are coupled with the generators of this backend, which
    -- generate the code that declares and defines the constants.
    -- That is, the expressions that evaluate to the values of constants depend
    -- of course on how the constants are defined in code (e.g. as members of a
    -- struct).
    ret.constantAccess = {
        valueExpression = function(expr)
            if expr.isIdentity() then
                local constant = expr.expression.arg
                if config.constants.generate_local_defs then
                    -- conform to the policy of the other generators of this
                    --  backend, that is, the constants are static members of a
                    --  container
                    local cont = config.constants.local_defs_container_name
                    return cont .. "::" .. config.model_property_to_varname(constant)
                else
                    -- use the user-supplied read-access expression
                    return config.constants.value_expression(constant)
                end
            else
                return config.internal.constants_container .. "::" ..
                    config.internal.cached_value_identifier(expr)
            end
        end,
        sineValueExpression = function(expr)
            return config.internal.constants_container .. "::" ..
                    config.internal.cached_sinvalue_identifier(expr)
        end,
        cosineValueExpression = function(expr)
            return config.internal.constants_container .. "::" ..
                    config.internal.cached_cosvalue_identifier(expr)
        end,
    }

    return ret
end

ctgen_cppiitrbd_backend = {
    getSpecifics = getSpecifics
}

return ctgen_cppiitrbd_backend
