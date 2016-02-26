import os, subprocess, shutil, datetime

# Building Hosts Workstations
online_hosts = []
offline_hosts = []
total_workstations = 130

# Log file
logfile = open("pushlog.txt", "w")

startlog = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

with open(os.devnull, "wb") as limbo:
   for i in range(total_workstations):

      # Prefix hostnames
      hostname = "MCKNWKS"+str(i)
      result = subprocess.Popen(["ping", "-n", "1", "-w", "200", hostname],stdout=limbo, stderr=limbo).wait()

      # Put hostnames in off/on line list
      if result:
         offline_hosts.append(hostname)
      else:
         online_hosts.append(hostname)

         # Copy files to host workstations
         shutil.copy2('LaunchSyngoVia.bat','\\\\'+hostname+'\\C$\\ITSTemp\\')
         print ("Copying file to: "+hostname+"\n")


endlog = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
print("...done: " + endlog)

# Write log file
logfile.write("Script started: "+ startlog+" ...............\n\n")

logfile.write("\n\t\t------ Online Hosts Copied Files To------\n")
for i in online_hosts: logfile.write(i+"\n")

logfile.write("\n\t\t------ Offline Hosts (Did Not Copy To)------\n")
for i in offline_hosts: logfile.write(i+"\n")

logfile.write("\n\n........... Script Ended: "+endlog+"\n\n")
logfile.close()