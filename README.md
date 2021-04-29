# Grafana dashboard admin tool

Please use at your own risk. Take a backup of the dashboards before performing destructive operations.

## Requirements

- python 3
- jq 1.6

This package depends on [grafana-api](https://pypi.org/project/grafana-api/) PIP package.
Run the following command to install it:

```bash
pip3 install -r requirements.txt
```

# Configuration
Edit `grafana.rc`, and set the admin username, password, organization
Then source it in the shell

```bash
. ./grafana.rc
```

# Usage

Get the list of dashboard for the org

```bash
./grafana-dash.py --list
```

Download all of the dashbaords for the org

```bash
./grafana-dash.py --dump
```

Download one dashboard

```bash
./grafana-dash.py --dump "My Dashboard"
```

Datasource update script
```bash
jq -Mf ./update-datasource.jq --arg old "old datasource name" --arg new "new datasource name" < my_dashboard.json > edited_my_dashboard.json
```

Check diff of the local dashboard json and the one in Grafana

```bash
./grafana-dash.py --diff my_dashboard.json
```

Upload one dashboard

```bash
./grafana-dash.py --upload my_dashboard.json
```

# Example 1: update datasources in a dashboard
- dashboard name "My Dashboard"
- old datasource name "old datasource"
- new datasource name "new datasource"

```bash
# download the dashboard
./grafana-dash.py --dump "My Dashboard"

# edit the datasource
jq -Mf ./update-datasource.jq --arg old "old datasource" --arg new "new datasource" < my_dashboard.json > new_my_dashboard.json

# check if the result is desirable
./grafana-dash.py --diff new_my_dashboard.json
---

+++

@@ -23,7 +23,7 @@

                 "value": "avg"
               }
             ],
-            "datasource": "old datasource",
+            "datasource": "new datasource",
             "editable": true,
             "error": false,
             "fontSize": "100%",

# upload the edited dashboard
./grafana-dash.py --upload new_my_dashboard.json
```


# Example 2: update datasources of all dashboards.
This script demonstrates the idea of batch processing.
It has no dry-run mode or any error checking.  Potentially it can destroy your Grafana dashboards.
Do not run against your production Grafana without understanding what is going on.

Edit `batch_datasource_update.sh` and set OLD and NEW datasource names
```bash
./batch_datasource_update.sh
```



