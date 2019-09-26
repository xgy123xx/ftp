import os
import sys
FILE_DIR = os.path.dirname(os.path.dirname(__file__))
print(FILE_DIR )
os.chdir(FILE_DIR)
sys.path.insert(0,FILE_DIR)
from core import main
if __name__ == '__main__':
    main.run()
os.path.abspath()