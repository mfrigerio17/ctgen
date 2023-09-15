local common = common

local cmake_template =
[[
cmake_minimum_required(VERSION 2.8)
project(ctgen-«ctModelMetadata.name»)

set(CMAKE_CXX_FLAGS "-Wall -O2 -std=c++11")


set(SOURCES
@if not template_all then
    «files.source»
@end
    «files.test.subdir»/«files.test.source»
)

# Include directories
include_directories(./«files.include_basedir»)

@local SRCS = "${SOURCES}"
@for i, tf in ipairs(transforms) do
add_executable(t_«tf.name»
    «SRCS»
    «files.test.subdir»/«files.test.per_tf_source(tf)»
)
target_link_libraries(t_«tf.name» ctgen_cppiitrbd_test)

@end

]]


function cmake_generator(env)
    return common.tpleval(cmake_template, env)
end