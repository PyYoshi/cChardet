#ifndef charsetdetect_
#define charsetdetect_

#if defined(__GNUC__)
/* The classes below are exported */
#pragma GCC visibility push(default)
#endif // __GNUC__

#ifdef __cplusplus
extern "C" {
#endif

// Opaque type of character set detectors
typedef void* csd_t;
    
// Create a new character set detector. Must be freed by csd_close.
// If creation fails, returns (csd_t)-1.
csd_t csd_open(void);
// Feeds some more data to the character set detector. Returns 0 if it
// needs more data to come to a conclusion and a positive number if it has enough to say what
// the character set is. Returns a negative number if there is an error.
int csd_consider(csd_t csd, const char *data, int length);
// Closes the character set detector and returns the detected character set name as an ASCII string.
// Returns NULL if detection failed.
const char *csd_close(csd_t csd);

const char *csd_close2(csd_t csd,float *confidence);

#ifdef __cplusplus
}
#endif

#if defined(__GNUC__)
#pragma GCC visibility pop
#endif // __GNUC__

#endif
