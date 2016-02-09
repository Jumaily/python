# python 3
import glob, os, csv, mysql.connector

# Clean strings/inputs for Database
def clnstr(s):
    s = str(format(s))
    return "".join(filter(lambda x: ord(x)<128, s))

# Database Config
config = {'user': ‘user’, 'password': 'pass1234','host': 'localhost',
          'database': 'am', 'raise_on_warnings': True}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Clears out table first
cursor.execute("TRUNCATE TABLE cct")

# Read all files in directory
path = ‘/path/to/csv/files’
fnum = 0
lnum = 0
totalfilesindir = len([item for item in os.listdir(path) if os.path.isfile(os.path.join(path, item))])

for file in sorted(glob.glob(path + "/*")):
    fnum += 1
    TotPer = round((fnum/totalfilesindir)*100)

    print("%d/%d (%d%%) - Opening file: %s " % (fnum, totalfilesindir, TotPer, file))

    fn = open(file, 'r', encoding="utf8")
    reader = csv.reader(fn)
    for row in reader:
        # make sure correct length
        if (len(row) == 28):

            # Validate State (two letter)
            state = '' if len(list(row[22])) > 2 else clnstr(row[22])

            sql = ("INSERT INTO cct (Account, AccountName, AmountMoney, AuthCode, AVS, BrandType, CardEndingIn, CVDI, FirstName, " \
                   "LastName, MerchTransID, OptionCode, Date, TINID, ConfNumber, ErrorCode, AuthType, Type, City, Country, " \
                   "Email, State, Address, Zip, IP) VALUES " \
                   "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                   (clnstr(row[0]), clnstr(row[1]), clnstr(row[2]), clnstr(row[3]), clnstr(row[4]), clnstr(row[5]),
                   clnstr(row[6]), clnstr(row[7]), clnstr(row[8]), clnstr(row[9]), clnstr(row[10]),
                   clnstr(row[11]), clnstr(row[12]), clnstr(row[13]), clnstr(row[14]), clnstr(row[15]),
                   clnstr(row[16]), clnstr(row[17]), clnstr(row[18]), clnstr(row[19]), clnstr(row[20]),
                   state, clnstr(row[23]), clnstr(row[25]), clnstr(row[26])))
            cursor.execute(*sql)
            cnx.commit()
            lnum += 1
    fn.close()

print("\nTotal files read: ", fnum)
print("Total lines read: ", format(lnum, ',d'))
print("\t----------- DONE ---------- \t\n")
cursor.close()
cnx.close()
