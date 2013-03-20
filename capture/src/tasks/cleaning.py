import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Delete all .pyc files, dependencies, and directory used for building dependencies
@task
@needs(['cleanBuild', 'cleanDeps'])
def clean(options):
  files=glob.glob('*.pyc')
  for file in files:
    os.remove(file)

# Delete directory used for building dependencies
@task
def cleanBuild():
  if os.path.exists('build'):
    shutil.rmtree('build')

# Delete dependencies
@task
def cleanDeps():
  if os.path.exists('deps'):
    shutil.rmtree('deps')

# Delete trace directories
@task
def cleanTraces():
  if os.path.exists('traces'):
    shutil.rmtree('traces')
