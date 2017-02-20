import sys
import os


k=len(sys.argv)
#!/usr/bin/python
path = sys.argv[1]
# Open a file
os.chdir(path)
fo = open("name.txt", "wb")

if (k == 4):
	name1 = sys.argv[2]
	name2 = sys.argv[3]
	fo.write(name1+' '+name2)
	
elif (k == 5):
	name1 = sys.argv[2]
	name2 = sys.argv[3]
	name3 = sys.argv[4]
	fo.write(name1+' '+name2+' '+name3)

# Close opend file
fo.close()