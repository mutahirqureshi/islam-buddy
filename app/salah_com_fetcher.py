"""Fetches prayer times from 'www.salah.com'."""

import json
import requests
from app import logger

_SALAH_API_URL = 'http://www.salah.com/times/get'
'''
The 'salah.com' API provides a response in the following format:
"Prayers": {
  "2017": { "5": { 17": {
    # actual prayer times yere
    "Fajr": "5 AM"
    ...
  }}}
}
The depth of the useful information (prayer times) is at level 4
'''
_PRAYER_TIMES_RESPONSE_DEPTH = 3


def GetDailyPrayerTimes(lat, lng):
  """Gets the daily prayer times from 'salah.com'.

  Performs a POST request on the salah.com prayer times API
  to get today's prayer times (local to timezone of provided
  location).

  Args:
    lat: a double representing the latitude
    lng: a double representing the longitude

  Returns: a dict containing of daily prayer times
  """
  # set up the parameters in the format expected by 'salah.com'
  post_data = {
      'lt': lat,
      'lg': lng,
  }

  try:
    response = requests.post(_SALAH_API_URL, data=post_data, timeout=15)
    response.raise_for_status()
    payload = response.json()
    logger.debug('salah.com response=%s', json.dumps(payload, indent=2))
    # dig into the response until we find the prayer times
    payload = payload['Prayers']
    while len(payload) == 1: payload = payload.itervalues().next()
    return payload
  except requests.exceptions.HTTPError as err:
    logger.error(err)
    return {}
  except:
    return {}

def GetEventTime(event, lat, lng):
  times = GetDailyPrayerTimes(lat, lng)
  logger.debug('times=%s', json.dumps(times, indent=2))
  return times[event]
