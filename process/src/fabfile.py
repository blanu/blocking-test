# fabfile.py is a Fabric configuraton file defining tasks which can be executed
# remotely. Remote tasks execution allows for client and server components to
# be executed on different machines, allowing for the traffic between them to
# travel across the Internet and therefore giving more representative traces
# than when run over loopback.
# It can be used manually with the "fab" command, but is normally launched
# from a paver task defined in pavement.py.

import os

from fabric.api import cd, run

def list():
  with cd('blockint-test'):
    run('ls *.zip')
