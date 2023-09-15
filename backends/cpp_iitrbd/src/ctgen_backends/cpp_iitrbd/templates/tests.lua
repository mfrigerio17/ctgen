local common = common


local header_template =
[[
#pragma once

#include <iit/rbd/rbd.h>
#include <ctgen/cppiitrbd/dataset.h>

#include <«ids.include_path»/«files.header»>

${ids.ns.open}

using Mx44 = iit::rbd::PlainMatrix<double,4,4>;


@for i, tf in ipairs(transforms) do
struct Test_«tf.name»
{
    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed);
};

@end

${ids.ns.close}
]]

local source_template =
[[
#include <«ids.include_path»/«files.test.subdir»/«files.test.header»>

template<int N>
using Vec = iit::rbd::PlainMatrix<double,N,1>;

@if template_all then
«ids.ns.qualifier»::Transforms<double> transforms;
«ids.ns.qualifier»::VarsState<double> q;
@else
«ids.ns.qualifier»::Transforms transforms;
«ids.ns.qualifier»::VarsState q;
@end

@for i, tf in ipairs(transforms) do
    @local vcount = common.pylen(tf.vars)
void «ids.ns.qualifier»::Test_«tf.name»::computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed)
{
    @if vcount>0 then
    Vec<«vcount»> aux_vars;
    ds.readVector(«vcount», aux_vars);
        @local i = 0
        @for var in python.iter(tf.vars) do
    q.«ids.model_property_to_varname(var)» = aux_vars(«i»);
            @i = i + 1
            @if i==vcount then break end
        @end
    @end
    computed = transforms.«ids.container_class.members.transform(tf)»(q).«ids.transform_class.members.view_as.homog(tf,true)»().matrix();
}

@end
]]

local individual_main_template =
[[
#include <«ids.include_path»/«files.test.subdir»/«files.test.header»>
#include <ctgen/cppiitrbd/testmain_tpl.h>

int main(int argc, char** argv)
{
    return ::ctgen::testmain<«ids.ns.qualifier»::Test_«tf.name»>(argc, argv);
}
]]

local function generators(env)

    return {
        header = function() return common.tpleval(header_template, env) end,
        source = function() return common.tpleval(source_template, env) end,
        per_tf_main = function(tf)
            env.tf = tf
            return common.tpleval(individual_main_template, env)
        end
    }
end


tests_generator = generators
