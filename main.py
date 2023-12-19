import os
import requests
import googlemaps
import json
import time
import random

from dotenv import load_dotenv

def configure():
    """Load .env file
    """
    load_dotenv()

def get_user_input():
    """Get command line input of the place to search and the minimum rating.

    Returns:
        keyword (str): place to search
        min_rating (float): minimum rating
    """
    keyword = str(input('Where do you want to go? (cafe, restaurant, ...): '))
    min_rating = float(input('What is the minimum rating?:  '))
    while True:
        if min_rating < 0.0 or 5.0 < min_rating:
            min_rating = float(input('What is the minimum rating? (enter a float between 0 and 5):  '))
        else:
            break
    return keyword, min_rating

def get_current_location():
    """Gets current location from GeoJS API and returns coordinates.

    Returns:
        tuple: coordinates
    """
    geo_request_url = 'https://get.geojs.io/v1/ip/geo.json'
    response = requests.get(geo_request_url).json()
    current_location = (response.get('latitude'), response.get('longitude'))
    return current_location

def get_places_nearby(client, keyword, location, radius):
    """Gets all places within a certain radius from the clients's current location.

    Args:
        client (googlemaps Client): *refer to google maps API
        location (tuple): coordinates of the location
        radius (int): maximum distance from the location in meters

    Returns:
        list: list of places retrieved containing JSON in each entry
    """
    place_list = []
    response = client.places_nearby(
        location=location,
        keyword=keyword,
        radius=radius,
        open_now=True,
    )
    place_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

    while next_page_token:
        time.sleep(2)
        response = client.places_nearby(
            location=location,
            keyword=keyword,
            radius=radius,
            open_now=True,
            page_token=next_page_token
        )
        next_page_token=response.get('next_page_token')
        place_list.extend(response.get('results'))

    return place_list

def get_high_rating_places(places, min_rating):
    """Gets only the places that are rated above the minimum rating.

    Args:
        places (list): list of places containing JSON in each entry
        min_rating (float): the rating condition

    Returns:
        list: list of places above the minimum rating
    """
    place_list = []
    for place in places:
        name = place.get('name')
        place_id = place.get('place_id')
        rating = place.get('rating')
        price_level = place.get('price_level')
        latitude = place.get('geometry').get('location').get('lat')
        longitude = place.get('geometry').get('location').get('lng')
        place_object = {
            'name': name,
            'place_id': place_id,
            'rating': rating,
            'price_level': price_level,
            'latitude': latitude,
            'longitude': longitude
        }

        if rating > min_rating:
            place_list.append(place_object)
    return place_list

def get_random_place(places):
    """Chooses a random place and returns its coordinates.

    Args:
        places (list): a list of places

    Returns:
        tuple: coordinates of the chosen place
    """
    random_int = random.randint(0, len(places)-1)
    place_chosen = places[random_int]
    lat, lng = place_chosen.get('latitude'), place_chosen.get('longitude')
    return (lat, lng)

def main():
    configure()
    GMAPS_API_KEY = os.getenv('gmaps_api_key')
    map_client = googlemaps.Client(key=GMAPS_API_KEY)

    keyword, min_rating = get_user_input()
    current_location = get_current_location()
    max_distance = 1_000
    place_list = get_places_nearby(map_client, keyword, current_location, max_distance)
    high_rating_place_list = get_high_rating_places(place_list, min_rating)
    lat, lng = get_random_place(high_rating_place_list)
    print(f'http://maps.google.com/maps?q={lat},{lng}+(My+Point)&z=14&ll={lat},{lng}')

main()