import sys
from typing import Union

from .typedefs import DecodeResultDict

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


def detect_with_confidence(msg: bytes) -> Union[tuple[bytes, float], tuple[None, None]]:
    """same as detect but it returns back a tuple[encoding, confidence]
    
    Args:
        msg: A give string of bytes to detect
    
    Raises:
        MemoryError: If Internal handle could not be allocated
    """
    ...

class UniversalDetector:
    """Detects character encodings from an input stream"""
    def __init__(self) -> None:
        ...
    
    def reset(self) -> None:
        """
        Resets the universal detector allow it to handle a
        new stream of data
        """

    def feed(self, msg: bytes) -> None:
        """
        feeds a stream of characters for detection.

        Args:
            msg: a steam of data to pass through
        
        Raises:

            MemoryError: if memory to memory couldn't 
            be allocated during handling of the given data
        """
    
    def close(self) -> None:
        """Closes handle and frees internal memory"""
    
    @property
    def closed(self) -> bool:
        """Determines if UniversalDetector was closed or not"""
    
    @property
    def done(self) -> bool:
        """
        Determines if character detection has finished
        """
    
    @property
    def result(self) -> DecodeResultDict:
        """
        The Result of the given stream, 
        values will be None if stream is not 
        considered done or otherwise
        """
    
    def __enter__(self) -> Self:...
    def __exit__(self, *args) -> None:...
    


