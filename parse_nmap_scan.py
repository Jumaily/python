import xml.etree.ElementTree as ET
import sys
import requests
import argparse
import pandas as pd
from datetime import datetime
import urllib3
import socket

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

col_headers = ["IP", 'host_name', 'OS_name', 'protocol', 'port', 'service', 'product']
this_hostname = (socket.gethostbyaddr(socket.gethostname())[0])
this_IP = (socket.gethostbyaddr(socket.gethostname())[2])

#curl them datas bro and not be on dat couch
def curl_bro(pumps):
    global this_hostname
    data = '{"sourcetype": "external_scans","host":"'+this_hostname+'","event":"'
    x = 0
    for i in col_headers:
        try: data += col_headers[x]+'='+pumps[x]
        except: pass
        if i != len(col_headers): data += ', '
        x += 1
    data += '"}'

    url = 'https://http-inputs-x.splunkcloud.com:443/services/collector'
    sourcetype = 'external_scans'
    headers = {'Authorization': 'Splunk xxxxxx-xxxx-xxx-xx-x'}
    response = requests.post(url=url, headers=headers, data=data, verify=False)

def whompwhomp(woot):
    result = [] # used to hold all the results to put into a csv for later

    # split it by each host
    for host in woot.findall('host'):
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
            port_element = host.findall('ports')
            #loop through each port found
            ports = port_element[0].findall('port')
            for port in ports:
                port_data = [ip_address, host_name, os_name]

                # Ignore ports that are not 'open'
                if not port.findall('state')[0].attrib['state'] == 'open': continue    #skip to the next one
                
                proto = port.attrib['protocol']
                port_id = port.attrib['portid']

                #step inside the service tag
                service = port.findall('service')[0].attrib['name']     #assume the name attrib will always be there
                try: product = port.findall('service')[0].attrib['product']
                except (IndexError, KeyError): product = ''      

                port_data.extend((proto, port_id, service, product))
                curl_bro(port_data)
                result.append(port_data)

        # If no port information, just create a list of host information
        except IndexError:
            temp.extend((ip_address, host_name, os_name))
            curl_bro(temp)
            result.append(temp)

    return result


def main():
    now = datetime.now()
    curr_date = now.strftime("%m-%d-%Y")

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    #creates the object(i think)
    tree = ET.parse("./"+args.file)
    #gets the tree of the root
    root = tree.getroot()

    datadatadata = whompwhomp(root)

    df = pd.DataFrame(datadatadata)
    df.to_csv('/jobs/scan_'+curr_date+".csv", index=False, header=col_headers)

main()
