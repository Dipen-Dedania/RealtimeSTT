"""
Script to patch scipy for PyInstaller + Python 3.12 compatibility
This fixes the 'NameError: name obj is not defined' issue
"""
import os
import shutil
import sys

def patch_scipy():
    """Patch scipy.stats._distn_infrastructure for Python 3.12 + PyInstaller"""
    try:
        import scipy.stats
        scipy_stats_path = os.path.dirname(scipy.stats.__file__)
        target_file = os.path.join(scipy_stats_path, '_distn_infrastructure.py')
        backup_file = target_file + '.backup'
        
        # Create backup if it doesn't exist
        if not os.path.exists(backup_file):
            print(f"Creating backup: {backup_file}")
            shutil.copy2(target_file, backup_file)
        
        # Read the file
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already patched
        if '# PATCHED FOR PYINSTALLER' in content:
            print("scipy already patched!")
            return
        
        # Find and replace the problematic section
        # The issue is around line 360 where it has:
        #     exec('del ' + obj)
        # del obj
        
        original = """    exec('del ' + obj)
del obj"""
        
        patched = """    exec('del ' + obj, globals(), locals())
# PATCHED FOR PYINSTALLER - Commenting out 'del obj' that causes issues in Python 3.12
# del obj"""
        
        if original in content:
            content = content.replace(original, patched)
            print("Patching scipy...")
            
            # Write the patched content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Successfully patched {target_file}")
            print("You can restore the original file from the backup if needed.")
        else:
            print("Could not find the expected code pattern to patch.")
            print("scipy version might have changed.")
            
    except Exception as e:
        print(f"Error patching scipy: {e}")
        sys.exit(1)

if __name__ == '__main__':
    patch_scipy()
