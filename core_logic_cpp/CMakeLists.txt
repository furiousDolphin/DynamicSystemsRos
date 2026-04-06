cmake_minimum_required(VERSION 3.8)
project(core_logic_cpp)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


find_package(ament_cmake REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11_vendor REQUIRED)
find_package(pybind11 REQUIRED)
find_package(SDL2 REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Boost REQUIRED)


pybind11_add_module(module_uno 
    modules/module_uno.cpp 
    src/System.cpp
    src/ChebFunc.cpp
    src/ValueManager.cpp)

target_include_directories(module_uno PUBLIC
    ${PROJECT_SOURCE_DIR}/include
    ${SDL2_INCLUDE_DIRS}
    ${EIGEN3_INCLUDE_DIRS}
    ${Boost_INCLUDE_DIRS}
)

target_link_libraries(module_uno PUBLIC 
    ${SDL2_LIBRARIES}
    ${Boost_LIBRARIES}
    Eigen3::Eigen 
)

install(TARGETS module_uno
  DESTINATION lib/python3.10/site-packages
)

install(DIRECTORY scripts/
  DESTINATION lib/python3.10/site-packages
  FILES_MATCHING PATTERN "*.py"
)

#jakbym chcial zrobic apke na boku
# add_executable(DynamicSystemsApp main.cpp)

# target_include_directories(DynamicSystemsApp PUBLIC
#     ${PROJECT_SOURCE_DIR}/include
#     ${SDL2_INCLUDE_DIRS}
#     ${EIGEN3_INCLUDE_DIRS}
#     ${Boost_INCLUDE_DIRS}
# )

# target_link_libraries(DynamicSystemsApp PUBLIC 
#     ${SDL2_LIBRARIES}
#     ${Boost_LIBRARIES}
#     Eigen3::Eigen 
# )


# install(TARGETS DynamicSystemsApp
#   DESTINATION lib/${PROJECT_NAME}
# )

ament_package()
