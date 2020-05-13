#!/usr/bin/env python3
import json
import sys
import os
import argparse
import time
import csv
import difflib

from urllib.parse import urlparse
# https://pypi.org/project/grafana-api/
from grafana_api import GrafanaFace
from grafana_api.grafana_api import GrafanaClientError
from datetime import datetime

SUCCESS=0
ERROR=1

ALL_ORGS = None
CLI = None

def printlist(l):
    for e in l:
        print(e)
        
def printerror(*args):
    print(*args, file=sys.stderr)


def read_dash_json(fname):
    with open(fname, 'r') as f:
        dash_json = json.loads(f.read())
    return dash_json

def dashboard_command(args):
    if args.list:
        # get source org dashboards
        dashboards = CLI.search.search_dashboards()

        writer = csv.writer(sys.stdout, dialect=csv.excel_tab)
        keys = dashboards[0].keys()
        writer.writerow(keys)
        for d in dashboards:
            writer.writerow([d[k] for k in keys])

    elif args.dump is None:
        # download all dashboards for the org
        dashboards = CLI.search.search_dashboards()
        for dash in dashboards:
            if dash['type'] != 'dash-db':
                continue
            dump_dashboard(dash['title'])

    elif args.dump != '__all__':
        # download a dashboard
        dump_dashboard(args.dump)

    elif args.diff:
        # show diff of the locally saved dashboard json, and the one in the Grafana
        new_dash = read_dash_json(args.diff)
        uid = new_dash['dashboard']['uid']
        old_dash = CLI.dashboard.get_dashboard(uid)

        new_dash_json=json.dumps(new_dash, sort_keys=True, indent=2)
        old_dash_json=json.dumps(old_dash, sort_keys=True, indent=2)
        printlist(difflib.unified_diff(old_dash_json.split("\n"), new_dash_json.split("\n")))
        
    elif args.upload:
        # upload the local dashboard json.  Overwrite if the same uid exists
        new_dash = read_dash_json(args.upload)
        payload = {
            "dashboard": new_dash['dashboard'],
            "folderId": 0,
            "overwrite": True
        }
        upload_dashboard(payload)

    return SUCCESS

def dump_dashboard(dash_title):
    # prepare source
    dashes = CLI.search.search_dashboards(dash_title)
    if not dashes:
        raise ValueError("{} not found".format(dash_title))

    dash = None
    for d in dashes:
        if d['title'] == dash_title:
            dash = d
            break
    else:
        raise ValueError("Ambiguous dashboard title {}.  Found multiple {}".format(dash_title, dash))

    # ignore folders and other non-dashboard data
    if dash['type'] != 'dash-db':
        raise ValueError("{} is not a dashboard type: The type is {}".format(dash_title, dash['type']))

        
    # Getting the dashboard from the source org
    dash_detail = CLI.dashboard.get_dashboard(dash['uid'])
    name = "{}_{}".format(dash['id'], dash['title']).lower().replace(' ', '_') + ".json"
    printerror("Saving {}".format(dash['title']))
    with open(name, 'w') as fh:
        fh.write(json.dumps(dash_detail))

def upload_dashboard(dash_json):
    CLI.dashboard.update_dashboard(dash_json)
    
def find_org_by_name(org_name):
    """
    find the target org id by name
    """
    global ALL_ORGS
    if not ALL_ORGS:
        ALL_ORGS = CLI.organizations.list_organization()
        
    org = None
    for o in ALL_ORGS:
        if o["name"] == org_name:
            org = o
            return org
    return None
    
def main():
    global CLI
    parser = argparse.ArgumentParser(description="Grafana admin")
    parser.add_argument("--url", help="Grafana URL")
    parser.add_argument("--admin", help="admin username")
    parser.add_argument("--password", help="admin password")
    parser.add_argument("--org", dest="org_name", help="org name")

    # dashbord command
    parser.add_argument("--list", default=False, action='store_true', help="list dashboards")
    parser.add_argument("--dump", nargs='?', help="dump a dashboard", default='__all__')
    parser.add_argument("--diff", help="take a diff of locally saved dashboard json and the one in the Grafana")
    parser.add_argument("--upload", help="upload a dashboard.  Overwrite existing dashboard if the same uid exists")
    parser.set_defaults(func=dashboard_command)

    args = parser.parse_args()

    # try to find configs from env var if not given in the command line
    args.url = args.url or os.environ.get("GRAFANA_URL")
    args.admin = args.admin or os.environ.get("GRAFANA_ADMIN_USER")
    args.password = args.password or os.environ.get("GRAFANA_ADMIN_PASS")
    args.org_name = args.org_name or os.environ.get("GRAFANA_ORG")

    # check mandatory configs
    if not (args.admin and args.password and args.org_name):
        print("Please set admin user and password. Alternatively the admin user and the password can be set via GRAFANA_ADMIN_USER and GRAFANA_ADMIN_PASS env variables.")
        sys.exit(ERROR)

    # create a grafana client.
    u = urlparse(args.url)
    CLI = GrafanaFace((args.admin, args.password), host= u.netloc, protocol=u.scheme)

    # make sure the org exists
    org = find_org_by_name(args.org_name)
    if not org:
        printerror("org \"{}\" not found".format(args.org_name))
        printerror("Valid orgs:")
        for o in ALL_ORGS:
            printerror(o['name'])
            return ERROR

    # Switch the cli to the target org.  Please note the cli is stateful in terms of org.
    CLI.organizations.switch_organization(org["id"])

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
