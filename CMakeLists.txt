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
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)

    # set(CMAKE_BUILD_TYPE MinSizeRel)
    # set(CMAKE_BUILD_TYPE Release)
    set(CMAKE_BUILD_TYPE RelWithDebInfo)

    # Enable Link Time Optimization to reduce binary size
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION FALSE)  # TEMP: disable LTO (OOM)

    # Wheel/CI build: -O1 keeps compilation fast and low-memory. -g is
    # intentionally dropped — full debug info on the large pybind11 + json
    # translation units (converter.cpp is ~6k lines) balloons RAM during
    # compile and OOM-kills CI runners (exit 143). Frame pointers are kept
    # for usable backtraces. We REPLACE (not append) the flags so the -g in
    # the default RelWithDebInfo flags is stripped too. For local debugging
    # with symbols, re-add -g here.
    set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O1 -DNDEBUG -fno-omit-frame-pointer")
endif()

SET(MAS_DIRECTORY "${CMAKE_BINARY_DIR}/MAS/")
if(DEFINED ENV{LOCAL_MKF_DIR})
    SET(LOCAL_MKF_MAS TRUE)
    SET(MAS_DIR "${PROJECT_SOURCE_DIR}/_mas_local")
    SET(MKF_DIR "${PROJECT_SOURCE_DIR}/_mkf_local")
else()
    SET(LOCAL_MKF_MAS FALSE)
    SET(MAS_DIR "${CMAKE_BINARY_DIR}/_deps/mas-src")
    SET(MKF_DIR "${CMAKE_BINARY_DIR}/_deps/mkf-src")
endif()
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

FetchContent_Declare(rapidfuzz
  GIT_REPOSITORY https://github.com/rapidfuzz/rapidfuzz-cpp.git
  GIT_TAG main)
FetchContent_MakeAvailable(rapidfuzz)

message(STATUS "Fetching Eigen")
FetchContent_Declare(eigen
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG 3.4.0
  GIT_PROGRESS TRUE
  GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(eigen)
include_directories("${CMAKE_BINARY_DIR}/_deps/eigen-src")

if(NOT LOCAL_MKF_MAS)
    message(STATUS "Fetching MKF")
    # --------------------------------------------------------------------
    # MKF is PINNED to a SHA, NOT tracked to main (ABT #73).
    #
    # MKF main advanced past this commit to "delete converter_models + link
    # the Kirchhoff converter-model library (libKirchhoffApi.so)". This
    # vendored build compiles MKF by *globbing* its .cpp files straight into
    # the PyOpenMagnetics module (see file(GLOB SOURCES ...) below) — it does
    # NOT drive MKF's own CMakeLists, so it never builds or links
    # libKirchhoffApi.so. Kirchhoff and its AAS sibling are also UNPUBLISHED,
    # so a clean checkout cannot obtain the library at all. A from-scratch
    # build of newer main therefore fails to LINK: KirchhoffBridge.cpp and
    # WaveformProcessor reference symbols that now live in libKirchhoffApi.so.
    #
    # 2ae859dc is the last commit BEFORE that hard dependency — KirchhoffBridge
    # does not yet exist and MKF's Kirchhoff references are comments only, so
    # the globbed sources link self-contained. It is the exact commit the
    # currently-shipping vendored .so was built from (git rev-list 2ae859dc..main
    # == 9). To ADVANCE the pin you must first wire the Kirchhoff lib build into
    # THIS file (publish AAS/Kirchhoff, then add_subdirectory + link
    # libKirchhoffApi.so) — see ABT #73 option (b). Until then, bumping this to
    # a newer main breaks a clean rebuild.
    set(MKF_GIT_TAG "2ae859dcae6c3b2e5a128893247b7714360e863f"
        CACHE STRING "MKF git ref for the vendored PyOM build (pinned; see ABT #73)")
    # Force fresh clone by using a unique timestamp - update this when the pin changes
    set(MKF_FORCE_REFRESH "2026-07-01-pin-2ae859dc")
    # Tell MKF to disable matplotplusplus and use SVG-based Painter instead
    set(INCLUDE_PYMKF ON CACHE BOOL "Build Python interface" FORCE)
    # GIT_SUBMODULES_RECURSE pulls in CAS/PEAS (added 2026-04 alongside the
    # ExtraComponentsMode API). MAS is also a submodule of MKF but PyMKF
    # fetches it independently below for fast-update reasons; CAS/PEAS only
    # exist as MKF submodules, so we need them populated under MKF/.
    # NOTE: we cannot use GIT_SHALLOW with GIT_SUBMODULES — shallow clone
    # skips submodule init. Drop the shallow flag for MKF so CAS/PEAS/
    # cci_coords are actually checked out. cci_coords MUST stay in this
    # list — the CCI generator reads from MKF/cci_coords/coordinates/.
    # MAS is fetched separately below (not a sub-fetch of MKF here) so
    # leave it out, otherwise FetchContent doubles the clone.
    FetchContent_Declare(MKF
            GIT_REPOSITORY https://github.com/OpenMagnetics/MKF.git
            GIT_TAG ${MKF_GIT_TAG}
            GIT_PROGRESS TRUE
            GIT_SUBMODULES "CAS" "PEAS" "cci_coords"
            GIT_SUBMODULES_RECURSE TRUE)

    message(STATUS "Fetching mas")
    # Skip Git LFS to avoid bandwidth quota issues - data files are optional for build
    set(ENV{GIT_LFS_SKIP_SMUDGE} "1")
    # Force fresh clone by using a unique timestamp - update this when MAS changes
    set(MAS_FORCE_REFRESH "2025-02-26-01")
    FetchContent_Declare(
           mas
           GIT_REPOSITORY https://github.com/OpenMagnetics/MAS.git
           GIT_TAG main
           GIT_SHALLOW TRUE)

    message(STATUS "Fetching Properties mas")
    FetchContent_GetProperties(mas)
    message(STATUS "Fetching Properties MKF")
    FetchContent_GetProperties(MKF)
    message(STATUS "MAS_POPULATED: ${MAS_POPULATED}")
    message(STATUS "MKF_POPULATED: ${MKF_POPULATED}")

    # Always delete and repopulate MAS to ensure we get the latest
    if(EXISTS ${CMAKE_BINARY_DIR}/_deps/mas-src)
        message(STATUS "Removing old MAS source to force fresh clone")
        file(REMOVE_RECURSE ${CMAKE_BINARY_DIR}/_deps/mas-src)
    endif()
    message(STATUS "Populating MAS")
    FetchContent_Populate(mas)
    # Show git log to verify version
    execute_process(
        COMMAND git -C ${mas_SOURCE_DIR} log --oneline -1
        OUTPUT_VARIABLE MAS_GIT_LOG
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_VARIABLE MAS_GIT_ERROR
    )
    message(STATUS "MAS version: ${MAS_GIT_LOG}")
    if(MAS_GIT_ERROR)
        message(STATUS "MAS git error: ${MAS_GIT_ERROR}")
    endif()

    # Always delete and repopulate MKF so the checkout matches ${MKF_GIT_TAG}
    # exactly, mirroring the MAS refresh above. FetchContent will NOT re-checkout
    # an already-cloned source dir when the pin changes, so a persisted build dir
    # (incremental CI cache, or a local build that previously tracked main) would
    # otherwise keep a STALE MKF checkout at the wrong SHA — e.g. a main tip that
    # needs the unpublished libKirchhoffApi.so and fails to link (ABT #73).
    if(EXISTS ${CMAKE_BINARY_DIR}/_deps/mkf-src)
        message(STATUS "Removing old MKF source to force fresh checkout at ${MKF_GIT_TAG}")
        file(REMOVE_RECURSE ${CMAKE_BINARY_DIR}/_deps/mkf-src)
    endif()
    message(STATUS "Populating MKF")
    FetchContent_Populate(MKF)
    # Show git log AND assert the checkout is exactly the pinned SHA. A silent
    # drift here would resurface the libKirchhoffApi.so link failure ABT #73
    # guards against, so fail LOUDLY at configure time instead.
    execute_process(
        COMMAND git -C ${mkf_SOURCE_DIR} rev-parse HEAD
        OUTPUT_VARIABLE MKF_GIT_HEAD
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_VARIABLE MKF_GIT_ERROR
    )
    message(STATUS "MKF version: ${MKF_GIT_HEAD}")
    if(MKF_GIT_ERROR)
        message(STATUS "MKF git error: ${MKF_GIT_ERROR}")
    endif()
    # Only assert when the pin is a full 40-char SHA (a branch/tag ref can't be
    # compared to a resolved HEAD; that path is opt-in and the builder owns it).
    string(LENGTH "${MKF_GIT_TAG}" _mkf_pin_len)
    if(_mkf_pin_len EQUAL 40 AND NOT "${MKF_GIT_HEAD}" STREQUAL "${MKF_GIT_TAG}")
        message(FATAL_ERROR
            "Vendored PyOM built MKF at ${MKF_GIT_HEAD} but the pin is "
            "${MKF_GIT_TAG} (ABT #73). Delete ${CMAKE_BINARY_DIR}/_deps/mkf-src "
            "and reconfigure, or fetch the pinned commit.")
    endif()

    message(STATUS ${MAS_SOURCE_DIR})
else()
    message(STATUS "Using local MKF at ${MKF_DIR}")
    message(STATUS "Using local MAS at ${MAS_DIR}")
endif()

message(STATUS "Compiling MAS")


add_custom_command(
  OUTPUT "${MAS_DIRECTORY}/MAS.hpp"
  # Force regeneration by removing output first
  COMMAND ${CMAKE_COMMAND} -E remove -f ${MAS_DIRECTORY}/MAS.hpp
  COMMAND quicktype -l c++ -s schema ${MAS_DIR}/schemas/MAS.json
    # PEAS schemas: MAS main ($id https://psma.com/mas/...) now $refs shared
    # PEAS primitives (https://psma.com/peas/...). quicktype resolves those
    # external $refs by $id from sources passed with -S, so the PEAS schemas
    # must be fed in here. PEAS is an MKF submodule at ${MKF_DIR}/PEAS.
    -S ${MKF_DIR}/PEAS/schemas/utils.json
    -S ${MKF_DIR}/PEAS/schemas/inputs/operatingPointExcitation.json
    -S ${MKF_DIR}/PEAS/schemas/outputs/insulationCoordination.json
    # outputBase.json must precede/accompany lossElementPerHarmonic.json: the
    # latter's allOf[0] is {"$ref": "./outputBase.json"}. On Linux quicktype
    # resolves that relative ref off the file path, but on Windows the file-URI
    # resolution yields an empty URI ("Could not fetch schema") and the build
    # fails. Feeding outputBase.json as a source lets quicktype resolve it by
    # $id (https://psma.com/peas/outputs/outputBase.json) on every platform.
    -S ${MKF_DIR}/PEAS/schemas/outputs/outputBase.json
    -S ${MKF_DIR}/PEAS/schemas/outputs/lossElementPerHarmonic.json
    -S ${MAS_DIR}/schemas/magnetic.json
    -S ${MAS_DIR}/schemas/magnetic/core.json
    -S ${MAS_DIR}/schemas/magnetic/coil.json
    -S ${MAS_DIR}/schemas/utils.json
    -S ${MAS_DIR}/schemas/magnetic/core/gap.json
    -S ${MAS_DIR}/schemas/magnetic/core/shape.json
    -S ${MAS_DIR}/schemas/magnetic/core/material.json
    -S ${MAS_DIR}/schemas/magnetic/core/coating.json
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
    -S ${MAS_DIR}/schemas/inputs/topologies/forward.json
    -S ${MAS_DIR}/schemas/inputs/topologies/isolatedBuck.json
    -S ${MAS_DIR}/schemas/inputs/topologies/isolatedBuckBoost.json
    -S ${MAS_DIR}/schemas/inputs/topologies/pushPull.json
    -S ${MAS_DIR}/schemas/inputs/topologies/dualActiveBridge.json
    -S ${MAS_DIR}/schemas/inputs/topologies/llcResonant.json
    -S ${MAS_DIR}/schemas/inputs/topologies/cllcResonant.json
    -S ${MAS_DIR}/schemas/inputs/topologies/clllcResonant.json
    -S ${MAS_DIR}/schemas/inputs/topologies/phaseShiftedFullBridge.json
    -S ${MAS_DIR}/schemas/inputs/topologies/phaseShiftedHalfBridge.json
    -S ${MAS_DIR}/schemas/inputs/topologies/powerFactorCorrection.json
    -S ${MAS_DIR}/schemas/inputs/topologies/commonModeChoke.json
    -S ${MAS_DIR}/schemas/inputs/topologies/differentialModeChoke.json
    -S ${MAS_DIR}/schemas/inputs/topologies/asymmetricHalfBridge.json
    -S ${MAS_DIR}/schemas/inputs/topologies/cuk.json
    -S ${MAS_DIR}/schemas/inputs/topologies/sepic.json
    -S ${MAS_DIR}/schemas/inputs/topologies/zeta.json
    -S ${MAS_DIR}/schemas/inputs/topologies/weinberg.json
    -S ${MAS_DIR}/schemas/inputs/topologies/fourSwitchBuckBoost.json
    -S ${MAS_DIR}/schemas/inputs/topologies/seriesResonant.json
    -S ${MAS_DIR}/schemas/inputs/topologies/vienna.json
    -o ${MAS_DIRECTORY}/MAS.hpp --namespace MAS --source-style single-source --type-style pascal-case --member-style underscore-case --enumerator-style upper-underscore-case --no-boost
  USES_TERMINAL)

add_custom_target(PyMASGeneration
                  /bin/echo "RUNNING PyMASGeneration"
                  DEPENDS "${MAS_DIRECTORY}/MAS.hpp")

# ──────────────────────────────────────────────────────────────────
# CAS.hpp generation (mirrors MKF/CMakeLists.txt:419-451)
# CAS = Capacitor Adviser Schema. PEAS = Power Element Adviser Schema.
# Both are submodules of MKF (added 2026-04). MKF/Topology.h #includes
# <CAS.hpp> for the get_extra_components_inputs API; we must generate
# the header here so PyOpenMagnetics's TU sees it.
# ──────────────────────────────────────────────────────────────────
set(CAS_DIRECTORY "${CMAKE_BINARY_DIR}/CAS/")
set(CAS_DIR "${MKF_DIR}/CAS")
set(PEAS_DIR "${MKF_DIR}/PEAS")
file(MAKE_DIRECTORY "${CAS_DIRECTORY}")

add_custom_command(
  OUTPUT "${CAS_DIRECTORY}/CAS.hpp"
  COMMAND ${CMAKE_COMMAND} -E remove -f "${CAS_DIRECTORY}/CAS.hpp"
  COMMAND quicktype -l c++ -s schema ${CAS_DIR}/schemas/inputs.json
    -S ${CAS_DIR}/schemas/inputs/designRequirements.json
    -S ${PEAS_DIR}/schemas/utils.json
    -S ${PEAS_DIR}/schemas/inputs/twoTerminalOperatingPoint.json
    -S ${PEAS_DIR}/schemas/inputs/operatingConditions.json
    -S ${PEAS_DIR}/schemas/inputs/operatingPointExcitation.json
    -o ${CAS_DIRECTORY}/CAS.hpp --namespace CAS --source-style single-source
    --type-style pascal-case --member-style underscore-case
    --enumerator-style upper-underscore-case --no-boost
    --top-level Inputs
  DEPENDS
    "${CAS_DIR}/schemas/inputs.json"
    "${CAS_DIR}/schemas/inputs/designRequirements.json"
    "${PEAS_DIR}/schemas/utils.json"
    "${PEAS_DIR}/schemas/inputs/twoTerminalOperatingPoint.json"
    "${PEAS_DIR}/schemas/inputs/operatingConditions.json"
    "${PEAS_DIR}/schemas/inputs/operatingPointExcitation.json"
  USES_TERMINAL)

add_custom_target(PyCASGeneration
                  /bin/echo "RUNNING PyCASGeneration"
                  DEPENDS "${CAS_DIRECTORY}/CAS.hpp")
add_dependencies(PyCASGeneration PyMASGeneration)
include_directories("${CAS_DIRECTORY}")

message(STATUS "Compiling PyOpenMagnetics with modular structure")
file(GLOB SOURCES src/*.cpp
    ${MKF_DIR}/src/*.cpp
    ${MKF_DIR}/src/advisers/*.cpp
    ${MKF_DIR}/src/constructive_models/*.cpp
    ${MKF_DIR}/src/converter_models/*.cpp
    ${MKF_DIR}/src/physical_models/*.cpp
    ${MKF_DIR}/src/processors/*.cpp
    ${MKF_DIR}/src/support/*.cpp
    )

set(CCI_GENERATED_CPP "${CMAKE_BINARY_DIR}/generated/CciCoordinatesData.cpp")
find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_custom_command(
    OUTPUT "${CCI_GENERATED_CPP}"
    COMMAND "${Python3_EXECUTABLE}"
            "${MKF_DIR}/scripts/generate_cci_data.py"
            "${MKF_DIR}/cci_coords"
            "${CCI_GENERATED_CPP}"
    DEPENDS "${MKF_DIR}/scripts/generate_cci_data.py"
    COMMENT "Generating embedded CCI coordinates"
    VERBATIM)
add_custom_target(cci_data_gen DEPENDS "${CCI_GENERATED_CPP}")
list(APPEND SOURCES "${CCI_GENERATED_CPP}")

message(STATUS SOURCES)
message(STATUS ${SOURCES})
pybind11_add_module(PyOpenMagnetics ${SOURCES})

add_dependencies(PyOpenMagnetics PyMASGeneration PyCASGeneration cci_data_gen)

target_link_libraries(PyOpenMagnetics PUBLIC nlohmann_json::nlohmann_json levmar rapidfuzz::rapidfuzz)

file(DOWNLOAD "https://raw.githubusercontent.com/vector-of-bool/cmrc/master/CMakeRC.cmake"
                 "${CMAKE_BINARY_DIR}/CMakeRC.cmake")
include("${CMAKE_BINARY_DIR}/CMakeRC.cmake")

include_directories("${MKF_DIR}/")

cmrc_add_resource_library(insulation_standards ALIAS data::insulation_standards NAMESPACE insulationData WHENCE ${MKF_DIR}/ ${MKF_DIR}/src/data/insulation_standards/IEC_60664-1.json ${MKF_DIR}/src/data/insulation_standards/IEC_60664-4.json ${MKF_DIR}/src/data/insulation_standards/IEC_60664-5.json ${MKF_DIR}/src/data/insulation_standards/IEC_62368-1.json ${MKF_DIR}/src/data/insulation_standards/IEC_61558-1.json ${MKF_DIR}/src/data/insulation_standards/IEC_61558-2-16.json ${MKF_DIR}/src/data/insulation_standards/IEC_60335-1.json)
target_link_libraries(PyOpenMagnetics PUBLIC data::insulation_standards)


# Only embed essential data files to reduce binary size
# Skip large optional datasets like cores_stock.ndjson
cmrc_add_resource_library(data ALIAS data::data NAMESPACE data WHENCE ${MAS_DIR} PREFIX MAS 
    ${MAS_DIR}/data/core_materials.ndjson 
    ${MAS_DIR}/data/core_shapes.ndjson 
    ${MAS_DIR}/data/cores.ndjson 
    ${MAS_DIR}/data/bobbins.ndjson 
    ${MAS_DIR}/data/insulation_materials.ndjson 
    ${MAS_DIR}/data/wire_materials.ndjson 
    ${MAS_DIR}/data/wires.ndjson)
target_link_libraries(PyOpenMagnetics PUBLIC data::data)

cmrc_add_resource_library(core_losses_data ALIAS data::core_losses_data NAMESPACE coreLossesData ${MKF_DIR}/src/data/core_losses/ciGSE_coefficients.json)
target_link_libraries(PyOpenMagnetics PUBLIC data::core_losses_data)

include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/nlohmann/")
include_directories("${CMAKE_BINARY_DIR}/_deps/pybind11-src/include/")
include_directories("${CMAKE_BINARY_DIR}/_deps/pybind11_json-src/include/pybind11_json/")
include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/nlohmann/")
include_directories("${CMAKE_BINARY_DIR}/_deps/magic-enum-src/include")
include_directories("${CMAKE_BINARY_DIR}/_deps/svg-src/src")
include_directories("${CMAKE_BINARY_DIR}/_deps/spline-src/src")
include_directories("${CMAKE_BINARY_DIR}/_deps/json-src/include/")
include_directories("${MKF_DIR}/src/")
include_directories("${MKF_DIR}/src/advisers/")
include_directories("${MKF_DIR}/src/constructive_models/")
include_directories("${MKF_DIR}/src/converter_models/")
include_directories("${MKF_DIR}/src/physical_models/")
include_directories("${MKF_DIR}/src/processors/")
include_directories("${MKF_DIR}/src/support/")
include_directories("${CMAKE_BINARY_DIR}/_deps/eigen-src")
include_directories("${CMAKE_BINARY_DIR}/_cmrc/include")
include_directories("${MAS_DIRECTORY}")
include_directories("src/")

# target_link_libraries(PyOpenMagnetics PUBLIC MKF)



install(TARGETS PyOpenMagnetics LIBRARY DESTINATION .)

# Install the package __init__.py so `import PyOpenMagnetics` exposes the
# compiled extension's API. Without it the wheel installs as an empty PEP-420
# namespace package and `PyOpenMagnetics.<fn>` resolves to nothing.
install(FILES __init__.py DESTINATION .)

# Install documentation files for AI assistants
install(FILES AGENTS.md llms.txt PyOpenMagnetics.pyi DESTINATION .)