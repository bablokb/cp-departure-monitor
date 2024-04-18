# ----------------------------------------------------------------------------
# settings.py: Network, hardware and application configuration
#              (not maintained in Git).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

class Settings:
  pass

# network configuration   ----------------------------------------------------

secrets  = Settings()
secrets.ssid      = 'my_wlan_ssid'
secrets.password  = 'my_secret_password'
secrets.retry     = 2                      # connect attempts
secrets.debugflag = False
secrets.channel   = 6                      # optional: use fixed channel

# hardware configuration (optional)  -----------------------------------------

hw_config = Settings()
def _get_display(hal):
  from blinka_displayio_pygamedisplay import PyGameDisplay
  return PyGameDisplay(width=296,height=128,
                       native_frames_per_second=1)
def _get_keys(hal):
  """ return list of pin-numbers for up, down, left, right """
  # format is (active-state,[up,down,left,right])
  # return (False,[board.GPa,board.GPb,board.GPc,board.GPd])
  return None

def _get_rtc_ext():
  # currently not supported/unused
  return None

# add functions as attributes
hw_config.DISPLAY     = _get_display
hw_config.get_keys    = _get_keys
hw_config.get_rtc_ext = _get_rtc_ext

# app configuration   --------------------------------------------------------

app_config = Settings()
app_config.debug = True

#app_config.stations: a list of tuples with the following fields
#  station-ID of departure
#  station-ID of direction
#  filter for product (use None for no filter)
#  filter for line name (use None for no filter)
app_config.stations = [
  (8005676,8004158,None,None),   # Starnberg in direction to Pasing
  (8004158,8005676,None,None)    # Pasing in direction to Starnberg
  ]

app_config.duration = 120        # time-horizon in minutes
app_config.upd_time = 60         # update interval in seconds
app_config.off_time = 120        # stop after given time of inactivity

# replacements (list of tuples (from,to), supports regex-syntax)
app_config.replace = [
  ("München","MUC")
  ]

# changes to UI-defaults (see ui_settings.py for a list)   -------------------

ui_config = Settings()
#ui_config.ROWS  = 8

# all settings   -------------------------------------------------------------

settings = Settings()
settings.secrets     = secrets
settings.hw_config   = hw_config
settings.app_config  = app_config
settings.ui_config   = ui_config
