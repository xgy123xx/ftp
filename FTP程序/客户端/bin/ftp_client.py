import os
import sys
FILE_DIR = os.path.dirname(os.path.dirname(__file__))
os.chdir(FILE_DIR)
sys.path.append(FILE_DIR)
from core import main

if __name__ == '__main__':
    main.run()