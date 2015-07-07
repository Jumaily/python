# python 3
import mysql.connector

# Build Human Chromosome array
chrs = []
for i in range(1,23): chrs.append(i)
chrs.extend({'X','Y'})

rng = 1000
# rslt = []
# for i in range(0,(2*(rng+1))): rslt.append(i)

# Database Config
config = {
		'user': 'username',
		'password': 'passwd',
		'host': 'localhost',
		'database': 'databasename',
		'raise_on_warnings': True,
		}
cnx = mysql.connector.connect(**config)

# Search Settings
ReadTable = "mdamb231_mr"
tblprx = [1,10]
cntx = ['cg','cwg']
limit = ''#'LIMIT 1'

# Create file to output results to
resultfile = open("results.csv", "w")
resultfile.write("Table Read From, Chromosome, Context, Total Rows In Table, Total Overlaps\n")

# Table
for tbl in tblprx:
	# Context
	for cnt in cntx:
		# Chromosome - Run initial search loop & create arrays for each
		for c in chrs:
			# Create the array for each chromosome
			cstart = []
			sqls = ("SELECT chromStart FROM databasename.%s%s WHERE context LIKE '%s' && chrom LIKE 'chr%s' ORDER BY chromStart %s"
								 % (ReadTable, tbl, cnt, c, limit))
			cur = cnx.cursor()
			cur.execute(sqls)
			rows = cur.fetchall()

			print('Total Row(s) in Table %s%s: %s Context: %s, Chromosome: %s' % (ReadTable, tbl, cur.rowcount, cnt, c))
			resultfile.write('%s%s, Chr%s, %s, %s, ' % (ReadTable, tbl, c, cnt, cur.rowcount))

			# Build array of results
			for row in rows: cstart.append(row[0])
			cur.close()

			# make each result number into a center to search in the query
			TOvLap = 0
			for ctr in cstart:
				if((ctr-rng)<1):
					lw = 0
					hi = 2 * ctr
				else:
					lw = ctr - rng
					hi = ctr + rng

				sqls_rng = ("SELECT COUNT(*) AS CResult FROM databasename.%s%s WHERE (context LIKE '%s' && chrom LIKE 'chr%s')"
					" && (chromStart BETWEEN %s AND %s) ORDER BY chromStart %s"
							% (ReadTable, tbl, cnt, c, lw, hi, limit))
				cur = cnx.cursor()
				cur.execute(sqls_rng)
				rows = cur.fetchall()
				TOvLap += rows[0][0]

			resultfile.write('%r\n' % (TOvLap))

cnx.close()
resultfile.close()
print ("\n\t----------- DONE ---------- \t\n")