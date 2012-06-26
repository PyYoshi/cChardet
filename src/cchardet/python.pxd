# coding:utf8

cdef extern from "Python.h":
    void * PyMem_Malloc(size_t)
    void PyMem_Free(void *)