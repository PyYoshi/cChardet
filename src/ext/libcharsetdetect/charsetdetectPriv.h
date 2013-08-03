/* The classes below are not exported */

#include <stdio.h>
#include <stdlib.h>
#include "nscore.h"
#include "nsUniversalDetector.h"

class Detector : public nsUniversalDetector {
public:
	Detector(PRUint32 aLanguageFilter) : nsUniversalDetector(aLanguageFilter) {};
    int Consider(const char *data, int length);
    const char *Close(void);

    const char *Close2(float *confidence);
protected:
	void Report(const char* aCharset);
    const char *mDetectedCharset;
};

