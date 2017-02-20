import glob
import os
import sys
import select
import time
import cv2
import MySQLdb
import hardware
import config
import face


#Create new path for user
def folder_create(path):
    if not os.path.exists(path):
        os.makedirs(path)

def automated_folder_creation(path):
	os.chdir(path)
	if not os.path.exists("./person_0"):
		os.makedirs("./person_0")
	else:
		os.makedirs("person_"+str(finding_last_folder("./")+1))
		
def finding_last_folder(path):
    folders = os.walk(path).next()[1]
    folders_index = [int(folder[7:]) for folder in folders]
    folders_index.sort()
    return folders_index[-1]

path = "/var/www/final/visitors/"

automated_folder_creation(path)
new_path=path+'person_'+str(finding_last_folder(path))
print new_path
	
# Prefix for positive training image filenames.
POSITIVE_FILE_PREFIX = 'positive_'


def is_letter_input(letter):
	# Utility function to check if a specific character is available on stdin.
	# Comparison is case insensitive.
	if select.select([sys.stdin,],[],[],0.0)[0]:
		input_char = sys.stdin.read(1)
		return input_char.lower() == letter.lower()
	return False


if __name__ == '__main__':
	camera = config.get_camera()
	box = hardware.Box()
	# Create the directory for positive training images if it doesn't exist.
	if not os.path.exists(new_path):
		os.makedirs(new_path)
	# Find the largest ID of existing positive images.
	# Start new images after this ID value.
	files = sorted(glob.glob(os.path.join(new_path, 
		POSITIVE_FILE_PREFIX + '[0-9][0-9][0-9].png')))
	count = 0
	if len(files) > 0:
		# Grab the count from the last filename.
		count = int(files[-1][-7:-4])+1
	print 'Capturing positive training images.'
	i=0
	while i<10:
		# Check if button was pressed or 'c' was received, then capture image.
		print 'Capturing image...'
		image = camera.read()
		# Convert image to grayscale.
		image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
		# Get coordinates of single face in captured image.
		result = face.detect_single(image)
		if result is None:
			print 'Could not detect single face!  Check the image in capture.png' \
				  ' to see what was captured and try again with only one face visible.'
			continue
		x, y, w, h = result
		# Crop image as close as possible to desired face aspect ratio.
		# Might be smaller if face is near edge of image.
		crop = face.crop(image, x, y, w, h)
		# Save image to file.
		filename = os.path.join(new_path, POSITIVE_FILE_PREFIX + '%03d.png' % count)
		cv2.imwrite(filename, crop)
		print 'Found face and wrote training image', filename
		count += 1
		i += 1
		time.sleep(0.4)
	db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="raspberry", # your password
                      db="raspberry") # name of the data base
	# you must create a Cursor object. It will let
	#  you execute all the queries you need
	cur = db.cursor() 
	os.system('sudo python /var/www/final/train_new.py '+new_path)
	cur.execute("INSERT INTO visitors (`name`, `nb_visits`, `last_visit`, `folder`, `pre`) VALUES ('---','1',%s,%s,'1')",((time.strftime("%Y/%m/%d"),new_path)))
	db.commit()
