INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_EQUISAT_DECODER equisat_decoder)

FIND_PATH(
    EQUISAT_DECODER_INCLUDE_DIRS
    NAMES equisat_decoder/api.h
    HINTS $ENV{EQUISAT_DECODER_DIR}/include
        ${PC_EQUISAT_DECODER_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    EQUISAT_DECODER_LIBRARIES
    NAMES gnuradio-equisat_decoder
    HINTS $ENV{EQUISAT_DECODER_DIR}/lib
        ${PC_EQUISAT_DECODER_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/equisat_decoderTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(EQUISAT_DECODER DEFAULT_MSG EQUISAT_DECODER_LIBRARIES EQUISAT_DECODER_INCLUDE_DIRS)
MARK_AS_ADVANCED(EQUISAT_DECODER_LIBRARIES EQUISAT_DECODER_INCLUDE_DIRS)
