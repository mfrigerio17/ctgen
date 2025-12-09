local common = common

local cmake_template =
[[
cmake_minimum_required(VERSION 3.0.2...3.22)
project(ctgen-«ctModelMetadata.name»)

add_compile_options(-Wall -O2 -std=c++11)

# Include directories
include_directories(./«files.include_basedir»)

@if not template_all then
set(SOURCES
    «files.source»
)
add_library(objs OBJECT ${SOURCES})
@end

@for i, tf in ipairs(transforms) do
add_executable(t_«tf.name»
@   if not template_all then
    \$<TARGET_OBJECTS:objs>
@   end
    «files.test.subdir»/«files.test.per_tf_source(tf)»
)
target_link_libraries(t_«tf.name» ctgen_cppiitrbd_test)

@end


]]


function cmake_generator(env)
    return common.tpleval(cmake_template, env)
end
