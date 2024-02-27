# ----------------------------------------------------------------------------
# wifi_helper_builtin.py: Wifi-helper for builtin wifi
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

import board
import time
import socketpool
import ssl
import adafruit_requests

from settings import secrets

class WifiHelper:
  """ Wifi-Helper for MCU with integrated wifi """

  # --- constructor   --------------------------------------------------------

  def __init__(self,debug=False):
    """ constructor """

    self._debug = debug
    self._wifi = None
    if not hasattr(secrets,'channel'):
      secrets.channel = 0
    if not hasattr(secrets,'timeout'):
      secrets.timeout = None

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- initialze and connect to AP and to remote-port   ---------------------

  def connect(self):
    """ initialize connection """

    import wifi
    self._wifi = wifi
    self.msg("connecting to %s" % secrets.ssid)
    retries = secrets.retry

    # check for static client hostname/address
    if hasattr(self._secrets,'hostname'):
      import ipaddress
      addr  = ipaddress.ip_address(self._secrets.address)
      mask  = ipaddress.ip_address(self._secrets.netmask)
      gatew = ipaddress.ip_address(self._secrets.gateway)
      dns   = ipaddress.ip_address(self._secrets.dns)
      wifi.radio.hostname = self._secrets.hostname
      wifi.radio.set_ipv4_address(ipv4 = addr,
                                  netmask = mask,
                                  gateway = gatew,
                                  ipv4_dns = dns)    while True:
      try:
        wifi.radio.connect(secrets.ssid,
                          secrets.password,
                           channel = secrets.channel,
                           timeout = secrets.timeout
                           )
        break
      except:
        self.msg("could not connect to %s" % secrets.ssid)
        retries -= 1
        if retries == 0:
          raise
        time.sleep(1)
        continue
    self.msg("connected to %s" % secrets.ssid)
    pool = socketpool.SocketPool(wifi.radio)
    self._requests = adafruit_requests.Session(pool,ssl.create_default_context())

  # --- return implementing wifi   -----------------------------------------

  @property
  def wifi(self):
    """ return wifi """
    return self._wifi

  # --- execute get-request and return json   ------------------------------

  def get_json(self,url):
    """ process get-request """

    if not self._wifi:
      self.connect()
    return self._requests.get(url).json()

  # --- execute get-request and return response   ---------------------------

  def get(self,url):
    """ process get-request """

    if not self._wifi:
      self.connect()
    return self._requests.get(url)
