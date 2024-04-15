# -------------------------------------------------------------------------
# UI settings.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# -------------------------------------------------------------------------

from displayio import Palette

class Settings:
  pass

PALETTE = Palette(7)
PALETTE[0] = 0xFFFFFF
PALETTE[1] = 0x000000
PALETTE[2] = 0x0000FF
PALETTE[3] = 0x00FF00
PALETTE[4] = 0xFF0000
PALETTE[5] = 0xFFFF00
PALETTE[6] = 0xFFA500

# index into palette
COLORS = Settings()
COLORS.WHITE  = 0
COLORS.BLACK  = 1
COLORS.BLUE   = 2
COLORS.GREEN  = 3
COLORS.RED    = 4
COLORS.YELLOW = 5
COLORS.ORANGE = 6

# UI-settings
UI_SETTINGS = Settings()
UI_SETTINGS.PALETTE    = PALETTE
UI_SETTINGS.FONT       = "fonts/DejaVuSansMono-Bold-16.bdf"
UI_SETTINGS.MARGIN     = 1
UI_SETTINGS.FG_INDEX   = COLORS.BLACK
UI_SETTINGS.BG_INDEX   = COLORS.WHITE
UI_SETTINGS.ROWS       = 4
UI_SETTINGS.FOOTER     = "Aktualisiert"

# don't change
UI_SETTINGS.FG_COLOR = PALETTE[UI_SETTINGS.FG_INDEX]
UI_SETTINGS.BG_COLOR = PALETTE[UI_SETTINGS.BG_INDEX]

# overrides from settings

try:
  from settings import ui_config
  for var in dir(ui_config):
    if var[0] != '_':
      setattr(UI_SETTINGS,var,getattr(ui_config,var))
except:
  raise
