# pavement.py is the config file for paver.
# It contains all of the paver tasks and default options.

import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Create virtualenv environment
@task
def bootstrap(options):
    try:
        import virtualenv
    except ImportError, e:
        raise RuntimeError("virtualenv is needed for bootstrap")

    options.virtualenv.no_site_packages = False
    options.bootstrap.no_site_packages = False
    call_task('paver.virtual.bootstrap')

# Removed virtualenv environment created by bootstrap task
@task
def cleanBootstrap():
  if os.path.exists('bin'):
    shutil.rmtree('bin')
  if os.path.exists('include'):
    shutil.rmtree('include')
  if os.path.exists('lib'):
    shutil.rmtree('lib')
