# ----------------------------------------------------------------------------
# wifi_helper_generic.py: Wifi-helper for CPython
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

import socket
import ssl
import adafruit_requests

class WifiHelper:
  """ request-implementation using sockets from CPython """

  def __init__(self,debug=False):
    """ constructor """
    self._debug = debug
    self._http = None

  def connect(self):
    self._http = adafruit_requests.Session(socket,ssl.create_default_context())

  def get_json(self,url):
    if not self._http:
      self.connect()
    response = self._http.get(url)
    result = response.json()
    response.close()
    return result

  def get(self,url):
    if not self._http:
      self.connect()
    return self._http.get(url)

  @property
  def wifi(self):
    """ return ourselves as wifi-module """
    return self

  @property
  def connected(self):
    """ emulate radio.connected """
    return self._http is not None

