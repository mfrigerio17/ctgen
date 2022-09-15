# Project configuration
cmake_minimum_required(VERSION 2.8)
project(ctgen-cppiitrbd-test)

set(HEADER_INSTALL_ROOT /usr/local/include/ CACHE PATH "Where to install the headers")
set(LIB_INSTALL_ROOT    /usr/local/lib/     CACHE PATH "Where to install the shared library")

set(CMAKE_CXX_FLAGS "-g -Wall -O3 -std=c++11")

set(LIB_NAME ctgen_cppiitrbd_test)


set(SOURCES
    dataset.cpp
)

# Include directories
include_directories(./include/)

# Add library
add_library(${LIB_NAME} SHARED ${SOURCES})

# Install (ie copy) header files
install(DIRECTORY include/ DESTINATION ${HEADER_INSTALL_ROOT} PATTERN *~ EXCLUDE)

# Install the shared library
install(TARGETS ${LIB_NAME} LIBRARY DESTINATION ${LIB_INSTALL_ROOT})
