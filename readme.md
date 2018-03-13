py-sporstracker
=

Python library dedicated to interact with Sports Tracker App

Instalation
-
	pip install git+git://github.com/prezesp/py-sporstracker.git

Usage
-

```python
from sportstracker import SportsTrackerLib

stlib = SportsTrackerLib()
stlib.login('USER', 'PASS')

# print number of my workouts
print(len(stlib.get_workouts()))

# add workout
filename = "my-great-training.gpx"
with open(filename) as f:
	gpx = f.read()
	stlib.add_workout(filename, gpx)

```