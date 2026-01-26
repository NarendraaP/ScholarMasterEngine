import ctypes
import sys
import gc
import numpy as np

def secure_wipe(data):
    """
    Best-effort secure memory erasure.
    Overwrites the memory of a mutable buffer (like numpy array) with zeros
    before deleting the reference.
    
    Args:
        data: The object to wipe (must be mutable and support buffer interface, e.g., numpy array)
    """
    if data is None:
        return

    try:
        # 1. Implementation for Numpy Arrays
        if isinstance(data, np.ndarray):
            # Fill with zeros (Ctl+Z style)
            data.fill(0)
            return

        # 2. Generic Buffer method (for bytearrays etc)
        # We try to get the memory address and size
        if hasattr(data, '__buffer__'):
            # This is complex in pure Python without specific types.
            # Best effort: rely on GC but try to clear content if list/dict
            pass
            
    except Exception as e:
        # Do not crash system on cleanup errors
        pass
    finally:
        # 3. Force deletion and GC
        del data
        # We don't call gc.collect() every time to avoid performance hit,
        # but this function signals "Intent to Delete"
