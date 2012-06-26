# Universal Character Set Detector (UCSD)

A library exposing a C interface and dependency-free interface to the Mozilla C++ UCSD library.

This library provides a highly accurate set of heuristics that attempt to determine the character set used to encode some input text.
This is extremely useful when your program has to handle an input file which is supplied without any encoding metadata.

Pulls together:

  * A NSPR emulation library (see `nspr-emu/README.md`)
  * Code written by Colin Snover to provide a command line interface to the library
  * The UCSD library itself from the Mozilla seamonkey source tree

The UCSD version provided is that present in the Mozilla public repo as of 31/10/2010.

## Building

We have a build system based on CMake, so you will need that installed. That done, simply do this incantation:

    ./configure
    make
    sudo make install

This will install the header file `charsetdetect.h` and the UCSD shared library, which you should link against in your compiler.

## API documentation

The library provides an opaque type of character set detectors:

    typedef void* csd_t;

The first thing a client should do is create one of these:

    csd_t csd_open(void);

A `csd_t` created in this fashion must be freed by `csd_close`. If creation fails, `csd_open` returns `(csd_t)-1`.

Now you need to feed some data to the detector:

    int csd_consider(csd_t csd, const char *data, int length);

The meaning of the return code is as follows:

  * Returns 0 if more data is needed to come to a conclusion
  * Returns a positive number if enough data has been received to detect the character set
  * Returns a negative number if there is an error

Finally, close the detector to find out what the character set is:

    const char *csd_close(csd_t csd);

The detected character set name is returned as an ASCII string. This function returns `NULL` if detection failed because there was not
enough data. It is safe to call `csd_close` at any point from creation by `csd_open` to the first call of `csd_close` on that character
set detector.

## Full example

This is a complete C program that shows how the library can be used to build a simple command-line character set detector:

    #include "charsetdetect.h"
    #include "stdio.h"

    #define BUFFER_SIZE 4096

    int main(int argc, const char * argv[]) {
        csd_t csd = csd_open();
        if (csd == (csd_t)-1) {
            printf("csd_open failed\n");
            return 1;
        }
    
        int size;
        char buf[BUFFER_SIZE] = {0};

        while ((size = fread(buf, 1, sizeof(buf), stdin)) != 0) {
            int result = csd_consider(csd, buf, size);
            if (result < 0) {
                printf("csd_consider failed\n");
                return 3;
            } else if (result > 0) {
                // Already have enough data
                break;
            }
        }
    
        const char *result = csd_close(csd);
        if (result == NULL) {
            printf("Unknown character set\n");
            return 2;
        } else {
            printf("%s\n", result);
            return 0;
        }
    }

You can compile it and try it (on platforms with GCC) as follows:

    gcc example.c -lcharsetdetect
    ./a.out < my_test_file.txt

## Known character sets

The list of possible character sets that can be returned from the library as of the most recent update are:

    Big5
    EUC-JP
    EUC-KR
    GB18030
    gb18030
    HZ-GB-2312
    IBM855
    IBM866
    ISO-2022-CN
    ISO-2022-JP
    ISO-2022-KR
    ISO-8859-2
    ISO-8859-5
    ISO-8859-7
    ISO-8859-8
    KOI8-R
    Shift_JIS
    TIS-620
    UTF-8
    UTF-16BE
    UTF-16LE
    UTF-32BE
    UTF-32LE
    windows-1250
    windows-1251
    windows-1252
    windows-1253
    windows-1255
    x-euc-tw
    X-ISO-10646-UCS-4-2143
    X-ISO-10646-UCS-4-3412
    x-mac-cyrillic

We believe this list to be exhaustive. Future updates to the UCSD library may add more alternatives, but we will endeavour to keep
this list current.

Notice that you may get both capitalisations of `GB18030`. For this reason (and to be future-proof against any future behaviour
like this for newly-added character sets) we recommend that you compare character set names case insensitively.

## Licensing

The files `libcharsetdetect.{cpp,h}` are (c) 2010 Colin Snover and released under an MIT license.

The UCSD is (c) mozilla.org and tri-licensed under MPL 1.1/GPL 2.0/LGPL 2.1.

We incorporate header files from the NSPR emulation library, which is LGPL licensed.

Thus the resulting artifact is LGPL licensed (I think).