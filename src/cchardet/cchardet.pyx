cimport cython
from libc.stdlib cimport malloc, free
import warnings

cdef extern from "Python.h":
    void * PyMem_Malloc(size_t)
    void PyMem_Free(void *)

cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

cdef extern from "string.h":
    cdef int strlen(char *s)

cdef extern from "charsetdetect.h":
    ctypedef void* csd_t
    cdef csd_t csd_open()
    cdef int csd_consider(csd_t csd, char* data, int length)
    cdef const_char_ptr csd_close(csd_t csd)
    cdef const_char_ptr csd_close2(csd_t csd, float *confidence)

def detect(char *msg):
    cdef csd_t csd = csd_open()
    cdef int length = strlen(msg)
    cdef int result = csd_consider(csd, msg, length)
    # ref: charsetdetect.cpp
    if result == -1: # Error, signal with a negative number
        raise Exception("Error, signal with a negative number")
    elif result == 1: # Need more data
        warnings.warn("Need more data",UserWarning)
        return csd_close(csd)
    elif result == 0: # Detected early
        return csd_close(csd)

def detect_with_confidence(char *msg):
    # TODO: fix "sometimes, to output invalid confidence value" bug.
    cdef csd_t csd = csd_open()
    cdef int length = strlen(msg)
    cdef int result = csd_consider(csd, msg, length)
    cdef float confidence
    cdef const_char_ptr detected_charset
    # ref: charsetdetect.cpp
    if result == -1: # Error, signal with a negative number
        raise Exception("Error, signal with a negative number")
    elif result == 1: # Need more data
        warnings.warn("Need more data",UserWarning)
        detected_charset = csd_close2(csd, &confidence)
        ret = {
            "encoding":detected_charset,
            "confidence":confidence
        }
        return ret
    elif result == 0: # Detected early
        detected_charset = csd_close2(csd, &confidence)
        ret = {
            "encoding":detected_charset,
            "confidence":confidence
        }
        return ret

