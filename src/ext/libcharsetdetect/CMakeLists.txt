CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

#IF("${CMAKE_SYSTEM_PROCESSOR}" STREQUAL "x86_64")
	SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -std=c++0x" )
#ENDIF("${CMAKE_SYSTEM_PROCESSOR}" STREQUAL "x86_64")

# Add a distclean target to the generated makefile
IF (UNIX)
  ADD_CUSTOM_TARGET (distclean @echo cleaning for source distribution)
  SET(DISTCLEANED
   cmake.depends
   cmake.check_depends
   CMakeCache.txt
   cmake.check_cache
   *.cmake
   Makefile
   core core.*
   gmon.out
   *~
  )
  
  ADD_CUSTOM_COMMAND(
    DEPENDS clean
    COMMENT "distribution clean"
    COMMAND rm
    ARGS    -Rf CMakeTmp ${DISTCLEANED}
    TARGET  distclean
  )
ENDIF(UNIX)


PROJECT(charsetdetect)

INCLUDE_DIRECTORIES(. nspr-emu mozilla/extensions/universalchardet/src/base/)

FILE(GLOB charsetdetect_lib_src mozilla/extensions/universalchardet/src/base/*.cpp)
SET(charsetdetect_lib_src ${charsetdetect_lib_src} charsetdetect.cpp)
ADD_LIBRARY(charsetdetect ${charsetdetect_lib_src})

# Do not output the shared library into the root
SET(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/build)

INSTALL (TARGETS charsetdetect DESTINATION lib)
INSTALL (FILES charsetdetect.h DESTINATION include)
