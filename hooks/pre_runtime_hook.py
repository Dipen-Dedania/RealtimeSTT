# Pre-runtime hook to patch scipy before it loads
# This must run before scipy is imported
import sys

# Monkey-patch the scipy module loader to handle the 'obj' issue
def patch_scipy():
    """Patch scipy to work with PyInstaller"""
    try:
        # Import scipy._lib first to establish the module structure
        import scipy._lib
        
        # Now we can safely import the problematic module
        # The issue is in scipy.stats._distn_infrastructure where 'obj' 
        # is referenced before being defined due to PyInstaller's module loading order
        
        # Pre-import in the correct order
        import scipy.special
        import scipy.special._ufuncs
        import scipy.special._ufuncs_cxx
        
    except Exception as e:
        # If patching fails, continue anyway
        pass

# Apply the patch
patch_scipy()
