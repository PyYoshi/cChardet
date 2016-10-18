cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

cdef extern from "charsetdetect.h":
    ctypedef void* csd_t
    cdef csd_t csd_open()
    cdef int csd_consider(csd_t csd, char* data, int length)
    cdef const_char_ptr csd_close2(csd_t csd, float *confidence)

def detect_with_confidence(char *msg):
    cdef csd_t csd = csd_open()

    # すでにカウント済みの長さへアクセス
    # strlenでは再度カウントすることになる
    # https://github.com/python/cpython/blob/c30098c8c6014f3340a369a31df9c74bdbacc269/Include/bytesobject.h#L82
    # https://github.com/python/cpython/blob/c30098c8c6014f3340a369a31df9c74bdbacc269/Objects/bytesobject.c#L2490
    # https://github.com/python/cpython/blob/c30098c8c6014f3340a369a31df9c74bdbacc269/Include/object.h#L346
    # https://github.com/python/cpython/blob/c30098c8c6014f3340a369a31df9c74bdbacc269/Objects/bytesobject.c#L2410
    cdef int length = len(msg)

    cdef int result = csd_consider(csd, msg, length)
    cdef float confidence = 0.0
    cdef const_char_ptr detected_charset

    if result == 1: # Need more data
        detected_charset = csd_close2(csd, &confidence)
    elif result == 0: # Detected early
        detected_charset = csd_close2(csd, &confidence)
    else: # Error, signal with a negative number
        raise Exception("Error, signal with a negative number")

    if detected_charset:
        return detected_charset, confidence
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
            length = len(msg)
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
        return None, None
