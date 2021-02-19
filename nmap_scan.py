import xml.etree.ElementTree as ET
import requests
import argparse
import pandas as pd
from datetime import datetime
import urllib3
import socket
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# function will just parse out xml format into a single line/txt file of 
# online IPs only
def def_JustIps(curr_date, fn_phase1, result = []):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)

    # Open file for reading
    root = (ET.parse("./"+fn_phase1)).getroot()

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
    fn = fn_phase1+".txt"
    df.to_csv(fn, index=False, header=False)
    return fn


def main():
    IPs = '128.163.188.10-15'
    curr_date = datetime.now().strftime("%m-%d-%Y")
    fn_phase1 = "phase1-online_IPs_only_"+curr_date
    fn_phase2 = "phase2-probe_"+curr_date

    # just a ping/discovery scan, to see whats online. Then output it to a txt file.
    os.system('nmap -sn -n -T4 -oX '+fn_phase1+' '+IPs)
    fn_IP_list = def_JustIps(curr_date,fn_phase1)

    # next probe all IPs from list we got, scan all ports (1 – 65535) + service/host info
    os.system('nmap -sS -p- -sV -O -T4 -iL '+fn_IP_list+' -oX '+fn_phase2+' '+IPs)

    
    return 0

main()
