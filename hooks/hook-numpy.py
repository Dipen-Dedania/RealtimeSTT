# PyInstaller hook for numpy to ensure all submodules are included
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all numpy submodules
hiddenimports = collect_submodules('numpy')

# Add specific numpy modules that might be missed
hiddenimports += [
    'numpy.core',
    'numpy.core.multiarray',
    'numpy.core._multiarray_umath',
    'numpy.random',
    'numpy.random._common',
    'numpy.random._bounded_integers',
    'numpy.random._mt19937',
    'numpy.random._pcg64',
    'numpy.random._philox',
    'numpy.random._sfc64',
    'numpy.random._generator',
]

# Collect numpy data files
datas = collect_data_files('numpy')
