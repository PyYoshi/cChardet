# coding:utf8

from libc.stdlib cimport malloc, free

cimport prtypes, src.cchardet.nscore

cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

cdef extern from "nsUniversalDetector.h":
    cdef cppclass nsCharSetProber
    cdef enum:
        NUM_OF_CHARSET_PROBERS = 3
    cdef enum nsInputState:
        ePureAscii = 0
        eEscAscii = 1
        eHighbyte = 2

    cdef unsigned int NS_FILTER_CHINESE_SIMPLIFIED = 0x01
    cdef unsigned int NS_FILTER_CHINESE_TRADITIONAL = 0x02
    cdef unsigned int NS_FILTER_JAPANESE = 0x04
    cdef unsigned int NS_FILTER_KOREAN = 0x08
    cdef unsigned int NS_FILTER_NON_CJK = 0x10
    cdef unsigned int NS_FILTER_ALL = 0x1F
    cdef unsigned int NS_FILTER_CHINESE = NS_FILTER_CHINESE_SIMPLIFIED | NS_FILTER_CHINESE_TRADITIONAL | NS_FILTER_JAPANESE | NS_FILTER_KOREAN

    cdef class nsUniversalDetector:
        cdef nsUniversalDetector(self, PRUint32 aLanguageFilter)
        cdef nsresult HandleData(self, const_char_ptr aBuf, PRUint32 aLen)
        cdef void DataEnd(self,)

        cdef void _Report(self,const_char_ptr aCharset)
        cdef void _Reset(self)
        cdef nsInputState _mInputState
        cdef PRBool _mDone
        cdef PRBool _mInTag
        cdef PRBool _mStart
        cdef PRBool _mGotData
        cdef char _mLastChar
        cdef const_char_ptr _mDetectedCharset
        cdef PRUInt32 _mBestGuess
        cdef PRUint32 _mLanguageFilter

        cdef nsCharSetProber *_mCharsetProber[NUM_OF_CHARSET_PROBERS]
        cdef nsCharSetProber *_mEscCharSetProber

"""
cdef extern from *:
    cdef class Detector(nsUniversalDetector):
        cdef Detector(self, PRUint32 aLanguageFilter):
            nsUniversalDetector(self, aLanguageFilter)
        cdef int Consider(self, const_char_ptr data, int length)
        cdef const_char_ptr Close(self, )

        cdef void _Report(self, const_char_ptr aCharset)
        cdef const_char_ptr *_mDetectedCharset"""

cdef class Detector(nsUniversalDetector):
    cdef Detector(self, PRUint32 aLanguageFilter):
        nsUniversalDetector(self, aLanguageFilter)

    cdef void Report(self, const_char_ptr aCharset):
        self._mDone = PR_TRUE
        self._mDetectedCharset = aCharset

    cdef int Consider(self, const_char_ptr data, int length):
        if HandleData(data,length) == NS_ERROR_OUT_OF_MEMORY:
            # Error, signal with a negative number
            return -1

        if self._mDone:
            # Detected early
            return 0

        # Need more data!
        return 1

    cdef const_char_ptr Close(self):
        self.DataEnd()

        if not self._mDone:
            if self._mInputState == eEscAscii:
                return "ibm850"
            elif self._mInputState == ePureAscii:
                return "ASCII"

            return None

        return self._mDetectedCharset

cdef extern from *:
    ctypedef void* csd_t
    cdef csd_t csd_open()
    cdef int csd_consider(csd_t csd, char* data, int length)
    cdef const_char_ptr csd_close(csd_t csd)

cdef csd_t csd_open():
    # TODO: capture exceptions thrown by "new" and return -1 in that case
    # TODO: provide C-land with access to the language filter constructor argument
    return Detector(NS_FILTER_ALL)

cdef int csd_consider(csd_t csd, const_char_ptr data, int length):
    # return ((Detector*)csd)->Consider(data, length);
    return <Detector*>csd.Consider(data, length)

cdef const_char_ptr csd_close(csd_t csd):
    cdef const_char_ptr result = <Detector*>csd.Close()
    del <Detector*>csd
    return result