# coding: utf-8
#cython: embedsignature=True, c_string_encoding=ascii, language_level=3, freethreading_compatible = True

from libc.string cimport memcpy, strlen
from cpython.bool cimport PyBool_FromLong
from cpython.bytes cimport PyBytes_GET_SIZE, PyBytes_FromString
from cpython.bytearray cimport PyByteArray_Resize, PyByteArray_AS_STRING, PyByteArray_FromStringAndSize


# uchardet v0.0.8
cdef extern from "uchardet.h":
    ctypedef void* uchardet_t
    cdef uchardet_t uchardet_new()
    cdef void uchardet_delete(uchardet_t ud)
    cdef int uchardet_handle_data(uchardet_t ud, const char* data, size_t length)
    cdef void uchardet_data_end(uchardet_t ud)
    cdef void uchardet_reset(uchardet_t ud)
    cdef const char* uchardet_get_charset(uchardet_t ud)
    cdef float uchardet_get_confidence(uchardet_t ud, size_t i)
    # cdef const char* uchardet_get_encoding(uchardet_t ud, size_t i)
    # cdef const char* uchardet_get_language(uchardet_t ud, size_t i)

def detect_with_confidence(bytes msg):
    """same as detect but it returns back a tuple[encoding, confidence]"""
    cdef size_t length = <size_t>PyBytes_GET_SIZE(msg)

    cdef uchardet_t ud = uchardet_new()
    if ud == NULL:
        raise MemoryError

    if  uchardet_handle_data(ud, msg, length) == -1:
        uchardet_delete(ud)
        raise MemoryError

    uchardet_data_end(ud)

    cdef bytes detected_charset = PyBytes_FromString(uchardet_get_charset(ud))
    # cdef bytes detected_encoding = uchardet_get_encoding(ud, 0)
    # cdef const char* detected_language = uchardet_get_language(ud, 0)
    cdef float detected_confidence = uchardet_get_confidence(ud, 0)

    uchardet_reset(ud)
    uchardet_delete(ud)

    if detected_charset:
        return detected_charset, detected_confidence

    return None, None

cdef inline int set_to_bytearray(bytearray arr, const char* data) except -1:
    cdef Py_ssize_t data_size = <Py_ssize_t>strlen(data)
    cdef Py_ssize_t arr_size
    if not data_size:
        return 0

    if PyByteArray_Resize(arr, data_size) < 0:
        return -1
 
    memcpy(PyByteArray_AS_STRING(arr), data, data_size)
    return 0


cdef class UniversalDetector:
    """Detects character encodings from an input stream"""
    cdef:
        uchardet_t _ud
        bytearray _detected_charset
        float _detected_confidence
        bint _done
        bint _closed
    
    def __cinit__(self):
        self._ud = uchardet_new()
        if self._ud == NULL:
            raise MemoryError

        self._done = False
        self._closed = False
        # self._detected_encoding = b""
        # self._detected_language = b""

        # NOTE: these are internal so bytearrays should be acceptable here
        self._detected_charset = PyByteArray_FromStringAndSize(NULL, 0)
        self._detected_confidence = 0.0
    
    # Aggressive check incase of abrupt closure
    def __dealloc__(self):
        if not self._closed:
            self.close()

    def reset(self):
        if not self._closed:
            self._done = False
            self._closed = False
            # reset bytearray
            PyByteArray_Resize(self._detected_charset, 0)
            self._detected_confidence = 0.0
            uchardet_reset(self._ud)

    def feed(self, bytes msg):
        cdef Py_ssize_t length
        cdef int result

        if self._closed:
            return

        length = PyBytes_GET_SIZE(msg)
        if length > 0:
            result = uchardet_handle_data(self._ud, msg, <size_t>length)

            if result == -1:
                self._closed = True
                uchardet_delete(self._ud)
                raise MemoryError
            
            elif result == 0:
                self._done = True 

            if set_to_bytearray(self._detected_charset, uchardet_get_charset(self._ud)) < 0:
                # Throw the latest exception given from CPython
                raise
            
            # self._detected_encoding = uchardet_get_encoding(self._ud, 0)
            # self._detected_language = uchardet_get_language(self._ud, 0)
            self._detected_confidence = uchardet_get_confidence(self._ud, 0)

    cpdef object close(self):
        if not self._closed:
            uchardet_data_end(self._ud)

            if set_to_bytearray(self._detected_charset, uchardet_get_charset(self._ud)) < 0:
                raise 
            
            # self._detected_encoding = uchardet_get_encoding(self._ud, 0)
            # self._detected_language = uchardet_get_language(self._ud, 0)
            self._detected_confidence = uchardet_get_confidence(self._ud, 0)

            uchardet_delete(self._ud)
            self._closed = True

    @property
    def closed(self):
        """Determines if UniversalDetector was closed or not"""
        return PyBool_FromLong(self._closed)

    @property
    def done(self):
        """
        Determines if character detection is over returns True done, 
        false if otherwise
        """
        return PyBool_FromLong(self._done)

    @property
    def result(self):
        if PyBytes_GET_SIZE(self._detected_charset):
            return {
                "encoding": self._detected_charset.decode('utf-8', 'surrogateescape'), 
                "confidence": self._detected_confidence
            }
        else:
            return {
                "encoding": None,
                "confidence": None
            }

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        return self.close()
