import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

options(
  # Capture configuration
  generate=Bunch(
    traceDir='traces',
  )
)

# Generate HTTP over Tor over obfs2 traffic
@task
def generate_tor_obfs2(options):
  call_task('run_tor_with_obfs2')

  sh('nosetests generate:TorTests')

  call_task('kill_fab')
  call_task('kill_tor')

# Run a local Tor client and a remote Tor bridge, both configured to use a obfs2 encoder
@task
def run_tor_with_obfs2(options):
  call_task('run_remote_tor_bridge')
  time.sleep(10)
  call_task('run_local_tor_client_with_obfs2')
  time.sleep(10)

# Run a local Tor client and a remote Tor bridge, both configured to use a Dust encoder
@task
def run_tor_with_dust(options):
  call_task('run_remote_tor_bridge')
  time.sleep(10)
  call_task('run_local_tor_client_with_dust')
  time.sleep(10)

# Run the Tor client on a remote machine, configured to use obfs2
@task
def run_local_tor_bridge(options):
  sh('nohup deps/tor/bin/tor -f etc/torrc_bridge &')

# Run the Tor client on the local machine, configured to use obfs2
@task
def run_local_tor_client_with_obfs2(options):
  sh('nohup deps/tor/bin/tor -f etc/torrc_client_obfs2 &')

# Run the Tor client on the local machine, configured to use Dust
@task
def run_local_tor_client_with_dust(options):
  sh('nohup deps/tor/bin/tor -f etc/torrc_client_dust &')

# Run the Tor bridge on a remote machine, configured to use obfs2
@task
def run_remote_tor_bridge(options):
  sh('fab -H blanu@blanu.net run_tor_bridge &')

# Kill all Tor processes, both local and remote
@task
def kill_tor(options):
  call_task('kill_local_tor')
  call_task('kill_remote_tor')

# Kill Fabric processes running on thelocal machine
@task
def kill_fab(options):
  sh('killall fab')

# Kill Tor processes running on the local machine
@task
def kill_local_tor(options):
  sh('killall tor')

# Kill Tor processes running on a remote machine
@task
def kill_remote_tor(options):
  sh('fab -H blanu@blanu.net kill_tor')
