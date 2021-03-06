# Intent handler for 'WHEN_IS_START_TIME_INTENT'

import response_builder
import gmaps_API
from prayer_info import PrayerInfo
import util


class StartTimeIntentHandler(object):

  INTENTS_HANDLED = [
      'WHEN_IS_START_TIME_INTENT',
      'PERMISSION_INTENT',
  ]

  def __init__(self, prayer_info, fake_db):
    self.prayer_info_ = prayer_info
    self.fake_db_ = fake_db


  def _EncodeParameter(self, param):
    return ' '.join(param).encode('utf-8')


  def _GetContext(self, post_params, context_name):
    for candidate in post_params.get('result').get('contexts'):
      if candidate['name'] == context_name:
        return candidate
    return None


  def HandleIntent(self, device_params, post_params):
    """Returns a server response as a dictionary."""
    
    # filled if we have the user's city, country and/or state
    params = post_params.get('result').get('parameters')
    city = params.get('geo-city')
    country = params.get('geo-country')
    state = params.get('geo-state-us')

    # filled if we have the user's lat/lng
    has_location = 'location' in device_params
    # this will only be populated if the intent type is PERMISSION_REQUEST
    permission_context = None

    if not has_location:
      # this should always be filled since its a required parameter to the intent
      # the only time it won't be filled is on PERMISSION_REQUEST intents
      desired_prayer = params.get('PrayerName')
    else:
      # this should be filled on PERMISSION_REQUEST intents in the relevant context
      permission_context = self._GetContext(post_params, 'requ')
      print 'permission context = ', permission_context 
      desired_prayer = permission_context.get('parameters').get('PrayerName')
      

    # this should also always be available
    user_id = post_params.get('originalRequest').get('data').get('user').get('userId')

    # if there is no city or location, we won't be able to do anything
    # so request the user for permissions to use their location
    if not (city or has_location):
      # do not ask for permission if we've already asked for it before
      permission_context = self._GetContext(post_params, 'actions_intent_permission')
      if (permission_context and 
          permission_context.get('parameters').get('PERMISSION') == 'false'):
        # if we are here it means the user rejected our request to use location
        return {'speech': ('Sorry, I\'ll need a location in order to get a prayer time.'
                           ' You can also try asking prayer times for a city next time.')}

      # the user has specified a state or country but not a city, then we should
      # instruct them to tell us a city name.
      if state or country:
        return {'speech': ('Sorry, I don\'t have enough information. Please try '
                           'again with a city next time.')}
      
      # at this stage, we don't know anything about the user's location - try
      # checking our db for a stored location
      user_info = self.fake_db_.GetUserInfo(user_id)
      if user_info and user_info.get('lat') and user_info.get('lng') and user_info.get('city'):
        print 'found user ', user_id, ' in databse, so location request is not necesary'
        lat = user_info.get('lat')
        lng = user_info.get('lng')
        city = user_info.get('city')
        return self._ComputePrayerTimeAndRespond(desired_prayer, lat, lng, city)

      else:
        print ('Could not find location in request, '
               'so responding with a permission request.')
        return response_builder.RequestLocationPermission()

    # we must fill these parameters in order to make a query to salah.com
    lat = None
    lng = None

    # if we have a city, then use this
    if city:
      print 'city:', city 
      print 'country:', country 
      print 'state:', state 
      city = self._EncodeParameter(params.get('geo-city'))

      if country:
        country = self._EncodeParameter(params.get('geo-country'))

      if state:
        state = self._EncodeParameter(params.get('geo-state-us'))

      location_coordinates = gmaps_API.GetGeocode(city, country, state)
      lat = location_coordinates.get('lat')
      lng = location_coordinates.get('lng')

    # if we have a device location, then use it
    elif has_location:
      if permission_context:
        location = device_params.get('location')
        city = location.get('city')
        lat = location.get('coordinates').get('latitude')
        lng = location.get('coordinates').get('longitude')
        user_info = {'city': city, 'lat': lat, 'lng': lng}
        self.fake_db_.AddOrUpdateUser(user_id, user_info)

      else:
        print 'Could not find relevant context!'

    return self._ComputePrayerTimeAndRespond(desired_prayer, lat, lng, city)


  def _ComputePrayerTimeAndRespond(self, desired_prayer, lat, lng, city):
    all_prayer_times = self.prayer_info_.GetPrayerTimes(lat, lng)
    canonical_prayer = util.StringToDailyPrayer(desired_prayer)
    prayer_time = \
       all_prayer_times.get(canonical_prayer)
    print 'prayer_times[', desired_prayer, "] = ", prayer_time 

    return self._MakeSpeechResponse(canonical_prayer, desired_prayer, prayer_time, city)


  def _MakeSpeechResponse(self, canonical_prayer, desired_prayer, prayer_time, city):
    print '_MakeSpeechResponse: ', canonical_prayer, desired_prayer, prayer_time, city
    if desired_prayer.lower() == 'suhur':
      return {'speech': 'Suhur ends at %s in %s' % (prayer_time, city)}
    elif desired_prayer.lower() == 'iftar':
      return {'speech': 'Today, iftar is at %s in %s' % (prayer_time, city)}
    else:
      print 'The time for %s is %s in %s.' % (util.GetPronunciation(canonical_prayer), prayer_time, city)
      return {
        'speech': 
            ('The time for %s is %s in %s.' % 
             (util.GetPronunciation(canonical_prayer), prayer_time, city))
      }

