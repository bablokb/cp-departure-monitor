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

ui_provider   = UIProvider()
data_provider = DataProvider() 
app = Application(data_provider,ui_provider,with_rtc=False)
app.blink(0.5)
print(f"startup: {time.monotonic()-start:f}s")

while True:
  app.run()
  if app.is_pygame:
    # pygame: don't loop, just wait for CTRL-C
    app.shutdown()
  else:
    # call shutdown if battery-management is available
    # app.set_wakeup(...)
    # app.shutdown()
    time.sleep(60)
