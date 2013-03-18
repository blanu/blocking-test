import os
import sys
import glob
import time
import json
import shutil

from paver.easy import *
from paver.path import *

sys.path.append(os.path.abspath('.'))

# Build and install dependencies
@task
@needs(['prepareEncoders', 'prepareDetectors', 'prepareCapture', 'prepareGenerate'])
def prepare(options):
  pass

# Build and install Tor, obfs2, and Dust
@task
@needs(['tor', 'dust', 'obfsproxy'])
def prepareEncoders(options):
  pass

# Build and install Tor from source
@task
def tor(options):
  prefix=os.getcwd()+'/deps/tor'
  libevent=os.getcwd()+'/deps/libevent/'

  if not os.path.exists('deps/tor/bin/tor'):
    if not os.path.exists('deps/tor'):
      os.mkdir('deps/tor')
    if not os.path.exists('build'):
      os.mkdir('build')
    with pushd('build'):
      if not os.path.exists('tor'):
        sh('git clone git://git.torproject.org/tor.git')
      with pushd('tor'):
        sh('git pull')
        if not os.path.exists('tor/src/or/tor'):
          if not os.path.exists('Makefile'):
            if not os.path.exists('configure'):
              sh('./autogen.sh')
            sh('./configure --prefix='+prefix+' --disable-asciidoc --with-libevent-dir='+libevent)
          sh('make')
        sh('make install')

# Install Dust from source
@task
def dust(options):
  if not os.path.exists('deps/Dust/py/dust/commands/go.sh'):
    with pushd('deps'):
      sh('git clone git://github.com/blanu/Dust.git')

# Build and install obfs2 from source
@task
@needs(['libevent'])
def obfsproxy(options):
  prefix=os.getcwd()+'/deps/obfsproxy'
  libevent=os.getcwd()+'/deps/libevent/lib/pkgconfig/'

  if not os.path.exists('deps/obfsproxy/bin/obfsproxy'):
    if not os.path.exists('deps'):
      os.mkdir('deps')
    if not os.path.exists('deps/obfsproxy'):
      os.mkdir('deps/obfsproxy')
    if not os.path.exists('build'):
      os.mkdir('build')
    with pushd('build'):
      if not os.path.exists('obfsproxy'):
        sh('git clone git://git.torproject.org/obfsproxy.git')
      with pushd('obfsproxy'):
        sh('git pull')
        if not os.path.exists('obfsproxy'):
          if not os.path.exists('Makefile'):
            if not os.path.exists('configure'):
              sh('./autogen.sh')
            sh('./configure --prefix='+prefix+' PKG_CONFIG_PATH='+libevent)
          sh('make')
        sh('make install')

# Build and install libevent from source, required by Tor and obfs2
@task
def libevent(options):
  from urllib import urlretrieve

  prefix=os.getcwd()+'/deps/libevent'
  if not os.path.exists('deps/libevent/lib/libevent.la'):
    if not os.path.exists('deps'):
      os.mkdir('deps')
    if not os.path.exists('deps/libevent'):
      os.mkdir('deps/libevent')
    if not os.path.exists('build'):
      os.mkdir('build')
    with pushd('build'):
      if not os.path.exists('libevent-2.0.11-stable'):
        if not os.path.exists('libevent.tgz'):
          urlretrieve('http://monkey.org/~provos/libevent-2.0.11-stable.tar.gz', 'libevent.tgz')
        sh('tar zxvf libevent.tgz')
      with pushd('libevent-2.0.11-stable'):
        if not os.path.exists('libevent.la'):
          if not os.path.exists('Makefile'):
            sh('./configure --prefix='+prefix)
          sh('make')
        sh('make install')

# Install dependencies for detectors
@task
def prepareDetectors(options):
  call_task('prepareRLibs')

# Install R library dependencies for detectors
@task
def prepareRLibs(options):
  sh('sudo Rscript prepareRLibs.r')
