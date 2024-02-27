#!/bin/bash

station="$1"
via="$2"
duration="&duration=${3:-10}"

if [ -n "$via" ]; then
  via="&direction=$via"
fi

url_prefix='https://v6.db.transport.rest/stops'
url_suffix='departures?linesOfStops=false&remarks=false&pretty=true'

wget -qO - "$url_prefix/$station/$url_suffix$duration$via"
