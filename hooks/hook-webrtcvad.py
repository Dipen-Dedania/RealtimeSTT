# Custom hook for webrtcvad to fix metadata issue
from PyInstaller.utils.hooks import collect_dynamic_libs

# Just collect the binaries, skip metadata
binaries = collect_dynamic_libs('webrtcvad')
datas = []  # Skip metadata collection
hiddenimports = []
