#!/usr/bin/env python3
import svc_config
import os
import sys
from time import sleep
import zipfile
import splunklib.client as client
from splunklib.binding import AuthenticationError


def run_q(earliest_time,latest_time,fname):
    search_string = "search index=its_network_sec_fw sourcetype=pan:traffic "\
    " host=uk-pa7080-edge1-act-log.net.uky.edu src_zone IN (campus-edge_outside,campus-edge_inside) "\
    " dest_zone IN (campus-edge_outside,campus-edge_inside) "\
    " | dedup src_ip | stats count by src_zone, action, rule | sort -count"

    try: service = client.connect(host=svc_config.splunk_host, port=8089, username=svc_config.splunk_user, password=svc_config.splunk_ps)
    except AuthenticationError: sys.exit("Error: incorrect credentials")

    print("Successfully connected to Splunk")
    jobs = service.jobs
    kwargs = {"exec_mode": "normal", "earliest_time": earliest_time, "latest_time": latest_time}
    
    print("Running search")
    job = jobs.create("search " + search_string, **kwargs)
    print("Search job created with SID %s" % job.sid)

    # Wait for job to complete
    while True:
        while not job.is_ready(): pass
        if job["isDone"] == "1":
            print("\nJob completed")
            break
        else: progress_percent = round(float(job["doneProgress"])*100, 1)
        sleep(10)

    event_count = int(job["eventCount"])
    print("\nDownloading and writing results to file")
    i = 0

    # Read results and write to file
    with open(os.path.join(fname), "wb") as out_f:
        while i < event_count:
            try: job_results = job.results(output_mode="csv", count=1000, offset=i)
            except AuthenticationError: 
                print("Session timed out. Reauthenticating")
                service = client.connect(host=hostname, port=8089, username=username, password=password)
                job_results = job.results(output_mode="csv", count=1000, offset=i)
            for result in job_results: out_f.write(result)
            i += 1000
    out_f.close

    # Create tar and delete raw file to save space
    tfile = fname+".tar.gz"
    print (tfile)
    zip_file = zipfile.ZipFile(tfile, 'w')
    zip_file.write(fname, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()    
    os.remove(fname) 
    print("\nDone!")


def main(fpath):
    for dy in range(1, 29):
        #for hr in range(0, 23):
        earliest_t = "2023-04-"+(str(dy).zfill(2))+"T01:00:00.000"
        latest_t = "2023-04-"+(str(dy).zfill(2))+"T23:00:00.000"
        fname = fpath+"splKresults_day-"+str(dy)+".csv"
        run_q(earliest_t, latest_t, fname)
        sleep(30)


# run it
main("/cybsec_automate/splunk_dump/")
