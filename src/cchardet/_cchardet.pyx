# coding: utf-8
#cython: embedsignature=True, c_string_encoding=ascii, language_level=3
#cython: freethreading_compatible=True

cimport cython
from libc.stddef cimport size_t

cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

# uchardet v0.0.8
cdef extern from "uchardet.h":
    ctypedef void* uchardet_t
    cdef uchardet_t uchardet_new() except + nogil
    cdef void uchardet_delete(uchardet_t ud) noexcept nogil
    cdef int uchardet_handle_data(uchardet_t ud, const_char_ptr data, size_t length) except + nogil
    cdef void uchardet_data_end(uchardet_t ud) except + nogil
    cdef void uchardet_reset(uchardet_t ud) except + nogil
    cdef int uchardet_is_done(uchardet_t ud) noexcept nogil
    cdef const_char_ptr uchardet_get_charset(uchardet_t ud)
    cdef size_t uchardet_get_n_candidates(uchardet_t ud)
    cdef float uchardet_get_confidence(uchardet_t ud, size_t i)
    cdef const_char_ptr uchardet_get_encoding(uchardet_t ud, size_t i)
    cdef const_char_ptr uchardet_get_language(uchardet_t ud, size_t i)
    cdef void uchardet_weigh_language(
        uchardet_t ud, const_char_ptr language, float weight
    ) except +


cdef int _handle_data(uchardet_t ud, const_char_ptr data, size_t length) except -1 nogil:
    """Feed buffers without overflowing uchardet's internal 32-bit length."""
    cdef size_t offset = 0
    cdef size_t chunk_length
    cdef size_t max_chunk_length = 0xffffffff
    cdef int result

    while offset < length:
        chunk_length = length - offset
        if chunk_length > max_chunk_length:
            chunk_length = max_chunk_length
        result = uchardet_handle_data(ud, data + offset, chunk_length)
        if result != 0:
            return result
        offset += chunk_length
    return 0


cdef list _language_weight_pairs(object language_weights):
    """Convert the weights to (bytes, float) pairs before touching a detector."""
    cdef list pairs = []
    cdef float weight

    if language_weights is None:
        return pairs
    for language_name, language_weight in language_weights.items():
        weight = language_weight
        pairs.append((language_name.encode("ascii"), weight))
    return pairs


cdef int _weigh_languages(uchardet_t ud, list pairs) except -1:
    cdef bytes language
    cdef float weight

    for language, weight in pairs:
        uchardet_weigh_language(ud, language, weight)
    return 0


cdef int _apply_language_weights(uchardet_t ud, object language_weights) except -1:
    return _weigh_languages(ud, _language_weight_pairs(language_weights))

def detect_with_details(bytes msg, max_bytes=None, language_weights=None):
    cdef size_t length = len(msg)
    cdef Py_ssize_t limit
    if max_bytes is not None:
        limit = max_bytes
        if limit < 0:
            raise ValueError("max_bytes must be non-negative")
        if limit < <Py_ssize_t>length:
            length = <size_t>limit
    cdef const_char_ptr data = msg

    cdef uchardet_t ud
    cdef int result
    cdef bytes detected_charset
    cdef const_char_ptr detected_language_ptr
    cdef bytes detected_language = b""
    cdef float detected_confidence
    ud = NULL
    try:
        with nogil:
            ud = uchardet_new()
        _apply_language_weights(ud, language_weights)
        with nogil:
            result = _handle_data(ud, data, length)
        if result != 0:
            raise RuntimeError("uchardet failed to handle data")

        with nogil:
            uchardet_data_end(ud)

        detected_charset = uchardet_get_encoding(ud, 0)
        detected_language_ptr = uchardet_get_language(ud, 0)
        detected_confidence = uchardet_get_confidence(ud, 0)
        if detected_language_ptr != NULL:
            detected_language = detected_language_ptr

        if detected_charset:
            return detected_charset, detected_language or None, detected_confidence
        return None, None, None
    finally:
        if ud != NULL:
            with nogil:
                uchardet_delete(ud)

def detect_with_confidence(bytes msg, max_bytes=None, language_weights=None):
    encoding, _, confidence = detect_with_details(msg, max_bytes, language_weights)
    return encoding, confidence

def detect_all(bytes msg, max_bytes=None, language_weights=None):
    cdef size_t length = len(msg)
    cdef Py_ssize_t limit
    if max_bytes is not None:
        limit = max_bytes
        if limit < 0:
            raise ValueError("max_bytes must be non-negative")
        if limit < <Py_ssize_t>length:
            length = <size_t>limit
    cdef const_char_ptr data = msg
    cdef uchardet_t ud
    cdef int result
    cdef size_t candidate
    cdef size_t candidate_count
    cdef const_char_ptr encoding_ptr
    cdef const_char_ptr language_ptr
    cdef bytes encoding
    cdef bytes language
    cdef list candidates = []

    ud = NULL
    try:
        with nogil:
            ud = uchardet_new()
        _apply_language_weights(ud, language_weights)
        with nogil:
            result = _handle_data(ud, data, length)
        if result != 0:
            raise RuntimeError("uchardet failed to handle data")
        with nogil:
            uchardet_data_end(ud)

        candidate_count = uchardet_get_n_candidates(ud)
        for candidate in range(candidate_count):
            encoding_ptr = uchardet_get_encoding(ud, candidate)
            language_ptr = uchardet_get_language(ud, candidate)
            encoding = encoding_ptr
            language = language_ptr if language_ptr != NULL else b""
            candidates.append(
                (encoding, language or None, uchardet_get_confidence(ud, candidate))
            )
        return candidates
    finally:
        if ud != NULL:
            with nogil:
                uchardet_delete(ud)

cdef class UniversalDetector:
    # uchardet runs without the GIL, so concurrent calls on one detector could
    # otherwise corrupt its native state even on regular builds. The lock
    # serializes every method; acquiring it releases the GIL while waiting.
    # It is not reentrant: methods must not call each other while holding it,
    # and no Python code that could reach this detector (user mappings,
    # finalizers run by a collection) may run under it. So Python objects are
    # converted or built outside the lock wherever the normal path needs them.
    cdef cython.pymutex _lock
    cdef uchardet_t _ud
    cdef int _done
    cdef int _closed
    cdef bytes _detected_charset
    cdef bytes _detected_language
    cdef float _detected_confidence

    def __cinit__(self):
        self._ud = uchardet_new()

    def __init__(self, language_weights=None):
        cdef list weights = _language_weight_pairs(language_weights)
        with self._lock:
            self._done = 0
            self._closed = 0
            self._detected_charset = b""
            self._detected_language = b""
            self._detected_confidence = 0.0
            _weigh_languages(self._ud, weights)

    def reset(self):
        with self._lock:
            self._done = 0
            self._closed = 0
            self._detected_charset = b""
            self._detected_language = b""
            self._detected_confidence = 0.0
            with nogil:
                uchardet_reset(self._ud)

    def feed(self, bytes msg):
        cdef size_t length
        cdef int result = 0
        cdef const_char_ptr data

        with self._lock:
            if self._closed:
                return

            length = len(msg)
            if length > 0:
                data = msg
                with nogil:
                    result = _handle_data(self._ud, data, length)

                if result != 0:
                    self._closed = 1
                elif uchardet_is_done(self._ud):
                    self._close_locked()
        if result != 0:
            raise RuntimeError("uchardet failed to handle data")

    def close(self):
        with self._lock:
            self._close_locked()

    @cython.final
    cdef int _close_locked(self) except -1:
        cdef const_char_ptr language_ptr
        if self._closed:
            return 0
        with nogil:
            uchardet_data_end(self._ud)

        self._detected_charset = uchardet_get_encoding(self._ud, 0)
        language_ptr = uchardet_get_language(self._ud, 0)
        if language_ptr != NULL:
            self._detected_language = language_ptr
        self._detected_confidence = uchardet_get_confidence(self._ud, 0)

        self._done = 1
        self._closed = 1
        return 0

    def __dealloc__(self):
        if self._ud != NULL:
            uchardet_delete(self._ud)

    @property
    def done(self):
        cdef int done
        with self._lock:
            done = self._done
        return bool(done)

    @property
    def result(self):
        cdef bytes charset
        cdef bytes language
        cdef float confidence
        with self._lock:
            charset = self._detected_charset
            language = self._detected_language
            confidence = self._detected_confidence
        if len(charset):
            return charset, language or None, confidence
        return None, None, None
