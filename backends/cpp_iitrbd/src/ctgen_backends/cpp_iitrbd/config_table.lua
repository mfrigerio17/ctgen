local files = {
    header = "transforms.h",
    source = "transforms.cpp",

    test = {
        header = "tests.h",
        source = "tests.cpp",
        subdir = "test",
        per_tf_source = function(tf)
            return "test_" .. tf.name .. ".cpp"
        end,
    },

    --- The root subdirectory for header files
    include_basedir = "include",

    --- The list of nested directories where to place the header files
    include_dirs = function(ctModelMeta) return {
        ctModelMeta.name, 'ctgen'
    } end,
}

local variables_status_formal_parameter = 'state'
local parameters_status_formal_parameter= 'params'
local model_property_to_varname = function(property) return property.name end
local def_scalar_traits_name = 'ScalarTraits'


local function view_as(tfMetadata, posPolarity, strToken)
    if posPolarity then
        return tfMetadata.ct.leftFrame.name .. strToken .. tfMetadata.ct.rightFrame.name
    else
        return tfMetadata.ct.rightFrame.name .. strToken .. tfMetadata.ct.leftFrame.name
    end
end
local transform_view_as = {
    motion = function(tfMetadata, posPolarity)
        return view_as(tfMetadata, posPolarity, '_XM_')
    end,
    force = function(tfMetadata, posPolarity)
        return view_as(tfMetadata, posPolarity, '_XF_')
    end,
    homog = function(tfMetadata, posPolarity)
        return view_as(tfMetadata, posPolarity, '_XH_')
    end,
}


--- The default configuration for the C++ code generators of this package.
-- Overwrite individual entries to customize the generated code.
--
local config = {
    files = files,

    model_property_to_varname = model_property_to_varname,

    -- When an option to generate a local type/definition is set to false, the
    -- other values of the same group might also need to be overridden.
    -- For example, if the type definition for the variables-status must not be
    -- generated, a suitable type is expected to be available in the compilation
    -- unit of the generated source; that is, a suitable type must be defined in
    -- one of the included headers (see the 'external' options below). Hence,
    -- the `status_type` name should be overridden to reflect the actual type
    -- name. In addition, the `value_expression` function should be defined so
    -- as to generate the expression that gives read-access to the given
    -- variable, which of course depends again on the variables-status type.

    variables = {
        generate_local_status_type = true,
        status_type  = 'VarsState',
        status_formal_parameter = variables_status_formal_parameter,
        value_expression = function(var)
            return variables_status_formal_parameter .. '.' .. model_property_to_varname(var)
        end,
    },

    --- The model parameters
    parameters = {
        --- Generate a local struct to hold the parameter values. On/Off
        generate_local_status_type = true,

        --- Name of the type acting as the container for the parameter values
        status_type = 'ModelParameters',

        --- The name of the formal parameter of type `status_type`
        status_formal_parameter = parameters_status_formal_parameter,

        --- The valid C++ expression resulting in read access of the given parameter
        value_expression = function(param)
            return parameters_status_formal_parameter .. '.' .. model_property_to_varname(param)
        end,

        --- Name of the type with the parameters actually used internally.
        -- This differs from `status_type` as it does not host the value of
        -- rotation parameters, but only the values of the corresponding sine
        -- and cosine.
        --
        -- When the transforms container is _not_ generated, user code needs to
        -- instantiate this type and pass the object(s) to the constructor of
        -- the individual transform classes; that allows to control whether the
        -- transforms share the parameter values, or not.
        internal_type  = 'Parameters',
    },

    constants = {
        generate_local_defs = true,
        local_defs_container_name = 'ModelConstants',
        value_expression = function(constant)
            return model_property_to_varname(constant)
        end,
        use_constexpr = false -- set to true only if the scalar type is going to be a LiteralType
    },

    scalar_traits = {
        use_default = true,
        type_name = def_scalar_traits_name
    },

    container_class = {
        generate_it = true,

        -- The name of the class having all the transforms as members
        class_name = function(ctModelMeta) return 'Transforms' end,

        members = {
            transform = function(tfMetadata) return 'm_' .. tfMetadata.name end,
            update_params = 'updateParams',
            update = 'update',
            parameters = 'parameters'
        }
    },

    transform_class = {
        class_name = function(transformMetadata) return transformMetadata.name  end,
        members = {
            update_params = 'updateParams',
            update = 'update',
            parameters = 'parameters',
            view_as = transform_view_as
        }
    },

    --- The namespace(s) that will enclose the generated code
    namespaces = function(ctModelMeta) return {
        ctModelMeta.name, 'ctgen'
    } end,


    tpl = {
        template_all = false,
        dummy_container = '_tf'
    },


    external = {
        includes = {
        },

        -- Identifiers related to the external library iit-rbd, used by the
        -- generated code. DO NOT change unless the iit-rbd library changes, or
        -- you really know what you are doing.
        iit_rbd = {
            namespaces = {
                'iit', 'rbd'
            },

            includes = {
                '<iit/rbd/compact_transform.h>', '<iit/rbd/scalar_traits.h>'
            },

            base_class = 'TransformBase',
            double_traits = 'DoubleTraits',
            scalar_traits = 'ScalarTraits',
            scalar_type_name = 'Scalar',

            inherited_members = {
                ct = {
                    name   = 'ct',
                    rot_mx = 'a_R_b',
                    vector = 'r_ab_a',
                    cast_type = {
                      motion = function(posPolarity) if posPolarity then return 'A_XM_B' else return 'B_XM_A' end end,
                      force  = function(posPolarity) if posPolarity then return 'A_XF_B' else return 'B_XF_A' end end,
                      homog  = function(posPolarity) if posPolarity then return 'A_XH_B' else return 'B_XH_A' end end,
                    }
                }
            }
        }
    },

    -- Identifiers used internally in the generated code, which are not exposed
    -- to the public interface. That is, these values only affect cosmetically
    -- the generated code.
    internal = {
        scalar_t = 'scalar_t',
        scalar_traits = def_scalar_traits_name,
        variables_status_t = 'state_t', -- for a local typedef
        transform_base_class = 'Transform',
        parameters_member = 'parameters',
        parameters_t = 'Parameters',
        constants_container = 'Constants',

        cached_value_identifier = function(expression) return expression.toIdentifier() end,
        cached_sinvalue_identifier = function(expression) return 's__'..expression.toIdentifier() end,
        cached_cosvalue_identifier = function(expression) return 'c__'..expression.toIdentifier() end,
    }
}


return config
