"""
This module creates web map with friends locations on it.
"""

import requests
import folium

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable


def get_json(bearer_token: str, screen_name: str, count: str) -> dict:
    """
    Return .json object using Twitter API using bearer token.

    >>> get_json('d', '@opop', '2')
    {'errors': [{'code': 89, 'message': 'Invalid or expired token.'}]}
    """

    base_url = 'https://api.twitter.com/'
    endpoint = '1.1/friends/list.json'

    if screen_name == '':
        screen_name = '@BarackObama'
    if count == "":
        count = '2'

    search_url = f"{base_url}{endpoint}"

    search_headers = {
        'Authorization': f'Bearer {bearer_token}'
    }

    search_params = {
        'screen_name': screen_name,
        'count' : int(count)
    }

    response = requests.get(search_url,
                            headers=search_headers,
                            params=search_params)

    json_response = response.json()

    return json_response


def make_friends_list(json_data: dict) -> list:
    """
    Returns a list of tuples: [(screen_name, location), ...]
    from json data (.json object)

    >>> make_friends_list({\
    "users": [\
        {\
            "id": 22119703,\
            "id_str": "22119703",\
            "name": "Niki Jennings",\
            "screen_name": "nufipo",\
            "location": "Kyiv"\
            }]})
    [('nufipo', 'Kyiv')]
    """

    friends = []

    for friend in json_data['users']:
        location = friend['location']
        if location != '':
            friends.append( (friend['screen_name'], location) )
    return friends

def find_coordinates_by_name(name: str) -> tuple:
    """
    Return coordinates as a tuple from name of the place.

    >>> find_coordinates_by_name('Старі Кути')
    (48.287312, 25.1738)
    """



    geolocator = Nominatim(user_agent="webmap")

    location = geolocator.geocode(name)
    name = name.split(',')
    while not location:
        name = ','.join(name[1:])
        location = geolocator.geocode(name)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0)
    return location.latitude, location.longitude


def transform_list(friends: list) -> list:
    """
    Returns a list: [(screen_name, (lat, lon)), ...] from
    [(screen_name, location), ...].

    >>> transform_list([('nufipo', 'Старі Кути')])
    [('nufipo', (48.287312, 25.1738))]
    """

    friends_coord = []
    for friend in friends:
        try:
            friends_coord.append( (friend[0],
                                find_coordinates_by_name(friend[1])) )
        except GeocoderUnavailable:
            continue
    return friends_coord


def transform_to_dict(friends_coord: list) -> dict:
    """
    Return a dict: {(lat, lon): {screen_name, ...}, ...} from
    [(screen_name, (lat, lon)), ...]

    >>> transform_to_dict([('nufipo', (48.287312, 25.1738))])
    {(48.287312, 25.1738): {'nufipo'}}
    """

    friends_dict = {}
    for friend in friends_coord:
        coord = friend[1]
        if coord in friends_dict:
            friends_dict[coord].add(friend[0])
        else:
            friends_dict[coord] = { friend[0] }
    return friends_dict

def generate_map(friends_dict: dict):
    """
    Generates map from dict: {(lat, lon): {screen_name, ...}, ...}.
    """

    my_map = folium.Map(tiles="Stamen Terrain",
                     zoom_start=3)
    fg_markers = folium.FeatureGroup(name="markers")

    for coord in friends_dict:
        lat = coord[0]
        lon = coord[1]
        screen_names = friends_dict[coord]
        fg_markers.add_child(folium.Marker(location=[lat, lon],
                                           popup = str(screen_names)[1:-1],
                                           icon=folium.Icon()))
    my_map.add_child(fg_markers)
    my_map.add_child(folium.LayerControl())
    my_map.save("tools/templates/friends_map.html")


def main(bearer: str, screen_name: str, count: str):
    """
    Runs a module.
    """

    json_data = get_json(bearer, screen_name, count)

    friends = make_friends_list(json_data)
    friends_coord = transform_list(friends)
    friends_dict = transform_to_dict(friends_coord)

    generate_map(friends_dict)


if __name__ == "__main__":
    # import doctest
    # print(doctest.testmod())
    bearertoken = input('Enter your bearer token: ')
    screenname = input('Enter screenname (press Enter for default value "@BarackObama"): ')
    countt = input('Enter count (press Enter for default value "2"): ')

    main(bearertoken, screenname, countt)
