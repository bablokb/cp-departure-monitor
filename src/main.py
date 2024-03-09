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

ui_provider   = UIProvider()
data_provider = DataProvider() 
app = Application(data_provider,ui_provider,with_rtc=False)
app.blink(0.5)
print(f"startup: {time.monotonic()-start:f}s")

if app.is_pygame:
  import sys
  import pygame

  def on_event(ev):
    if ev.key == pygame.K_ESCAPE:
      sys.exit(0)

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
