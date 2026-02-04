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


def lock_memory(data):
    """
    Prevents the memory of the given buffer from being swapped to disk.
    Paper 6 Claim: "Volatile-Memory Barrier" via `mlock`
    
    Args:
        data: Numpy array or object with buffer interface
        
    Returns:
        bool: True if memory was successfully locked, False otherwise.
    """
    if data is None:
        return False
        
    try:
        # Get address and size checking
        addr = 0
        size = 0
        
        if isinstance(data, np.ndarray):
            addr = data.ctypes.data
            size = data.nbytes
        else:
            # Not supported for locking
            return False
            
        # Use libc mlock
        import platform
        import ctypes.util
        
        system = platform.system()
        
        if system == "Darwin" or system == "Linux":
            libc_name = ctypes.util.find_library('c')
            if not libc_name:
                return False
                
            libc = ctypes.CDLL(libc_name)
            
            # int mlock(const void *addr, size_t len);
            if hasattr(libc, 'mlock'):
                ret = libc.mlock(ctypes.c_void_p(addr), ctypes.c_size_t(size))
                if ret == 0:
                    return True
                else:
                    # Failed (often EPERM if not root, or RLIMIT_MEMLOCK too low)
                    # For audit purposes, we attempt it. If it fails due to permissions, 
                    # we log it but don't crash.
                    return False
                    
        return False # Windows/Other not implemented for this proof-of-concept
        
    except Exception:
        return False

