''' Read each file and get study ID, MRN, and patient names
    -------------------------------------------------------
    use: python get_study_info_from_logs.py modalityname
'''
import os, re, datetime, glob, sys

# Get read/write time of file
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

# Get Command line input 
modality = sys.argv[1:][0]

# Great master array to sort/store info in
studies = []

# Our prod servers
servers = ["PrdRadMckApp01","PrdRadMckApp02","PrdRadMckApp03","PrdRadMckApp04","PrdRadMckApp05"]
for s in servers:
   # Path to local files
   dir = '//'+s+'/i$/ali/site/log'
   os.chdir(dir)

   # Log files
   files = glob.glob('igen_'+modality+'_importer_*.log')
   files.sort(key=os.path.getmtime)

   for file in (files):
      with open(file, 'r') as searchfile:
         acn = ln = fn = mn = mrn = ''
         for line in searchfile:
            if 'setAccessionNumber' in line: acn = line
            if 'setPatientFirstName' in line: fn = line
            if 'setPatientMiddleName' in line: mn = line
            if 'setPatientLastName' in line: ln = line
            if 'setPatientMedicalID' in line: mrn = line

      # Clean up line that has the proper fields 
      acn = acn[acn.find("'")+1:acn.rfind("'")]
      fn = fn[fn.find("'") + 1:fn.rfind("'")]
      mn = mn[mn.find("'") + 1:mn.rfind("'")]
      ln = ln[ln.find("'") + 1:ln.rfind("'")]
      mrn = mrn[mrn.find("'") + 1:mrn.rfind("'")]

      # Create array
      studies.append({"server": s, "file": file, "rw": modification_date(file), "path":dir+"/"+file, 'acc':acn, 'name':fn+" "+mn+" "+ln, 'mrn':mrn})

# Sort & Display studies based on date
studies.sort(key=lambda x:x['rw'])
for val in studies:
   print (val['server']+" | "+str(val['rw'])+" | "+val['name']+" | "+val['acc']+" | "+val['mrn']+" | "+val['file'])