#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Query station id from HAFAS
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
from pyhafas import HafasClient
from pyhafas.profile import DBProfile, VSNProfile

if __name__ == "__main__":
  if len(sys.argv) == 1:
    print(f"usage: {sys.argv[0]} search-term")
    sys.exit(0)

  client = HafasClient(DBProfile(), debug=True)
  stations = client.locations(' '.join(sys.argv[1:]))

  for i in range(min(len(stations),10)):
    print(f"{stations[i].id}: {stations[i].name}") 
    
