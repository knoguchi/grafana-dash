# Grafana dashboard admin tool

Please use at your own risk. Take a backup of the dashboards.

# Configuration
Edit grafana.rc, and set the admin username, password, organization

# Usage

Get the list of dashboard for the org

```
./grafana-dash.py --list
```

Download all of the dashbaords for the org

```
./grafana-dash.py --dump
```

Download one dashboard

```
./grafana-dash.py --dump "My Dashboard"
```

Check diff of the local dashboard json and the one in Grafana

```
./grafana-dash.py --diff my_dashboard.json
```


Upload one dashboard

```
./grafana-dash.py --upload my_dashboard.json
```

# Example: I want to update datasource
- dashboard name "My Dashboard"
- old datasource name "old datasource"
- new datasource name "new datasource"

```
# download the dashboard
./grafana-dash.py --dump "My Dashboard"

# edit the datasource
./update-datasource.jq --arg old "old datasource" --arg new "new datasource" < my_dashboard.json > new_my_dashboard.json

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

# upload the datasource
./grafana-dash.py --upload new_my_dashboard.json
```



