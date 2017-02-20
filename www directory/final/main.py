#!/usr/bin/python
import MySQLdb
import cv2

import config
import face
import hardware

import os
import RPi.GPIO as GPIO
import time

import glob
import sys
import select




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

def is_letter_input(letter):
	# Utility function to check if a specific character is available on stdin.
	# Comparison is case insensitive.
	if select.select([sys.stdin,],[],[],0.0)[0]:
		input_char = sys.stdin.read(1)
		return input_char.lower() == letter.lower()
	return False	

os.system("mjpg_streamer -i '/usr/lib/input_uvc.so -d /dev/video0 -y -r 640x480 -f 15' -o '/usr/lib/output_http.so -p 8080 -w ./www'&")

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="raspberry", # your password
                      db="raspberry") # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor() 

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

path = "/var/www/final/visitors/"
folders = os.walk(path).next()[1]
if __name__ == '__main__':
	
	print 'Training data loaded!'
	# Initialize camera and box.
	
	while True:
		# Check if capture should be made.
		# TODO: Check if button is pressed.
			input_state = GPIO.input(18)
			if input_state == False:
				os.system("sudo python kill_proc.py mjpg_streamer")
				camera = config.get_camera()
				os.system('sudo php button.php')
				test=False
				for folder in folders:
					# Load training data into model
					os.chdir(path+folder)
					print '#########'
					print os.getcwd()
					print '#########'
					print 'Loading training data...'
					model = cv2.createEigenFaceRecognizer()
					model.load(config.TRAINING_FILE)
					print 'Button pressed, looking for face...'
					# Check for the positive face and unlock if found.
					image = camera.read()
					# Convert image to grayscale.
					image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
					# Get coordinates of single face in captured image.
					result = face.detect_single(image)
					if result is None:
						print 'Could not detect single face!  Check the image in capture.pgm' \
							  ' to see what was captured and try again with only one face visible.'
						continue
					x, y, w, h = result
					# Crop and resize image to face.
					crop = face.resize(face.crop(image, x, y, w, h))
					# Test face against model.
					label, confidence = model.predict(crop)
					print 'Predicted {0} face with confidence {1} (lower is more confident).'.format(
						'POSITIVE' if label == config.POSITIVE_LABEL else 'NEGATIVE', 
						confidence)
					if label == config.POSITIVE_LABEL and confidence < config.POSITIVE_THRESHOLD:
						print 'Recognized face!'
						test=True
						with open('name.txt', 'r') as myfile:
							name=myfile.read()
						name1=name.replace(' ', '_')
						os.system("espeak '"+name1+"_sonne_a_la_porte' -vfr+f5  -s115")
						os.system("curl -u sqkCZHJZY71PLZsSmaczC1ptXl0Yn7u8: https://api.pushbullet.com/v2/pushes -d type=note -d title='Raspi-Security' -d body='"+name+" vient de vous rendre visite'")
						cur.execute("UPDATE visitors SET nb_visits = nb_visits+1 WHERE name = %s",name)
						cur.execute("UPDATE visitors SET last_visit = %s WHERE name = %s",(time.strftime("%Y/%m/%d"),name))
						cur.execute("UPDATE visitors SET pre = 1 WHERE name = %s",name)
						db.commit()
						break
					else:
						print 'Did not recognize face!'
				if test == False:
					camera = config.get_camera()
					print 'Cannot find this visitor in the database'
					print 'Adding to database'
					path = "/var/www/final/visitors/"
					automated_folder_creation(path)
					new_path=path+'person_'+str(finding_last_folder(path))+'/'
					print new_path
					# Prefix for positive training image filenames.
					POSITIVE_FILE_PREFIX = 'positive_'
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
					while i<6:
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
					cur.execute("INSERT INTO visitors (`name`, `nb_visits`, `last_visit`, `folder`, `pre`) VALUES ('---','1',%s,%s,'1')",((time.strftime("%Y/%m/%d"),new_path)))
					db.commit()
					os.system('sudo python /var/www/final/train_new.py '+new_path)
					os.system("curl -u sqkCZHJZY71PLZsSmaczC1ptXl0Yn7u8: https://api.pushbullet.com/v2/pushes -d type=note -d title='Raspi-Security' -d body='Un nouveau visiteur sonne a la porte'")
					os.system("espeak 'un_nouveau_visiteur_vient_de_vous_visiter' -vfr+f5  -s115")
					os.chdir('/var/www/final/')
