import os, subprocess, socket

# Number of workstations to Scan for
total_workstations = 5

# Save as csv file
logfile = open("PAC-IPs.csv", "w")
logfile.write("Hostname, IP\n")

# Get all IPs
with open(os.devnull, "wb") as limbo:
   for i in range(total_workstations):

      # Prefix - Create hostnames & Ping
      hostname = "MCKNWKS"+str(i)
      result = subprocess.Popen(["ping", "-n", "1", "-w", "200", hostname],stdout=limbo, stderr=limbo).wait()

      # For offline hosts
      if result:
         logfile.write(hostname+",Offline\n")
         print(hostname+" - Offline")
      # Online hosts
      else:
         IP = (socket.gethostbyaddr(hostname))[2][0]
         logfile.write(hostname+","+IP+"\n")
         print(hostname+" -> "+IP)

logfile.close()
print ("\n\t - Done - \n")
