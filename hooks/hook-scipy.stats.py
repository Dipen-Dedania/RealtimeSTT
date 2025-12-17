# Hook for scipy.stats to fix PyInstaller bundling issues
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules
hiddenimports = collect_submodules('scipy.stats')

# Also ensure these specific modules are included
hiddenimports += [
    'scipy.stats._distn_infrastructure',
    'scipy.stats._continuous_distns',
    'scipy.stats._discrete_distns',
    'scipy.stats.distributions',
    'scipy.stats._stats_py',
]
