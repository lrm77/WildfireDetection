#Version-------------------------------------------------------------------------------------------------------------------#

#Sources-------------------------------------------------------------------------------------------------------------------#

set(SOURCES 
	src/calibration.cpp
	src/ThermalCamera.cpp
)

#Project../core/-------------------------------------------------------------------------------------------------------------------#

project(capture DESCRIPTION "Seekware Camera Display and Capture")

#Targets-------------------------------------------------------------------------------------------------------------------#

add_executable(${PROJECT_NAME} ${SOURCES})
if(MSVC)
	set_property(GLOBAL PROPERTY VS_STARTUP_PROJECT calibration)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES INSTALL_RPATH ../../lib/${TOOLCHAIN_DIR})


#Extra Compile Options------------------------------------------------------------------------------------------------------#

#Include--------------------------------------------------------------------------------------------------------------------#

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

if (SDL2_FOUND)
  include_directories(${SDL2_EXEC_PREFIX}/include)
endif (SDL2_FOUND)

#Link------------------------------------------------------------------------------------------------------------------------#

#SDL2
target_link_libraries(${PROJECT_NAME} SDL2)

if(SDL2_FOUND)
	target_link_libraries(${PROJECT_NAME} ${SDL2_LIBRARIES})
endif()

#find_package(SDL2_ttf REQUIRED)
target_link_libraries(${PROJECT_NAME} SDL2_ttf)

#seekware
target_link_libraries(${PROJECT_NAME} seekware)

#OpenCV
find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )
target_link_libraries( ${PROJECT_NAME} ${OpenCV_LIBS} )

#pthread
target_link_libraries(${PROJECT_NAME} pthread)

#Runtime Dependencies--------------------------------------------------------------------------------------------------------#
if(MSVC)
	add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
		COMMAND ${CMAKE_COMMAND} -E copy_if_different
		$<TARGET_FILE_DIR:seekware>/seekware.dll
		$<TARGET_FILE_DIR:${PROJECT_NAME}>/seekware.dll
	)
	add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
		COMMAND ${CMAKE_COMMAND} -E copy_if_different
		$<TARGET_FILE_DIR:SDL2>/SDL2.dll
		$<TARGET_FILE_DIR:${PROJECT_NAME}>/SDL2.dll
	)
endif()

#Install---------------------------------------------------------------------------------------------------------------------#

install(TARGETS ${PROJECT_NAME} DESTINATION bin)

file(GLOB SRC ${CMAKE_CURRENT_LIST_DIR}/src/*)
install(FILES ${SRC} DESTINATION src/${PROJECT_NAME}/src)

file(GLOB INC ${CMAKE_CURRENT_LIST_DIR}/include/*)
install(FILES ${INC} DESTINATION src/${PROJECT_NAME}/include)

install(FILES ${CMAKE_CURRENT_LIST_DIR}/Makefile DESTINATION src/${PROJECT_NAME})
