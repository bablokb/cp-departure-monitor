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

def get_delay(departure):
  """ return delay """
  delay = getattr(departure,'delay',0)
  if isinstance(delay,datetime.timedelta):
    return round(delay.seconds/60)
  elif delay is None:
    return 0

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

  # get column-width for delay and name
  wmax_delay = 0
  wmax_name  = 0
  for d in deps:
    wmax_delay = max(wmax_delay,len(str(get_delay(d))))
    wmax_name  = max(wmax_name,len(d.name))

  # create template for printing
  template  = f"{{h:02}}:{{m:02}}{{s}}{{d:>{wmax_delay}.{wmax_delay}}}"
  template += f" {{n:<{wmax_name}.{wmax_name}}} {{dir}}"
  for d in deps:
    dt = d.dateTime
    delay = get_delay(d)
    if d.cancelled:
      sign = ' '
      delay = 'X'*wmax_delay
    elif delay > 0:
      sign = '+'
      delay = str(delay)
    elif delay < 0:
      sign = '-'
      delay = str(-delay)
    else:
      sign = ' '
      delay = ' '
    print(template.format(h=dt.hour,m=dt.minute,s=sign,
                          d=delay,n=d.name,dir=d.direction))
