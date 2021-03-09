#!/usr/bin/env python
import requests
import csv
import sys
import pandas as pd
import urllib3
import socket
from collections import namedtuple
import urllib.request

urllib3.disable_warnings()

# check status of site
def get_status(site):
    WebsiteStatus = namedtuple('WebsiteStatus', ['status_code', 'reason'])
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    try:
        response = requests.head(site, timeout=5, allow_redirects=False, headers=headers, auth=False)
        status_code = response.status_code
        reason = response.reason
    except requests.exceptions.ConnectionError:
        status_code = '000'
        reason = 'ConnectionError'
    return WebsiteStatus(status_code, reason)



# create a new CSV with site status.
# output: output_http_status.csv file
def get_pages(fn, l=0,results=[]):
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        results.append((['URL', 'ip', 'port', 'protocol', 'service', 'os_name', 'host_name', 'status_code', 'reason']))
        for row in csv_reader:
            ip = row[1]
            port = row[2]
            protocol = row[3]
            service = row[4]
            os_name = row[5]
            host_name = row[6]
            url = (service+'://'+ip)
            
            # skip header columns, else create column headers
            if(l>0):

                # Only going to scan a standards ports for now
                if (service in ['http','https'] and port in ["443","80"]):
                    sitestatus = get_status(url)
                    code = sitestatus.status_code
                    reason = sitestatus.reason        
                else: 
                    code = "None_standard"
                    reason = "None_standard"
                    
                print(str(l)+"_\t{0:30} {1:10} {2:10}".format(url, code, reason))
                t = ([url, ip, port, protocol, service, os_name, host_name, code, reason])
                results.append(t)                
            l+=1
        df = pd.DataFrame(results)
        df.to_csv("output_http_status.csv", index=False, header=False)
        print(f'Processed {l} lines.')

# get filename passed through arg CLI
get_pages(sys.argv[1:][0])
