#
# https://github.com/Jumaily
# Python 3
#

import sqlite3
import datetime
from time import gmtime, strftime

conn = sqlite3.connect('salaries.db')
c = conn.cursor()

rows = c.execute("SELECT id,hire_date FROM salaries").fetchall()
for row in rows:
   dbid = row[0]
   dbdate = str(row[1])
   
   # some dates are empty, make sure there is a value.
   if dbdate:
      ndate = dbdate.split('/')
      yr = int(ndate[2])
      mo = ndate[0]
      dy = ndate[1]
      cyr = int(strftime("%y", gmtime()))

      if yr<=cyr: yr+=2000
      else: yr+=1900
      newdate = (str(yr) +"-"+ mo +"-"+ dy)
      
      c.execute('''UPDATE salaries SET datehire=? WHERE id=?''', (newdate,dbid))
      # Save Changes to DB
      conn.commit()

      # for debuggin
      # print("Updating row: ", dbid)

conn.close()