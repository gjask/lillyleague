import sys
import os

path = os.path.dirname(__file__)

activate_this = os.path.join(path, 'env', 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, path)
from lilly import app as application