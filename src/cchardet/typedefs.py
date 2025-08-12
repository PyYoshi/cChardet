from typing import Optional, TypedDict


class DecodeResultDict(TypedDict):
    """typehints dictionary values of the given results"""
    
    encoding: Optional[str]
    confidence: Optional[str]
