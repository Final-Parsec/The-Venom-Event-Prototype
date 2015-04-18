import os
import glob

# Automatically imports all modules in the controllers directory.
# Allows you to add new controller files without having manually add them to this array.
__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]
