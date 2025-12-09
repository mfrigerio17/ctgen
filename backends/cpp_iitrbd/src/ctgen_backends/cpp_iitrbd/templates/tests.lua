local common = common

local individual_main_template =
[[
#include <array>
#include <iit/rbd/rbd.h>
#include <ctgen/cppiitrbd/testmain_tpl.h>
#include <ctgen/cppiitrbd/dataset.h>

#include <«ids.include_path»/«files.header»>

struct Test_«tf.name»
{
    using Mx44 = iit::rbd::PlainMatrix<double,4,4>;

    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
        compute_«tf.name»<::ctgen::NaiveBinDataset>(ds, computed);
    }
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
        compute_«tf.name»<::ctgen::TextDataset>(ds, computed);
    }

private:
    template<class Dataset>
    static void compute_«tf.name»(Dataset& ds, Mx44& computed)
    {
        using Transform = «ns»::«ids.transform_class.class_name(tf)»;
@if tf.is_parametric then
        using SrcParams = «ns»::«ctrl.parameters.status_type»;
        using Params    = «ns»::«ctrl.parameters.internal_type»;
        static Params params;
        static Transform xt(params);
        static SrcParams srcParams;
@else
        static Transform xt;
@end
@if tf.is_dependent then
        static «ns»::VarsState q;
@   local vcount = common.pylen(tf.variables)
        std::array<double, «vcount»> aux_vars;
        ds.readVector(«vcount», aux_vars);
@   local i = 0
@   for var in python.iter(tf.variables) do
        «ctrl.variables.assignable_expression(var, "q")» = aux_vars[«i»];
@       i = i + 1
@   end
@end
@if tf.is_parametric then
@   local pcount = common.pylen(tf.parameters)
        std::array<double, «pcount»> aux_pars;
        ds.readVector(«pcount», aux_pars);
@   local i = 0
@   for p in python.iter(tf.parameters) do
        srcParams.«ids.model_property_to_varname(p)» = aux_pars[«i»];
@       i = i + 1
@   end
    // inject the new parameter values in the transform
        params = srcParams;
@   if not tf.is_dependent then
        xt.update();
@   end
@end
@if tf.is_dependent then
        computed = xt(q).«ids.transform_class.members.view_as.homog(tf,true)»().matrix();
@else
        computed = xt.«ids.transform_class.members.view_as.homog(tf,true)»().matrix();
@end
    }

};


int main(int argc, char** argv)
{
    return ::ctgen::testmain<Test_«tf.name»>(argc, argv);
}
]]

local function generators(env)

    return {
        per_tf_main = function(tf)
            env.tf = tf
            env.ns = env.ids.ns.qualifier
            if env.template_all then
                env.ns = env.ns .. "::" .. env.tpl.container.name .. "<double>"
            end
            return common.tpleval(individual_main_template, env)
        end
    }
end


tests_generator = generators
