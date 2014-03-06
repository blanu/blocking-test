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

# Options required by different tasks
options(
  # Bootstrap configuration
  virtualenv=Bunch(
    # Packages to install in virtualenv on bootstrapping
    packages_to_install=['virtualenv', 'scapy', 'selenium', 'fabric', 'numpy', 'scipy', 'gensim', 'tornado', 'monocle'],
    # Block access to site packages
    no_site_packages=True
  ),
  # Capture configuration
  capture=Bunch(
    traceDir='test'
  ),
  # Capture configuration for HTTPS
  capture_https=Bunch(
    # default trace directory
    traceDir='test'
  ),
  # Capture configuration for obfs2
  capture_obfsproxy=Bunch(
    # default trace directory
    traceDir='test'
  ),
  # Capture configuration for Dust
  capture_dust=Bunch(
    # default trace directory
    traceDir='test'
  )
)

from tasks.bootstrapping import *
from tasks.preparing import *
from tasks.generating import *
from tasks.encoding import *
from tasks.capturing import *
from tasks.processing import *
from tasks.detecting import *
from tasks.scoring import *
from tasks.cleaning import *
from tasks.testing import *
