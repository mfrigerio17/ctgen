
local model_property_to_varname = function(property) return property.name end
local variables_status_formal_parameter = 'state'
local parameters_status_formal_parameter= 'params'

local mx_class_name = function(matrixMetadata)
    ctr  = matrixMetadata.ctMetadata.ct
    kind = matrixMetadata.representationKind.name
    key = 'X' -- default
    if    (kind == "homogeneous") then key = 'xh'
    elseif(kind == "spatial_motion") then key = 'xm'
    elseif(kind == "spatial_force") then key = 'xf'
    elseif(kind == "pure_rotation") then key = 'rot'
    end

    return ctr.leftFrame.name .. '_' .. key .. '_' .. ctr.rightFrame.name
end

local config = {
    model_property_to_varname = model_property_to_varname,

    variables = {
        status_formal_parameter = variables_status_formal_parameter,
        value_expression = function(var)
            return variables_status_formal_parameter .. '.' .. model_property_to_varname(var)
        end,
    },

    --- The model parameters
    parameters = {
        status_formal_parameter = parameters_status_formal_parameter,

        -- The class member of struct type, containing the parameter values
        member_name = 'params',
    },

    constants = {
        value_expression = function(container, constant)
            -- somewhere in the code need to make a closure of this function
            -- to get rid of the container argument, which will be the output
            -- of constants_container_name() once the ctModelMetadata argument
            -- is known
            return container .. '.' .. model_property_to_varname(constant)
        end
    },

    meta = {
        this_obj_ref = 'obj',
        tf_class = {
            class_name = mx_class_name,
            members = {
                matrix    = 'mx',
                constants = 'constants',
            },
            methods = {
                update_parameters = 'updateParams',
                update = 'update',
                update_explicit_vars = 'updateExplicit',
            },
            fargs = {
                constants = 'cc',
            }
        },
        constants_class = {
            class_name = function(ctModel) return ctModel.name .. 'ModelConstants' end,
        },
    },

    internal = {
        cached_value_identifier    = function(expression) return expression.toIdentifier() end,
        cached_sinvalue_identifier = function(expression) return 's__'..expression.toIdentifier() end,
        cached_cosvalue_identifier = function(expression) return 'c__'..expression.toIdentifier() end,
    }

}

return config
