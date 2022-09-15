
local model_property_to_varname = function(property) return property.name end
local variables_status_formal_parameter = 'state'
local parameters_status_formal_parameter= 'params'
local constants_container_name = function(ctModel) return ctModel.name .. 'ModelConstants' end
local this_obj_ref = 'obj'

local config = {

    mx_class_name = function(matrixMetadata)
        ctr  = matrixMetadata.ctMetadata.ct
        kind = matrixMetadata.representationKind.name
        key = 'X' -- default
        if    (kind == "homogeneous") then key = 'xh'
        elseif(kind == "spatial_motion") then key = 'xm'
        elseif(kind == "spatial_force") then key = 'xf'
        elseif(kind == "pure_rotation") then key = 'rot'
        end

        return ctr.leftFrame.name .. '_' .. key .. '_' .. ctr.rightFrame.name
    end,

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
        container_name = constants_container_name,
        generate_local_defs = true,
        value_expression = function(container, constant)
            -- somewhere in the code need to make a closure of this function
            -- to get rid of the container argument, which will be the output
            -- of constants_container_name() once the ctModelMetadata argument
            -- is known
            return container .. '.' .. model_property_to_varname(constant)
        end
    },

    this_obj_ref = this_obj_ref,
    matrix_member_name = 'mx',

    internal = {
        cached_value_identifier    = function(expression) return expression.toIdentifier() end,
        cached_sinvalue_identifier = function(expression) return 's__'..expression.toIdentifier() end,
        cached_cosvalue_identifier = function(expression) return 'c__'..expression.toIdentifier() end,
    }

}

return config