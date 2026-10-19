cmake_minimum_required(VERSION 3.22.1)
project(comicdiffusion LANGUAGES CXX)

if(NOT DEFINED MNN_ROOT)
  message(FATAL_ERROR "MNN_ROOT must point to the checked-out MNN 3.6.1 source tree")
endif()
if(NOT DEFINED MNN_RUNTIME_LIB)
  message(FATAL_ERROR "MNN_RUNTIME_LIB must point to the verified arm64-v8a libMNN.so")
endif()

add_library(MNN SHARED IMPORTED)
set_target_properties(MNN PROPERTIES IMPORTED_LOCATION "${MNN_RUNTIME_LIB}")

add_library(comicdiffusion SHARED comic_diffusion_jni.cpp)
target_compile_features(comicdiffusion PRIVATE cxx_std_17)
target_include_directories(comicdiffusion PRIVATE
  "${MNN_ROOT}/include"
  "${MNN_ROOT}/transformers/diffusion/engine/include"
  "${MNN_ROOT}/source"
)
target_link_libraries(comicdiffusion PRIVATE MNN log android dl)
