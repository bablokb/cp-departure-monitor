# -------------------------------------------------------------------------
# Departure Monitor for German public transport.
#
# This program needs an additional configuration file settings.py
# with wifi-credentials and application settings.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import time
start = time.monotonic()

from application import Application
from depmon_uiprovider   import DepmonUIProvider   as UIProvider
from depmon_dataprovider import DepmonDataProvider as DataProvider
from settings import app_config
from ui_settings import UI_SETTINGS

ui_provider   = UIProvider()
data_provider = DataProvider() 
app = Application(data_provider,ui_provider,with_rtc=False)
app.blink(0.5)
print(f"startup: {time.monotonic()-start:f}s")

# fill initial values for model
app.data["station_index"] = 0
app.data["row"]           = 0

if app.is_pygame:
  import sys
  import pygame

  # --- define event handler for keys   --------------------------------------

  def on_event(ev):
    if ev.key == pygame.K_ESCAPE:
      sys.exit(0)

    c_index = app.data["station_index"]
    n_departures = len(app.data["departures"]
                       [app_config.stations[c_index][0]].info)

    if ev.key == pygame.K_RIGHT:
      if c_index < len(app_config.stations)-1:
        app.data["station_index"] += 1
    elif ev.key == pygame.K_LEFT:
      if c_index > 0:
        app.data["station_index"] -= 1
    elif ev.key == pygame.K_DOWN:
      app.data["row"] += UI_SETTINGS.ROWS
      if app.data["row"] > n_departures-UI_SETTINGS.ROWS:
        app.data["row"] = n_departures-UI_SETTINGS.ROWS
    elif ev.key == pygame.K_UP:
      app.data["row"] -= UI_SETTINGS.ROWS
      if app.data["row"] < 0:
        app.data["row"] = 0
    ui_provider.update_ui(app.data)

  # --- main application logic   ---------------------------------------------

  app.run()
  app.display.event_loop(
    interval=app_config.upd_time,
    on_time=app.run, on_event=on_event, events=[pygame.KEYDOWN])
else:
  while True:
    app.run()

  # look for key-events until update-time expires
  #rest = max(0,app_config.upd_time-(time.monotonic()-cycle_start))
  #print(f"next update in {int(rest)}s")
  #self.process_keys(rest)
