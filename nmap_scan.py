import xml.etree.ElementTree as ET
import requests
import argparse
import pandas as pd
from datetime import datetime
import urllib3
import socket
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Send data to Splunk via CURL
def send_to_splunk(durr, col_headers):
    this_hostname = (socket.gethostbyaddr(socket.gethostname())[0])
    this_IP = (socket.gethostbyaddr(socket.gethostname())[2])
    sourcetype = 'external_scans'
    source = "nmap_scanV1"

    data = '{"sourcetype": "'+sourcetype+'","source": "'+source+'","host":"'+this_hostname+'","event":"'
    x = 0
    for i in col_headers:
        try: data += col_headers[x]+'='+durr[x]
        except: pass
        if i != len(col_headers): data += ', '
        x += 1
    data += '"}'

    # Splunk Event colector & source type. Change to your URL
    url = 'https://http-inputs-XYZ.splunkcloud.com:443/services/collector'
    headers = {'Authorization': 'Splunk 12345678-ABCD-4321-EFGH-1234567890XY'}
    
    # Send Data using curl
    response = requests.post(url=url, headers=headers, data=data, verify=False)
    #print (data+"\n")
    return 0


# function will just parse out xml format into a single line/txt file of online IPs only
def def_JustIps(curr_date, fn_phase, result = []):

    # Open file for reading
    root = (ET.parse("./"+fn_phase)).getroot()

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
    fn = fn_phase+".txt"
    df.to_csv(fn, index=False, header=False)
    return fn


# function to create a CSV of result scans
def create_csv(curr_date, fn_phase, result = []):
    col_headers = ['IP', 'host_name', 'OS_name', 'protocol', 'port', 'service', 'product']

    # Open file for reading
    root = (ET.parse("./"+fn_phase)).getroot()

    # split it by each host
    for host in root.findall('host'):
        temp = []

        # Ignore hosts that are not 'up'
        if not host.findall('status')[0].attrib['state'] == 'up': continue

        # Get IP address and host info. 
        ip_address = host.findall('address')[0].attrib['addr']

        # If no hostname, then ''
        host_name_element = host.findall('hostnames')
        try: host_name = host_name_element[0].findall('hostname')[0].attrib['name']
        except IndexError: host_name = ''
                
        # Get the OS information if available, else ''
        try:
            os_element = host.findall('os')
            os_name = os_element[0].findall('osmatch')[0].attrib['name']
        except IndexError: os_name = ''

        # Get information on ports and services
        try:
            #loop through each port found
            port_element = host.findall('ports')
            ports = port_element[0].findall('port')
            for port in ports:
                port_data = [ip_address, host_name, os_name]

                # Ignore ports that are not 'open', skip to the next one
                if not port.findall('state')[0].attrib['state'] == 'open': continue    
                
                proto = port.attrib['protocol']
                port_id = port.attrib['portid']

                #step inside the service tag, assume the name attrib will always be there
                service = port.findall('service')[0].attrib['name']     
                try: product = port.findall('service')[0].attrib['product']
                except (IndexError, KeyError): product = ''      

                port_data.extend((proto, port_id, service, product))
                send_to_splunk(port_data, col_headers)
                result.append(port_data)

        # If no port information, just create a list of host information
        except IndexError:
            temp.extend(ip_address, host_name, os_name)
            send_to_splunk(temp, col_headers)
            result.append(temp)
    
    df = pd.DataFrame(result)
    fn = fn_phase+".csv"
    df.to_csv(fn, index=False, header=col_headers)
    return 0


# main function to run the scans
def main():
    IPs = '123.12.2.1-12'
    curr_date = datetime.now().strftime("%m-%d-%Y")
    fn_phase1 = "phase1-online_IPs_only_"+curr_date
    fn_phase2 = "phase2-probe_"+curr_date

    # just a ping/discovery scan, to see whats online. Then output it to a txt file.
    os.system('nmap [PERAMS] '+fn_phase1+' '+IPs)
    fn_IP_list = def_JustIps(curr_date,fn_phase1)

    # next probe all IPs from list we got, scan all ports (1 – 65535) + service/host info
    os.system('nmap [PERAMS] -iL '+fn_IP_list+' -oX '+fn_phase2+' '+IPs)
    create_csv(curr_date,fn_phase2)
    
    return 0

main()
