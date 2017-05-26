from builtins import filter
import googlemaps


# TODO: store Google client key in environment variable for security
gmaps = googlemaps.Client(key='AIzaSyCqk8iX6cGYqEreeAofxVJw-RIJNFHSD6o')

def geolocation_from_place(city, state, country):
    geo_components = filter(None, (city, state, country))
    payload = gmaps.geocode(', '.join(geo_components))
    location = payload[0]['geometry']['location']
    return (location['lat'], location['lng'])


def city_from_geolocation(lat, lng):
    payload = gmaps.reverse_geocode((lat, lng))
    return next(address_component['long_name'] for address_component in
                payload[0]['address_components']
                if address_component['types'][0] == 'locality')

