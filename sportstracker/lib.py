import requests
import json
import logging

from sportstracker.sharing_type import Sharing

API_URL = 'https://api.sports-tracker.com/apiserver/v1'
API_LOGIN_URL = "{}/login".format(API_URL)
API_IMPORT_URL = "{}/workout/importGpx".format(API_URL)
API_COMMIT_URL = "{}/workouts/header".format(API_URL)
API_FETCH_URL = "{}/workouts?sortonst=true&limit={{}}&offset={{}}".format(API_URL)

class SportsTrackerLib:

	""" Communicate with the unofficial SportsTracker API Server """

	def login(self, user, password):
		""" Obtains token to authenticate user and saves internally """

		headers = {
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		data = 'l='+user+'&p='+password

		resp = requests.post(API_LOGIN_URL, headers=headers, data=data)
		if resp.status_code == 200:
			self.token = resp.json()['sessionkey']
			logging.debug('Token was obtained: ' + self.token)
		else:
			raise Exception("Login failed")


	def add_workout(self, name, gpx, sportId=1, description='', sharing=Sharing.PUBLIC, distance=None, duration=None):
		""" Adds workout to system """

		# Upload GPX file
		headers = {
			'STTAuthorization': self.token
		}
		resp = requests.post(API_IMPORT_URL, headers=headers, files=[('file', (name, gpx, 'application/gpx+xml'))])
		workout_header = WorkoutHeader(resp.json()['payload'], sportId, description, sharing, distance, duration)
		logging.debug('Workout key was obtained: ' + workout_header.workoutKey)
		
		# Commit workout
		headers['Content-Type'] ='application/json' 
		resp = requests.post(API_COMMIT_URL, headers=headers, data=workout_header.toJSON())
		if resp.status_code == 200:
			logging.info('Successfully added to SportsTracker')

	def get_workouts(self, limit=10, offset=0):
		""" Retrieves list of latest users workouts"""

		headers = {
			'STTAuthorization': self.token
		}
		resp = requests.get(API_FETCH_URL.format(limit, offset), headers=headers)

		return resp.json()['payload'] 
		

class WorkoutHeader:

	""" Represents temporary workout object before commiting it to SportsTracker """

	def __init__(self, data, sportId, description, sharing, distance, duration):
		self.data = dict()

		fields = (
			'energyConsumption', 'startTime',
			'totalDistance', 'totalTime', 'workoutKey'
		)
		
		for f in fields:
			if f == 'totalDistance':
				self.data[f] = distance
			elif f == 'totalTime':
				self.data[f] = duration
			else:
				self.data[f] = data[f]

		self.data['activityId'] = str(sportId)
		self.data['sharingFlags'] = str(sharing.value)
		self.data['description'] = description
	
	def __getattr__(self, name):
		try:
			return self.data[name]
		except KeyError:
			raise AttributeError(name)
	
	def toJSON(self):
		return '[' + json.dumps(self, default=lambda w: w.data, sort_keys= True) +']11'
	
