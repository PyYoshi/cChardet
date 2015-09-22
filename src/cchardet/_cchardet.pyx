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
        ret = csd_close(csd)
    elif result == 0: # Detected early
        ret = csd_close(csd)
    if ret:
        return ret

def detect_with_confidence(char *msg):
    cdef csd_t csd = csd_open()
    cdef int length = strlen(msg)
    cdef int result = csd_consider(csd, msg, length)
    cdef float confidence = 0.0
    cdef const_char_ptr detected_charset
    # ref: charsetdetect.cpp
    if result == 1: # Need more data
        detected_charset = csd_close2(csd, &confidence)
    elif result == 0: # Detected early
        detected_charset = csd_close2(csd, &confidence)
    else: # Error, signal with a negative number
        raise Exception("Error, signal with a negative number")
    if detected_charset:
        return detected_charset, confidence
    else:
        return None, None
