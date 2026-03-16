cmake_minimum_required(VERSION 3.0.2...3.22)
project(ctgen-CtgenSample)

add_compile_options(-Wall -O2 -std=c++11)

# Include directories
include_directories(./include)

set(SOURCES
    transforms.cpp
)
add_library(objs OBJECT ${SOURCES})

add_executable(t_frameA_X_frameB
    $<TARGET_OBJECTS:objs>
    test/test_frameA_X_frameB.cpp
)
target_link_libraries(t_frameA_X_frameB ctgen_cppiitrbd_test)

add_executable(t_frameD_X_frameB
    $<TARGET_OBJECTS:objs>
    test/test_frameD_X_frameB.cpp
)
target_link_libraries(t_frameD_X_frameB ctgen_cppiitrbd_test)

add_executable(t_frameE_X_frameG
    $<TARGET_OBJECTS:objs>
    test/test_frameE_X_frameG.cpp
)
target_link_libraries(t_frameE_X_frameG ctgen_cppiitrbd_test)



