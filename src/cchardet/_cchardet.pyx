cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

cdef extern from "uchardet.h":
    ctypedef void* uchardet_t
    cdef uchardet_t uchardet_new()
    cdef void uchardet_delete(uchardet_t ud)
    cdef int uchardet_handle_data(uchardet_t ud, const_char_ptr data, int length)
    cdef void uchardet_data_end(uchardet_t ud)
    cdef void uchardet_reset(uchardet_t ud)
    cdef const_char_ptr uchardet_get_charset(uchardet_t ud)
    cdef float uchardet_get_confidence(uchardet_t ud)

def detect_with_confidence(const_char_ptr msg):
    cdef int length = len(msg)
    
    cdef uchardet_t ud = uchardet_new()

    cdef int result = uchardet_handle_data(ud, msg, length)
    if result != 0:
        uchardet_delete(ud)
        raise Exception("Handle data error")

    uchardet_data_end(ud)

    cdef bytes detected_charset = uchardet_get_charset(ud)
    cdef float detected_confidence = uchardet_get_confidence(ud)
    uchardet_delete(ud)

    if detected_charset:
        return detected_charset, detected_confidence

    return None, None
