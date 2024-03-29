# -------------------------------------------------------------------------
# Dataprovider for the Departure Monitor.
#
# Interface to https://v6.db.transport.rest/
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# -------------------------------------------------------------------------

import gc
import time
try:
  # Blinka (CPython)
  import json_stream
except:
  # CircuitPython
  import adafruit_json_stream as json_stream

from settings import app_config

# --- interface to https://v6.db.transport.rest/   ---------------------------

URL_PREFIX='https://v6.db.transport.rest/stops'
URL_SUFFIX='departures?linesOfStops=false&remarks=false&pretty=false'

# --- helper classes (value-holders)   ---------------------------------------

class DepInfo:
  """ Value-holder for departure information """
  def __init__(self,plan,delay,line,dir,cancelled):
    self.plan      = plan
    self.delay     = delay
    self.line      = line
    self.dir       = dir
    self.cancelled = cancelled

class StatInfo:
  """ departure info for a station """
  def __init__(self,name,info,update):
    self.name   = name
    self.info   = info
    self.update = update

# --- main data-provider class   ---------------------------------------------

class DepmonDataProvider:

  def __init__(self,debug=False):
    self._debug = debug
    self._wifi  = None

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- set wifi-object   ----------------------------------------------------

  def set_wifi(self,wifi):
    """ set wifi-object """
    self._wifi   = wifi

  # --- trace memory   -------------------------------------------------------

  def _mem_free(self,label):
    """ print free memory (not available with Blinka) """
    try:
      self.msg(f"{label}: {gc.mem_free()}")
    except:
      pass

  # --- parse iso-time   -----------------------------------------------------

  def _parse_time(self,tm):
    """ parse iso-timestamp """

    the_date, the_time = tm.split('T')
    #year,month,mday   = the_date.split('-')
    hour,minute        = the_time.split(':')[0:2]

    offset = the_time[-6:]
    sign = 1 if offset[0] == '+' else -1
    offset = sign*3600*int(offset[1:3])+sign*60*int(offset[4:])
    return [hour,minute,offset]

  # --- create query-url   ---------------------------------------------------

  def _create_url(self,station,via,products):
    """ create query url for hafas """

    url = f"{URL_PREFIX}/{station}/{URL_SUFFIX}&duration={app_config.duration}"
    if via:
      url = f"{url}&direction={via}"
    if not products:
      return url

    # if we need to filter by product, set all products to false except those
    # that are provided
    all_products = {
      "nationalExpress": "false",
      "national": "false",
      "regionalExpress": "false",
      "regional": "false",
      "suburban": "false",
      "bus": "false",
      "ferry": "false",
      "subway": "false",
      "tram": "false",
      "taxi": "false"
      }
    for p in products.split(","):
      all_products[p] = "true"

    # add to url
    for key,value in all_products.items():
      url += f"&{key}={value}"
    return url
    
  # --- query departures   ---------------------------------------------------

  def update_data(self,data):
    """ callback for App: query data """

    dm_data = {"departures": [], "update": None}

    for station,via,product,line in app_config.stations:
      self.msg(f"fetching departures for {station}")
      info = []
      url   = self._create_url(station,via,product)
      self._mem_free("free memory before wifi.get()")
      resp  = self._wifi.get(url)
      jdata = json_stream.load(resp.iter_content(256))

      for dep in jdata["departures"]:
        stat_name = dep["stop"]["name"]
        cancelled = dep["when"] is None
        hour,minute,offset = self._parse_time(dep["plannedWhen"])
        plan  = ":".join([hour,minute])
        delay = dep["delay"]
        if delay:
          delay = int(int(delay)/60)
        else:
          delay = 0
        direction = dep["direction"]
        name      = dep["line"]["name"]
        # filter for given line
        if line and name != line:
          continue
        info.append(DepInfo(plan,delay,name,direction,cancelled))

      # get update-timepoint (robust code, might not exist)
      updated = jdata["realtimeDataUpdatedAt"]
      if updated:
        updated = int(updated)+offset
      self._mem_free("free memory after parsing response")
      #resp.close()
      #resp = None
      jdata = None
      gc.collect()
      self._mem_free("free memory after closing response")
      dm_data["departures"].append(StatInfo(stat_name,info,updated))

    data.update(dm_data)
