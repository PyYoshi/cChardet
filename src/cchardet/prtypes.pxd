# coding:utf8

cdef extern from "prtypes.h":
    ctypedef unsigned int PRUint32
    ctypedef int PRIntn
    ctypedef PRIntn PRBool
    cdef enum:
        PR_TRUE = 1
        PR_FALSE = 0