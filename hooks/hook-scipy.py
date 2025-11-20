# PyInstaller hook for scipy to fix initialization issues
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# Collect all scipy submodules - this is important for proper initialization
hiddenimports = collect_submodules('scipy')

# Explicitly add critical scipy modules in initialization order
hiddenimports += [
    # Core scipy
    'scipy._lib',
    'scipy._lib.messagestream',
    'scipy._lib._ccallback',

    # Special functions (needed by stats)
    'scipy.special',
    'scipy.special._ufuncs',
    'scipy.special._ufuncs_cxx',
    'scipy.special.cython_special',

    # Stats modules in proper order
    'scipy.stats._distn_infrastructure',
    'scipy.stats._continuous_distns',
    'scipy.stats._discrete_distns',
    'scipy.stats.distributions',
    'scipy.stats._stats_py',
    'scipy.stats',

    # Signal processing
    'scipy.signal',
    'scipy.signal._peak_finding',
    'scipy.signal._spectral_py',

    # Other commonly used modules
    'scipy.integrate',
    'scipy.interpolate',
    'scipy.linalg',
    'scipy.linalg.blas',
    'scipy.linalg.lapack',
]

# Collect scipy data files and binaries
datas = collect_data_files('scipy', include_py_files=True)
binaries = collect_dynamic_libs('scipy')
