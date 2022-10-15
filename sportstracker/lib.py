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
		data = 'l='+user+'&p='+password+'&captchaToken='+'03ANYolqt6U8dxgXg94q-8IqEw_O-GoBlKWZgSwjI5mJF8s2s3o-HXLPAZTDD4YfbdEzP-DKtRzr7TUFRMzDRVs45G3NFa4dm7ia5yVvh71aKspqZjSTV3WcqCSCubsVmHC2T9CClM6P1SNb4d4JKgH1F4GqAQrrlCYxjDZG7SiS-4aMoZtVHlieqbmjRg2eSyiijCX74o-ajJP0svfOQxVsE06n8-HUyXmz355eE-zhC2VeMCuiL1CxxxPmwd8VvYU3-sD2C9iCB2Z8zLxp1ZDwRjsJY6-K26i3LEipsG-Hyeedp9Bv0o61cuF8Sq0X5WU6IUZHoOxpjCmQU5dBXjYuQV95rGRrgBXbXJK1YigpmgTwfRHTCNscmpgWVSJQ_dRObRs9C53dCl9FlMB5YdWyXNcQYLvN1O4lkQeQYRjgJaQCVctSImZn5qk5ohXElYjw6Z3uAalkYdZgQv0gw2tZj7yPwOtbj4Uhp8zJLjRxSmeuXJMurigoHeFByiMRGSIbY4SMOAcc1Q8IhUXPjIm4BiKoqB1ereiJdVsBklFU-rcSaIssiKM1QMvEr1XEvRIT6twh6QwbJImL73UmCtbqTBO9ppSq7qhouRD3n5UczM8RobeNZtt2YAR3DIhJCVq1GgE8ZdMwGxXoIGCKgW2A5shfgRa4mr2JSEBcWX8nB3xd64Wv-XOuJ_f8F0XIgyv8Rf3o0rlQu_G0YBv0xh4naA1eYppGwjxukBGZcuLPKVQO-bMKupKNhvIvfMZkCfkAQCGc3cK0jbJc_Q8jmJXbvq8bIEA7hf99InGY0gv2V1dfMf4PvE5OwlAIO5BMIoTSgmXtSMMgb5Iv3jK1VXyHwMjUTmRBmfPJ_qV4hBlHWeTd8xLke1C9Cbn31UUF_wPFu522U9r5-8ASnoiU8EQpxHcz7XgxF17TqP4XLSgT-7J8Q284CHreVz5hp0t0-xz67sOz9bBQgoaxOSph_OB1tDmbaCMxDfHqStaS9JTfTSob7lMZHfrHMozRV3Z8eTtrscd_B_pLUXM5JKlGkGTagHnY4togrqL2V2v4fohZRspLiVlBVxi46UL1PJ4slTJ1r-kGkrOrZScUSdtgpyDhhJaXObQg6t36F4HV5APIX3QJnEZrskc877W27gSYnQPnJrwW40ttDKc_UxWmX43BNpQVkq122yLA'

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
	
