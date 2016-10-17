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

cdef class Detector:
    cdef csd_t csd
    cdef int _done
    cdef int _closed
    cdef float _confidence
    cdef const_char_ptr _detected_charset

    def __init__(self):
        self.csd = csd_open()
        self._done = 0
        self._closed = 0
        self._confidence = 0.0
        self._detected_charset = ''

    def feed(self, char *msg):
        cdef int length
        cdef int result

        if not self.done and not self._closed:
            length = strlen(msg)
            result = csd_consider(self.csd, msg, length)

            if result == -1: # Error, signal with a negative number
                raise Exception("Error, signal with a negative number")

            elif result == 1: # Need more data
                pass

            elif result == 0: # Detected early
                self._done = 1
                self.close()

    def close(self):
        if not self._closed:
            self._detected_charset = csd_close2(self.csd, &self._confidence)
            self._closed = 1

    @property
    def done(self):
        return bool(self._done)

    @property
    def result(self):
        if len(self._detected_charset):
            return self._detected_charset, self._confidence
        else:
            return None, None
