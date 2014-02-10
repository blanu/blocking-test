# generate.py drives a web browser using Selenium 2 in order to generate HTTP
# traffic which may be, depending on the configuration, carried over SSL, Tor
# over obfs2, or Tor over Dust.
# It can be run manually using nosetests, but is normally launched from a paver
# task defined in pavement.py.

import time
import unittest

import webdriverplus as webdriver

# Generate Tor traffic
class TorTests(unittest.TestCase):
  # Set Firefox to use an encoder as a SOCKS proxy
  def setUp(self):
    profile=webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1') # This double quoting is actually correct. It works around a bug in Selenium.
    profile.set_preference('network.proxy.socks_port', 5000)
    self.browser=webdriver.Firefox(profile)

  def test_rwb(self):
    self.browser.get('http://en.rsf.org/')
  def test_bbg(self):
    self.browser.get('http://www.bbg.gov/')
  def test_hrw(self):
    self.browser.get('http://www.hrw.org/news')
  def test_gvo(self):
    self.browser.get('http://globalvoicesonline.org/')
  def test_eff(self):
    self.browser.get('http://www.eff.org/')
  def test_torproject(self):
    self.browser.get('http://www.torproject.org/')

  def tearDown(self):
    self.browser.quit()

# Generate HTTP traffic
class HttpTests(unittest.TestCase):
  # Set Firefox to use an encoder as a SOCKS proxy
  def setUp(self):
    self.browser=webdriver.WebDriver('firefox', reuse_browser=True)

  def test_rwb(self):
    self.browser.get('http://en.rsf.org/')
  def test_bbg(self):
    self.browser.get('http://www.bbg.gov/')
  def test_hrw(self):
    self.browser.get('http://www.hrw.org/news')
  def test_gvo(self):
    self.browser.get('http://globalvoicesonline.org/')
  def test_eff(self):
    self.browser.get('http://www.eff.org/')
  def test_torproject(self):
    self.browser.get('http://www.torproject.org/')
  def test_voa(self):
    self.browser.get('http://www.voanews.org/')
  def test_bbc(self):
    self.browser.get('http://www.bbc.co.uk/')
  def test_google(self):
    self.browser.get('http://google.com/')
  def test_youtube(self):
    self.browser.get('http://youtube.com/')
  def test_tor2web(self):
    self.browser.get('http://tor2web.org/')
  def test_hideme(self):
    self.browser.get('http://hideme.be/')
  def test_cgiproxy(self):
    self.browser.get('http://jmarshall.com/tools/cgiproxy')
  def test_repress(self):
    self.browser.get('http://wordpress.org/plugins/repress/')

  def tearDown(self):
    self.browser.quit()

# Generate HTTPS traffic
class HttpsTests(unittest.TestCase):
  # Make sure that no proxy is set
  def setUp(self):
#    profile=webdriver.FirefoxProfile()
#    profile.set_preference('network.proxy.type', 0)
#    self.browser=webdriver.Firefox(profile)
    self.browser=webdriver.WebDriver('firefox', reuse_browser=True)

  def test_google(self):
    self.browser.get('https://encrypted.google.com/')
  def test_eff(self):
    self.browser.get('https://www.eff.org/')
  def test_torproject(self):
    self.browser.get('https://www.torproject.org/')

  def tearDown(self):
    self.browser.quit()
