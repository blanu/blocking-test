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
  # Capture configuration
  testing=Bunch(
    traceDir='traces',
    traceHost='internews.org'
  )
)

@task
def all(options):
  call_task('traceroute')
  call_task('ping')

# Record traceroute to server
@task
def traceroute(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; traceroute %s 2>&1 | tee %s/traceroute.txt) &" % (options.testing.traceHost, traceDir))
  time.sleep(180)
  sh('killall traceroute')

# Record ping to server
@task
def ping(options):
  traceDir=options.testing.traceDir
  if not os.path.exists(traceDir):
    os.mkdir(traceDir)
  sh("(date; ifconfig; ping %s 2>&1 | tee %s/ping.txt) &" % (options.testing.traceHost, traceDir))
  time.sleep(60)
  sh('killall ping')

# Generate HTTP over Tor over obfs2 traffic
@task
def generate_tor_dust(options):
  call_task('run_tor_with_dust')

  sh('nosetests generate:TorTests')

  call_task('kill_fab')
  call_task('kill_tor')

# Generate HTTP over Tor over obfs2 traffic
@task
def generate_http_dust(options):
  call_task('run_dust')

  sh('nosetests generate:DustTests')

  call_task('kill_fab')
  call_task('kill_dust')

# Generate HTTPS traffic
@task
def generate_https(options):
  sh('nosetests generate:HttpsTests')

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
