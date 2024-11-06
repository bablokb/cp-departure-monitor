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
    retries = max(1,secrets.retry)

    # check for static client hostname/address
    if hasattr(secrets,'hostname'):
      import ipaddress
      addr  = ipaddress.ip_address(secrets.address)
      mask  = ipaddress.ip_address(secrets.netmask)
      gatew = ipaddress.ip_address(secrets.gateway)
      dns   = ipaddress.ip_address(secrets.dns)
      wifi.radio.hostname = secrets.hostname
      wifi.radio.set_ipv4_address(ipv4 = addr,
                                  netmask = mask,
                                  gateway = gatew,
                                  ipv4_dns = dns)
    while retries > 0:
      retries -= 1
      try:
        wifi.radio.connect(secrets.ssid,
                          secrets.password,
                           channel = secrets.channel,
                           timeout = secrets.timeout
                           )
        if wifi.radio.connected:
          break
      except Exception as ex:
        self.msg(f"connection to {secrets.ssid} failed with {ex}")
      time.sleep(1)
      continue

    if retries == 0 and not wifi.radio.connected:
      raise RuntimeError(f"could not connect to {secrets.ssid}")

    self.msg(f"connected to {secrets.ssid}")
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

  def get(self,url,**kw):
    """ process get-request """

    if not self._wifi:
      self.connect()
    return self._requests.get(url,**kw)
