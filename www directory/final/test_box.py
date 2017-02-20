"""Raspberry Pi Face Recognition Treasure Box
Treasure Box Script
Copyright 2013 Tony DiCola 
"""
#!/usr/bin/python
import MySQLdb
import cv2

import config
import face
import hardware

import os
import RPi.GPIO as GPIO
import time


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
	camera = config.get_camera()
	while True:
		# Check if capture should be made.
		# TODO: Check if button is pressed.
			input_state = GPIO.input(18)
			if input_state == False:
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
						cur.execute("UPDATE visitors SET nb_visits = nb_visits+1 WHERE name = %s",name)
						cur.execute("UPDATE visitors SET last_visit = %s WHERE name = %s",(time.strftime("%Y/%m/%d"),name))
						cur.execute("UPDATE visitors SET pre = 1 WHERE name = %s",name)
						db.commit()
						break
					else:
						print 'Did not recognize face!'
				if test == False:
					print 'Cannot find this visitor in the database'
					print 'Adding to database'
					os.chdir('/var/www/final/')
					
					os.system('sudo python create_new.py')
					
