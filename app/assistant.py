from flask_assistant import(ask, tell, permission, context_manager, request,
                            Context)
from app import assist, app, cache, logger, geo
from app.salah_com_fetcher import GetEventTime
from app.models import Event


app.config['ASSIST_ACTIONS_ON_GOOGLE'] = True

@assist.action('welcome', events=['WELCOME'])
def greet():
    return ask('Assalamu Alaykum! Ask a prayer time to get started')


@assist.action('prayer-time', mapping={'city': 'sys.geo-city',
                'state': 'sys.geo-state-us', 'country': 'sys.geo-country'})
def tell_prayer_time(event, city=None, state=None, country=None):
    if city is None:
        user_id = _get_user_id()
        data = cache.get(user_id)
        if data is None:
            context_manager.add('request_permission',
                                {'event': event, 'user_id': user_id}, 1)
            return permission(['DEVICE_PRECISE_LOCATION'],
                    'To get you accurate timings')
        else:
            lat, lng, city = data['lat'], data['lng'], data['city']
            return _tell_prayer_time_internal(event, lat, lng, city)
    else:
        (lat, lng) = geo.geolocation_from_place(city, state, country)
        return _tell_prayer_time_internal(event, lat, lng, city) \
            if all([lat, lng]) \
            else ask("Sorry, we couldn't understand your location. \
                Please try again.")


@assist.prompt_for('event', intent_name='prayer-time')
def prompt_event():
    return ask('Sorry, which prayer was that?')


@assist.action('permission-fallback', is_fallback=True,
               with_context=['request_permission'])
def call_tell_prayer_time():
    if _is_permission_granted():
        event = context_manager.get_param('request_permission', 'event')
        user_id = context_manager.get_param('request_permission', 'user_id')
        coordinates = request['originalRequest']['data'] \
                      ['device']['location']['coordinates']
        lat, lng = coordinates['latitude'], coordinates['longitude']
        city = geo.city_from_geolocation(lat, lng)
        cache.set(user_id, {'lat': lat, 'lng': lng, 'city': city})
        return _tell_prayer_time_internal(event, lat, lng, city)
    else:
        return tell("Sorry, I can't get prayer times for you")


@assist.action('clear-location')
def clear_location():
    user_id = _get_user_id()
    logger.debug('clearing location for user_id=%s', user_id)
    cache.set(_get_user_id(), None)
    return tell('Okay, your location has been cleared')


@assist.action('fallback', is_fallback=True)
def tell_usage():
    return ask('Sorry, I did not understand that. You can ask things like \
               "What time is Maghrib?" or "When is Zuhr in San Ramon, \
               California?"')


def _tell_prayer_time_internal(event_name, lat, lng, city):
    time = GetEventTime(event_name, lat, lng)
    logger.debug('event=%s, lat=%s, lng=%s, city=%s, time=%s', event_name, lat, lng, city, time)
    event = Event.from_event_name(event_name)
    template = '{{}} is at {} in {}'.format(time, city)
    speech = template.format(event.speech)
    display_text = template.format(event.display_text.capitalize())
    return tell(speech, display_text)


def _is_permission_granted():
    try:
        args = next(input['arguments'] for input in
                    request['originalRequest']['data']['inputs']
                    if input['intent'] == 'actions.intent.PERMISSION')

        return [] != [arg for arg in args
                if arg['textValue'] == 'true' and arg['name'] == 'PERMISSION']
    except:
        return False

def _get_user_id():
    return request['originalRequest']['data']['user']['userId']


