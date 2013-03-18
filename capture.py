#!/usr/bin/python
# capture.py provides a convenient interface for using scapy to capture packets
# and generate trace files. It is a standalone executable, but is normally
# launched from a paver task defined in pavement.py.

import os
import sys
import time
from threading import Thread

from scapy.all import sniff, IPv6, IP, UDP, TCP, wrpcap

class CaptureDevice:
  def __init__(self, iface, ofile):
    self.iface=iface
    self.ofile=ofile
    self.finished=True

  def start(self):
    self.packets=[]
    self.finished=False
    self.thread=Thread(target=self.run)
    self.thread.start()

  def run(self):
    sniff(iface=self.iface, prn=self.process)

  def process(self, packet):
    if self.finished:
      raise(Exception('finished'))
    else:
      self.packets.append(packet)

  def end(self):
    self.finished=True
    if len(self.packets)>0:
      wrpcap(self.ofile, self.packets)
    else:
      print('No packets captured!')

if __name__=='__main__':
  cap=CaptureDevice(sys.argv[1], sys.argv[2])
  cap.start()
  while os.path.exists('CAPTURE_RUNNING'):
    time.sleep(10)
  cap.end()
