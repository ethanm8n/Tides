import json
import requests
import time
from datetime import datetime
from datetime import date
from dateutil.parser import isoparse
from uniplot import plot
import os
import sys

if __name__ == '__main__':
    pass
else:
    sys.exit('File was run as a module, exiting...')

# Canadian Hydrographic Service API URL. (See https://api-iwls.dfo-mpo.gc.ca/swagger-ui/ for reference.)
url = 'https://api-iwls.dfo-mpo.gc.ca/api/v1/'

# GET header(s).
headers = {
    'Content-Type': 'text/json; charset=utf-8',
}

# My coordinates.
lat = 49.275
lon = -123.132
summedCoordinates = lat + lon

# Return summed coordinates after calculating difference to my coordinates.
def getCoordinates(a):
    # When my coordinates are subtracted from other coordinates, closer values will approach 0.
    # Use abs() to convert negative numbers to positive in order for sort() to work properly.
    aCoordinates = abs(a['latitude'] + a['longitude'] - summedCoordinates)

    return aCoordinates;

# Get request for all stations in pacific region.
response = requests.request('GET', url + 'stations?chs-region-code=PAC', headers=headers)
stations = json.loads(response.text)

# Filter out unoperative stations.
operatingStations = list(filter(lambda x: x['operating'] is True, stations))

# Sort stations by proximity to my coordinates, modifies in-place.
operatingStations.sort(key=getCoordinates)

closestStationID = operatingStations[0]['id']

# Get the current date along with 24 hour period in which we want to extract tide data.
d = date.fromtimestamp(time.time()).isoformat()
fromTime = d + 'T00:00:00'
toTime = d + 'T23:00:00'

# Make GET request for station's tide height data in the current 24 hour period
tidesRequest = url + 'stations/' + closestStationID + '/data?time-series-code=wlo&from=' + fromTime + 'Z&to=' + toTime + 'Z'
stationMetadataResponse = requests.request('GET', tidesRequest, headers=headers)
closestStationData = json.loads(stationMetadataResponse.text)

# Track tide height by the hour.
timeSeries = list(map(lambda x: isoparse(x['eventDate']).hour, closestStationData))
heightSeries = list(map(lambda x: x['value'], closestStationData))

# Clear screen. (os.system('cls') for windows.)
os.system('clear')

# Plot 24 tide height data on graph.
plot(
    xs=timeSeries,
    ys=heightSeries,
    y_unit=' M',
    x_min=0,
    x_max=23,
    title=str(operatingStations[0]['officialName'] + ' Tide Levels ' + d)
)

lowTide = None
highTide = None

# Get low and high tide data.
for heightData in closestStationData:
    if lowTide is None:
        lowTide = heightData
    elif highTide is None:
        highTide = heightData
    elif heightData['value'] < lowTide['value']:
        lowTide = heightData
    elif heightData['value'] > highTide['value']:
        highTide = heightData

# Display information on high and low tides.
lowTideMessage = 'Low tide (' + str(lowTide['value']) + ' Meters) at ' + lowTide['eventDate']
highTideMessage = 'High tide (' + str(highTide['value']) + ' Meters) at ' + highTide['eventDate']

print(lowTideMessage, highTideMessage, sep='\n', end='\n')
