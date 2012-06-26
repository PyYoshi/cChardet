# coding:utf8

cdef extern from "nscore.h":
    # base: https://github.com/kmshi/miro/blob/5d7cdd679830169590a677632cd88a2fa27f81f5/tv/windows/plat/frontends/widgets/XULRunnerBrowser/xulrunnerbrowser.pyx
    ctypedef PRUint32 nsresult
    ctypedef PRUint32 PRBool
    cdef enum:
        NS_OK = 0
    cdef PRUint32 NS_ERROR_OUT_OF_MEMORY = <nsresult>0x8007000eL