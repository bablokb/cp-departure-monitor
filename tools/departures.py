#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Query departures for a given station id
#
# Needs pyhafas from https://github.com/FahrplanDatenGarten/pyhafas
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

import sys
import datetime

from pyhafas import HafasClient
from pyhafas.profile import DBProfile, VSNProfile

if __name__ == "__main__":
  if len(sys.argv) == 1:
    print(f"usage: {sys.argv[0]} station-id [[product] [direction]] ")
    sys.exit(0)

  dep_id = sys.argv[1]
  products = {}
  if len(sys.argv) > 2 and sys.argv[2] != "*":
    products = {
      "nationalExpress": False,
      "national": False,
      "regionalExpress": False,
      "regional": False,
      "suburban": False,
      "bus": False,
      "ferry": False,
      "subway": False,
      "tram": False,
      "taxi": False
      }
    for p in sys.argv[2].split():
      if p in products:
        products[p] = True
      else:
        print(f"unknown product: {p}")
        print(f"products: {' '.join([k for k in products.keys()])}") 
        sys.exit(1)

  if len(sys.argv) > 3:
    direction = sys.argv[3]
  else:
    direction = None

  client = HafasClient(DBProfile(), debug=True)
  deps = client.departures(
    station=dep_id,
    products=products,
    direction=direction,
    date=datetime.datetime.now(),
    duration=60,
    max_trips=10
    )

  for d in deps:
    dt = d.dateTime
    delay = getattr(d,'delay',0)
    if isinstance(delay,datetime.timedelta):
      delay = round(delay.seconds/60)
    elif delay is None:
      delay = 0
    print(f"{dt.hour:02}:{dt.minute:02} (+{delay:2}): {d.name} {d.direction}")
