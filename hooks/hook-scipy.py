# Custom hook for scipy to fix PyInstaller 'obj' is not defined error
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# This is a workaround for scipy 1.14+ and PyInstaller
# The issue is that scipy.stats._distn_infrastructure has a module-level
# reference to 'obj' that isn't defined when frozen

# Collect all scipy submodules
hiddenimports = collect_submodules('scipy')

# Ensure critical modules are loaded in the right order
hiddenimports_ordered = [
    'scipy._lib',
    'scipy._lib.messagestream',
    'scipy.special',
    'scipy.special._ufuncs',
    'scipy.special._ufuncs_cxx',
    'scipy.stats._constants',
    'scipy.stats._stats',
    'scipy.stats._distn_infrastructure',
    'scipy.stats._continuous_distns',
    'scipy.stats._discrete_distns',
]

hiddenimports = hiddenimports_ordered + [h for h in hiddenimports if h not in hiddenimports_ordered]

# Collect data files
datas = collect_data_files('scipy')
