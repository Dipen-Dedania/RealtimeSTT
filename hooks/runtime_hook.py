# Runtime hook to fix webrtcvad and numpy initialization issues
import sys
import os

# Suppress webrtcvad metadata warnings
try:
    import webrtcvad
except ImportError:
    pass

# Pre-import numpy modules to ensure proper initialization
try:
    import numpy
    import numpy.core
    import numpy.core.multiarray
    import numpy.core._multiarray_umath
except ImportError:
    pass
