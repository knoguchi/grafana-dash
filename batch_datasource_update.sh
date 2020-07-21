#!/bin/bash
#THIS IS JUST A SAMPLE TO SHOW THE IDEA OF BATCH PROCESSING.
#I CANNOT TAKE ANY RESPONSIBILITIES OF LOSS OF DATA

set -e

. ./grafana.rc

OLD="old datasource"
NEW="new datasource"

TMPJSON=___tmp.json

rm -f $TMPJSON

./grafana-dash.py --dump

for J in *.json
do
    echo "$J"
    jq -Mf ./update-datasource.jq --arg old "$OLD" --arg new "$NEW" < "$J" > "$TMPJSON"  && \
	mv "$TMPJSON" "$J" || exit
    ./grafana-dash.py --upload "$J" || exit
done
