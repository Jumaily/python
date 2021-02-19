import xml.etree.ElementTree as ET
import requests
import argparse
import pandas as pd
from datetime import datetime
import urllib3
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def def_JustIps(result = []):
    curr_date = datetime.now().strftime("%m-%d-%Y")
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    root = (ET.parse("./"+args.file)).getroot()

    # split it by each host
    for host in root.findall('host'):
        temp = []

        # Ignore hosts that are not 'up'
        if not host.findall('status')[0].attrib['state'] == 'up': continue

        # Get IP address only
        ip_address = host.findall('address')[0].attrib['addr']
        temp.extend((ip_address,))
        result.append(temp)

    df = pd.DataFrame(result)
    fn = './IPs_only_'+curr_date+".csv"
    df.to_csv(fn, index=False, header=False)

    return 0


def main():
    def_JustIps()

main()
