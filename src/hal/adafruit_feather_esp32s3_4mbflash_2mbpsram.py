# ----------------------------------------------------------------------------
# adafruit_feather_esp32s3_4mbflash_2mbpsram.py:
# HAL for Feather-ESP32S3 and Inky-wHat/Impression
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board

from hal.hal_base import HalBase
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import struct
import displayio
import adafruit_spd1656
from digitalio import DigitalInOut, Direction

# pinout for Pimoroni Inky-Impression / wHat
SCK_PIN   = board.SCK
MOSI_PIN  = board.MOSI
MISO_PIN  = board.MISO
DC_PIN    = board.A2
RST_PIN   = board.A1
CS_PIN_D  = board.A5
BUSY_PIN  = board.A0

DONE_PIN  = board.D5

class HalFeatherESP32S3(HalBase):
  """ pico-pi-base specific HAL-class """

  def __init__(self):
    """ constructor """
    self._done           = DigitalInOut(DONE_PIN)
    self._done.direction = Direction.OUTPUT
    self._done.value     = 0

  def _read_eeprom(self):
    """ try to read the eeprom """
    EE_ADDR = 0x50
    i2c_device = I2CDevice(board.I2C(),EE_ADDR)
    buffer = bytearray(29)
    with i2c_device as i2c:
      i2c.write(bytes([0x00])+bytes([0x00]))
      i2c.write_then_readinto(bytes([0x00]),buffer)
    return buffer

  def _get_display_info(self):
    """ try to return tuple (width,height,color) """
    COLOR = [None, 'black', 'red', 'yellow', None, 'acep7']
    try:
      data = struct.unpack('<HHBBB22s',self._read_eeprom())
      return [data[0],data[1],COLOR[data[2]]]
    except Exception as ex:
      print(f"could not read EEPROM: {ex}\nTrouble ahead!!!")
      return [400,300,'black']

  def get_display(self):
    """ return display """
    displayio.release_displays()
    width,height,color = self._get_display_info()
    spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
    display_bus = displayio.FourWire(
      spi, command=DC_PIN, chip_select=CS_PIN_D, reset=RST_PIN, baudrate=1000000
    )

    if color == 'acep7':
      # assume Inky-Impression
      import adafruit_spd1656
      display = adafruit_spd1656.SPD1656(display_bus,busy_pin=BUSY_PIN,
                                         width=width,height=height,
                                         refresh_time=2,
                                         seconds_per_frame=40)
      display.auto_refresh = False
    else:
      # assume Inky-wHat
      import what
      display = what.Inky_wHat(display_bus,busy_pin=BUSY_PIN,
                               color=color,border_color='white',
                               black_bits_inverted=False)
    return display

  def get_rtc_ext(self):
    """ return external rtc, if available """
    try:
      from rtc_ext.pcf8563 import ExtPCF8563
      i2c = board.STEMMA_I2C()
      return ExtPCF8563(i2c)
    except:
      return None

  def shutdown(self):
    """ turn off power by pulling GP4 high """
    self._done.value = 1
    time.sleep(0.2)
    self._done.value = 0
    time.sleep(0.5)

impl = HalFeatherESP32S3()
