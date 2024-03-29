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

import sys
import time
try:
  import pygame
  alarm = {}
except:
  # running CircuitPython on a MCU
  import keypad
  import alarm

from application import Application
from depmon_uiprovider   import DepmonUIProvider   as UIProvider
from depmon_dataprovider import DepmonDataProvider as DataProvider
from settings import app_config
from ui_settings import UI_SETTINGS

DEBUG = getattr(app_config,'debug',False)

class DepMon(Application):
  """ Departure-Monitor main-application class """

  KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT = list(range(4))
  try:
    PYGAME_KEYMAP = {
      pygame.K_UP:       KEY_UP,
      pygame.K_PAGEUP:   KEY_UP,
      pygame.K_DOWN:     KEY_DOWN,
      pygame.K_PAGEDOWN: KEY_DOWN,
      pygame.K_LEFT:     KEY_LEFT,
      pygame.K_RIGHT:    KEY_RIGHT
      }
  except:
    pass

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """
    ui_provider   = UIProvider(debug=DEBUG)
    data_provider = DataProvider(debug=DEBUG)
    super().__init__(data_provider,ui_provider,with_rtc=False,debug=DEBUG)
    self.blink(0.1,color=Application.GREEN)

    # fill initial values for model
    self.data["row"]           = 0
    self.data["station_index"] = 0
    try:
      if hasattr(alarm,'sleep_memory'):
        index = alarm.sleep_memory[0]
        if index < len(app_config.stations):
          self.data["station_index"] = index
    except:
      pass

  # --- process keys by number   ----------------------------------------------

  def process_keys(self,key_nr):
    """ process key by nr: up, down, left, right """

    self.msg(f"process_keys for: {key_nr}")
    c_index = self.data["station_index"]
    n_departures = len(self.data["departures"][c_index].info)

    if  key_nr == DepMon.KEY_RIGHT:
      if c_index < len(app_config.stations)-1:
        self.data["station_index"] += 1
        try:
          if hasattr(alarm,'sleep_memory'):
            alarm.sleep_memory[0] = self.data["station_index"]
        except:
          pass
      self.data["row"] = 0
    elif key_nr == DepMon.KEY_LEFT:
      if c_index > 0:
        self.data["station_index"] -= 1
        try:
          if hasattr(alarm,'sleep_memory'):
            alarm.sleep_memory[0] = self.data["station_index"]
        except:
          pass
      self.data["row"] = 0
    elif key_nr == DepMon.KEY_DOWN:
      self.data["row"] += UI_SETTINGS.ROWS
      if self.data["row"] > n_departures-UI_SETTINGS.ROWS:
        self.data["row"] = n_departures-UI_SETTINGS.ROWS
    elif key_nr == DepMon.KEY_UP:
      self.data["row"] -= UI_SETTINGS.ROWS
      if self.data["row"] < 0:
        self.data["row"] = 0
    else:
      return
    self.update_display()

  # --- key-handler for PyGame-Display environment   -------------------------

  def on_event(self,ev):
    """ process key-press """

    self._last_key_time = time.monotonic()          # reset time of last key
    if ev.key in [pygame.K_ESCAPE,pygame.K_q]:
      sys.exit(0)
    elif ev.key in DepMon.PYGAME_KEYMAP:
      self.process_keys(DepMon.PYGAME_KEYMAP[ev.key])

  # --- event-handler for PyGame-Display environment   -----------------------

  def on_time(self):
    """ process regular action """

    # check for auto-shutdown if no activity for longer than off_time
    rest_time = app_config.off_time - (time.monotonic()-self._last_key_time)
    if app_config.off_time and rest_time <= 0:
      self.msg(f"shutdown due to {app_config.off_time}s of inactivity")
      self.shutdown()
    else:
      if app_config.off_time:
        rest_time = max(app_config.upd_time,int(rest_time))
        self.msg(f"about {rest_time}s left before auto-shutdown")

    # next cycle: fetch data and update display
    # note: this should be in a separate thread, not in the event-handler,
    #       but for simplicity, we do it here
    self.run()

  # --- main loop for PyGame-Display environment   ---------------------------

  def run_pygame(self):
    """ event-loop for PyGame-Display environment """

    # track time of inactivity for automatic shutdown
    self._last_key_time = time.monotonic()

    self.run()
    self.display.event_loop(
      interval=app_config.upd_time,
      on_time=self.on_time, on_event=self.on_event, events=[pygame.KEYDOWN])

  # --- main loop for normal CircuitPython environment   ---------------------

  def run_cp(self):
    """ main-loop for normal environment """

    if self.keys:
      keys = keypad.Keys(self.keys[1],
                         value_when_pressed=self.keys[0],pull=True,
                         interval=0.1,max_events=4)

    # track time of inactivity for automatic shutdown
    self._last_key_time = time.monotonic()

    while True:
      start = time.monotonic()
      self.run()
      if self.keys:
        # clear pending key-events (i.e. keys pressed during self.run())
        keys.events.clear()
        self.msg("polling for keys...")
        while time.monotonic()-start < app_config.upd_time:
          event = keys.events.get()
          if event and event.pressed:
            self._last_key_time = time.monotonic()
            self.process_keys(event.key_number)
      else:
        self.sleep(app_config.upd_time - (time.monotonic()-start))

      # check for auto-shutdown if no activity for longer than off_time
      rest_time = app_config.off_time - (time.monotonic()-self._last_key_time)
      if app_config.off_time and rest_time <= 0:
        self.msg(f"shutdown due to {app_config.off_time}s of inactivity")
        self.shutdown()
      else:
        #self.free_ui_memory()
        self.reset()  # hack for systems with low memory, noop otherwise
        if app_config.off_time:
          rest_time = max(app_config.upd_time,int(rest_time))
          self.msg(f"about {rest_time}s left before auto-shutdown")

# --- main application code   -------------------------------------------------

app = DepMon()
if app.is_pygame:
  app.run_pygame()
else:
  app.run_cp()
