import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Run the obfs2 SOCKS proxy on the local machine and the obfs2 server on a remote machine
@task
@needs(['obfsproxy'])
def run_obfsproxy(options):
  call_task('run_remote_obfsproxy_server')
  time.sleep(5)
  call_task('run_local_obfsproxy_socks')
  time.sleep(5)

# Run the obfs2 server on a remote machine
@task
def run_remote_obfsproxy_server(options):
  sh('fab -H blanu@blanu.net run_obfsproxy_server &')

# Run the obfs2 server on the local machine
@task
@needs(['obfsproxy'])
def run_local_obfsproxy_server(options):
  sh('export LD_LIBRARY_PATH=deps/libevent/lib; nohup deps/obfsproxy/bin/obfsproxy obfs2 --dest=127.0.0.1:5001 server 0.0.0.0:1051 </dev/null &>/dev/null &')

# Run the obfs2 SOCKS proxy on the local machine
@task
@needs(['obfsproxy'])
def run_local_obfsproxy_socks(options):
  sh('export LD_LIBRARY_PATH=deps/libevent/lib; nohup deps/obfsproxy/bin/obfsproxy obfs2 socks 127.0.0.1:1050 &')

# Kill all instances of obfs2, both locally and on a remote machine
@task
def kill_obfsproxy(options):
  call_task('kill_local_obfsproxy')
  call_task('kill_remote_obfsproxy')

# Kill all instances of obfs2 running on a remote machine
@task
def kill_remote_obfsproxy(options):
  sh('fab -H blanu@blanu.net kill_obfsproxy')

# Kill all local instances of obfs2
@task
def kill_local_obfsproxy(options):
  sh('killall obfsproxy')

# Run the Dust SOCKS proxy on the local machine and the Dust server on a remote machine
@task
@needs(['dust'])
def run_dust(options):
  call_task('run_remote_dust_server')
  time.sleep(5)
  call_task('run_local_dust_socks')
  time.sleep(5)

# Run the Dust server on a remote machine
@task
def run_remote_dust_server(options):
  sh('fab -H blanu@blanu.net run_dust_server &')

# Run the Dust server on the local machine
@task
@needs(['dust'])
def run_local_dust_server(options):
  with pushd('deps/Dust/py'):
    sh('git pull origin master')
    sh('export PYTHONPATH=.; nohup python dust/services/socks3/dustSocksServer.py </dev/null &>/dev/null &')

# Run the Dust SOCKS proxy on the local machine
@task
@needs(['dust'])
def run_local_dust_socks(options):
  with pushd('deps/Dust/py'):
    sh('export PYTHONPATH=.; nohup python dust/services/socks3/socksDustProxy.py </dev/null &>/dev/null &')

# Kill all instances of Dust, both locally and on a remote machine
@task
def kill_dust(options):
  call_task('kill_local_dust')
  call_task('kill_remote_dust')

# Kill all instances of Dust running on a remote machine
@task
def kill_remote_dust(options):
  sh('fab -H blanu@blanu.net kill_dust')

# Kill all local instances of Dust
@task
def kill_local_dust(options):
  sh('killall python') # FIXME - Clearly not the way to go, maybe we need to track PIDs
