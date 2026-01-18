cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYBIND11_NEWPYTHON ON)

option(BUILD_TESTS      "Build tests"    OFF)
option(BUILD_EXAMPLES   "Build examples" OFF)
option(UTPP_INCLUDE_TESTS_IN_BUILD   "Build tests" OFF)
option(MKF_INCLUDE_TESTS      "Build tests"    OFF)
option(BUILD_TESTS      "Build tests"    OFF)
option(BUILD_EXAMPLES   "Build examples" OFF)
option(BUILD_DEMO   "Build examples" FALSE)
option(HAVE_LAPACK   "HAVE_LAPACK" 0)

set(CMAKE_CXX_STANDARD 23) 
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /bigobj")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Ox")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W0")
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
else ()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wno-deprecated-declarations -Wno-unused-parameter -Wno-switch")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -pg")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -pg")
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)

    # set(CMAKE_BUILD_TYPE RelWithDebInfo)
    # set(CMAKE_BUILD_TYPE MinSizeRel)
    set(CMAKE_BUILD_TYPE Release)
endif()

SET(MAS_DIRECTORY "${CMAKE_BINARY_DIR}/MAS/")
SET(MAS_DIR "${CMAKE_BINARY_DIR}/_deps/mas-src/")
SET(MKF_DIR "${CMAKE_BINARY_DIR}/_deps/mkf-src/")
SET(FETCHCONTENT_QUIET FALSE)

message(STATUS MAS_DIRECTORY)
message(STATUS ${MAS_DIRECTORY})
message(STATUS MAS_DIR)
message(STATUS ${MAS_DIR})
message(STATUS MKF_DIR)
message(STATUS ${MKF_DIR})

include(FetchContent)

message(STATUS "Fetching https://github.com/nlohmann/json.git")
FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG  tags/v3.11.3
    GIT_PROGRESS TRUE
    )
FetchContent_MakeAvailable(json)
include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/nlohmann/")
include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/")

message(STATUS "Fetching pybind11")
FetchContent_Declare(pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git)

message(STATUS "Fetching pybind11_json")
FetchContent_Declare(pybind11_json
        GIT_REPOSITORY https://github.com/pybind/pybind11_json.git)

FetchContent_MakeAvailable( pybind11 pybind11_json)
include_directories("${CMAKE_BINARY_DIR}/_deps/pybind11-src/include/")
include_directories("${CMAKE_BINARY_DIR}/_deps/pybind11_json-src/include/")

message(STATUS "Fetching spline")
FetchContent_Declare(spline
    GIT_REPOSITORY https://github.com/AlfVII/spline.git)
FetchContent_MakeAvailable(spline)
include_directories("${CMAKE_BINARY_DIR}/_deps/spline-src/src")
    
FetchContent_Declare(levmar
    GIT_REPOSITORY https://github.com/AlfVII/levmar.git
    GIT_TAG main)
FetchContent_MakeAvailable(levmar)
include_directories("${CMAKE_BINARY_DIR}/_deps/levmar-src")

FetchContent_Declare(svg
    GIT_REPOSITORY https://github.com/AlfVII/svg)
FetchContent_MakeAvailable(svg)
include_directories("${CMAKE_BINARY_DIR}/_deps/svg-src/src")

message(STATUS "Fetching magic-enum")
FetchContent_Declare(magic-enum
    GIT_REPOSITORY https://github.com/Neargye/magic_enum
    GIT_TAG  tags/v0.9.6)
FetchContent_MakeAvailable(magic-enum)
include_directories("${CMAKE_BINARY_DIR}/_deps/magic-enum-src/include/magic_enum")

message(STATUS "Fetching matplotplusplus")
FetchContent_Declare(matplotplusplus
    GIT_REPOSITORY https://github.com/alandefreitas/matplotplusplus.git
    GIT_TAG tags/v1.2.1)
FetchContent_GetProperties(matplotplusplus)
if(NOT matplotplusplus_POPULATED)
    FetchContent_Populate(matplotplusplus)
    add_subdirectory(${matplotplusplus_SOURCE_DIR} ${matplotplusplus_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

FetchContent_Declare(rapidfuzz
  GIT_REPOSITORY https://github.com/rapidfuzz/rapidfuzz-cpp.git
  GIT_TAG main)
FetchContent_MakeAvailable(rapidfuzz)

message(STATUS "Fetching MKF")
FetchContent_Declare(MKF
        GIT_REPOSITORY https://github.com/OpenMagnetics/MKF.git
        GIT_TAG main)

message(STATUS "Fetching mas")
# Skip Git LFS to avoid bandwidth quota issues - data files are optional for build
set(ENV{GIT_LFS_SKIP_SMUDGE} "1")
FetchContent_Declare(
       mas
       GIT_REPOSITORY https://github.com/OpenMagnetics/MAS.git
       GIT_TAG main
)

message(STATUS "Fetching Properties mas")
FetchContent_GetProperties(mas)
message(STATUS "Fetching Properties MKF")
FetchContent_GetProperties(MKF)
message(STATUS ${MAS_POPULATED})
if(NOT MAS_POPULATED)
    message(STATUS "Populating MKF")
    FetchContent_Populate(mas)
endif()
message(STATUS ${MKF_POPULATED})
if(NOT MKF_POPULATED)
    message(STATUS "Populating MKF")
    FetchContent_Populate(MKF)
endif()
message(STATUS ${MAS_SOURCE_DIR})

message(STATUS "Compiling MAS")


add_custom_command(
  OUTPUT "${MAS_DIRECTORY}/MAS.hpp"
  COMMAND quicktype -l c++ -s schema ${MAS_DIR}/schemas/MAS.json 
    -S ${MAS_DIR}/schemas/magnetic.json
    -S ${MAS_DIR}/schemas/magnetic/core.json
    -S ${MAS_DIR}/schemas/magnetic/coil.json
    -S ${MAS_DIR}/schemas/utils.json
    -S ${MAS_DIR}/schemas/magnetic/core/gap.json
    -S ${MAS_DIR}/schemas/magnetic/core/shape.json
    -S ${MAS_DIR}/schemas/magnetic/core/material.json
    -S ${MAS_DIR}/schemas/magnetic/insulation/material.json
    -S ${MAS_DIR}/schemas/magnetic/insulation/wireCoating.json
    -S ${MAS_DIR}/schemas/magnetic/bobbin.json
    -S ${MAS_DIR}/schemas/magnetic/core/piece.json
    -S ${MAS_DIR}/schemas/magnetic/core/spacer.json
    -S ${MAS_DIR}/schemas/magnetic/wire/basicWire.json
    -S ${MAS_DIR}/schemas/magnetic/wire/round.json
    -S ${MAS_DIR}/schemas/magnetic/wire/rectangular.json
    -S ${MAS_DIR}/schemas/magnetic/wire/foil.json
    -S ${MAS_DIR}/schemas/magnetic/wire/planar.json
    -S ${MAS_DIR}/schemas/magnetic/wire/litz.json
    -S ${MAS_DIR}/schemas/magnetic/wire/material.json
    -S ${MAS_DIR}/schemas/magnetic/wire.json
    -S ${MAS_DIR}/schemas/utils.json
    -S ${MAS_DIR}/schemas/magnetic/insulation/wireCoating.json
    -S ${MAS_DIR}/schemas/magnetic/insulation/material.json
    -S ${MAS_DIR}/schemas/inputs.json
    -S ${MAS_DIR}/schemas/outputs.json
    -S ${MAS_DIR}/schemas/outputs/coreLossesOutput.json
    -S ${MAS_DIR}/schemas/inputs/designRequirements.json
    -S ${MAS_DIR}/schemas/inputs/operatingConditions.json
    -S ${MAS_DIR}/schemas/inputs/operatingPoint.json
    -S ${MAS_DIR}/schemas/inputs/operatingPointExcitation.json
    -S ${MAS_DIR}/schemas/inputs/topologies/flyback.json
    -S ${MAS_DIR}/schemas/inputs/topologies/currentTransformer.json
    -S ${MAS_DIR}/schemas/inputs/topologies/boost.json
    -S ${MAS_DIR}/schemas/inputs/topologies/buck.json
    -S ${MAS_DIR}/schemas/inputs/topologies/flybuck.json
    -S ${MAS_DIR}/schemas/inputs/topologies/forward.json
    -S ${MAS_DIR}/schemas/inputs/topologies/isolatedBuck.json
    -S ${MAS_DIR}/schemas/inputs/topologies/isolatedBuckBoost.json
    -S ${MAS_DIR}/schemas/inputs/topologies/pushPull.json
    -o ${MAS_DIRECTORY}/MAS.hpp --namespace MAS --source-style single-source --type-style pascal-case --member-style underscore-case --enumerator-style upper-underscore-case --no-boost
  USES_TERMINAL)

add_custom_target(PyMASGeneration
                  /bin/echo "RUNNING PyMASGeneration"
                  DEPENDS "${MAS_DIRECTORY}/MAS.hpp")

message(STATUS "Compiling PyOpenMagnetics with modular structure")
file(GLOB SOURCES src/*.cpp 
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/*.cpp
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/advisers/*.cpp
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/constructive_models/*.cpp
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/converter_models/*.cpp
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/physical_models/*.cpp
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/processors/*.cpp
    ${CMAKE_BINARY_DIR}/_deps/mkf-src/src/support/*.cpp
    )
message(STATUS SOURCES)
message(STATUS ${SOURCES})
pybind11_add_module(PyOpenMagnetics ${SOURCES})

add_dependencies(PyOpenMagnetics PyMASGeneration)

target_link_libraries(PyOpenMagnetics PUBLIC nlohmann_json::nlohmann_json matplot levmar rapidfuzz::rapidfuzz)

file(DOWNLOAD "https://raw.githubusercontent.com/vector-of-bool/cmrc/master/CMakeRC.cmake"
                 "${CMAKE_BINARY_DIR}/CMakeRC.cmake")
include("${CMAKE_BINARY_DIR}/CMakeRC.cmake")

include_directories("${CMAKE_BINARY_DIR}/_deps/mkf-src/")

cmrc_add_resource_library(insulation_standards ALIAS data::insulation_standards NAMESPACE insulationData WHENCE ${MKF_DIR}/ ${MKF_DIR}/src/data/insulation_standards/IEC_60664-1.json ${MKF_DIR}/src/data/insulation_standards/IEC_60664-4.json ${MKF_DIR}/src/data/insulation_standards/IEC_60664-5.json ${MKF_DIR}/src/data/insulation_standards/IEC_62368-1.json ${MKF_DIR}/src/data/insulation_standards/IEC_61558-1.json ${MKF_DIR}/src/data/insulation_standards/IEC_61558-2-16.json ${MKF_DIR}/src/data/insulation_standards/IEC_60335-1.json)
target_link_libraries(PyOpenMagnetics PUBLIC data::insulation_standards)


cmrc_add_resource_library(data ALIAS data::data NAMESPACE data WHENCE ${MAS_DIR} PREFIX MAS ${MAS_DIR}/data/core_materials.ndjson ${MAS_DIR}/data/core_shapes.ndjson ${MAS_DIR}/data/cores.ndjson ${MAS_DIR}/data/bobbins.ndjson ${MAS_DIR}/data/insulation_materials.ndjson ${MAS_DIR}/data/wire_materials.ndjson ${MAS_DIR}/data/wires.ndjson)
target_link_libraries(PyOpenMagnetics PUBLIC data::data)


include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/nlohmann/")
include_directories("${CMAKE_BINARY_DIR}/_deps/pybind11-src/include/")
include_directories("${CMAKE_BINARY_DIR}/_deps/pybind11_json-src/include/pybind11_json/")
include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/nlohmann/")
include_directories("${CMAKE_BINARY_DIR}/_deps/magic-enum-src/include")
include_directories("${CMAKE_BINARY_DIR}/_deps/svg-src/src")
include_directories("${CMAKE_BINARY_DIR}/_deps/spline-src/src")
include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/")
include_directories("${CMAKE_BINARY_DIR}/_deps/mkf-src/src/")
include_directories("${CMAKE_BINARY_DIR}/_cmrc/include")
include_directories("${MAS_DIRECTORY}")
include_directories("src/")

# target_link_libraries(PyOpenMagnetics PUBLIC MKF)



install(TARGETS PyOpenMagnetics LIBRARY DESTINATION .)