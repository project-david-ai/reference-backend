import os
import requests
from dotenv import load_dotenv
from backend.app.services.api_service_internal.project_david.user_location_service import UserLocationService

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API")
BASE_URL = os.getenv("GOOGLE_MAPS_BASE_URL_PROD")


class GoogleGeocodingService:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.reverse_geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        self.elevation_url = "https://maps.googleapis.com/maps/api/elevation/json"

        self.user_location_service = UserLocationService()

    def get_last_seen_user_location(self, faux_identity, limit):

        last_seen_user_location = self.user_location_service.get_user_locations(faux_identity=faux_identity, limit=limit)

        return last_seen_user_location

    def geocode(self, address):
        params = {
            'address': address,
            'key': self.api_key
        }
        response = requests.get(self.geocode_url, params=params)
        geocode_data = response.json()

        if geocode_data['status'] == 'OK':
            formatted_address = geocode_data['results'][0]['formatted_address']
            location = geocode_data['results'][0]['geometry']['location']
            url = self.compose_url("geocode", address=address)
            return {"formatted_address": formatted_address, "location": location, "url": url}
        else:
            raise Exception(f"Geocoding error: {geocode_data['status']}")

    def reverse_geocode(self, lat, lng):
        params = {
            'latlng': f"{lat},{lng}",
            'key': self.api_key
        }
        response = requests.get(self.reverse_geocode_url, params=params)
        geocode_data = response.json()

        if geocode_data['status'] == 'OK':
            formatted_address = geocode_data['results'][0]['formatted_address']
            url = self.compose_url("reverse-geocode", lat=lat, lng=lng)
            return {"formatted_address": formatted_address, "url": url}
        else:
            raise Exception(f"Reverse geocoding error: {geocode_data['status']}")

    def find_places_nearby(self, location, radius, type):
        params = {
            'location': f"{location['lat']},{location['lng']}",
            'radius': radius,
            'type': type,
            'key': self.api_key
        }
        response = requests.get(self.places_url, params=params)
        places_data = response.json()

        if places_data['status'] == 'OK':
            places = places_data['results']
            url = self.compose_url("places-nearby", lat=location['lat'], lng=location['lng'], radius=radius, type=type)
            return {"places": places, "url": url}
        else:
            raise Exception(f"Places API error: {places_data['status']}")

    def get_distance_matrix(self, origins, destinations):
        params = {
            'origins': '|'.join([f"{origin['lat']},{origin['lng']}" for origin in origins]),
            'destinations': '|'.join([f"{destination['lat']},{destination['lng']}" for destination in destinations]),
            'key': self.api_key
        }
        response = requests.get(self.distance_matrix_url, params=params)
        distance_data = response.json()

        if distance_data['status'] == 'OK':
            return {"distance_matrix": distance_data['rows']}
        else:
            raise Exception(f"Distance Matrix API error: {distance_data['status']}")

    def get_elevation(self, locations):
        params = {
            'locations': '|'.join([f"{location['lat']},{location['lng']}" for location in locations]),
            'key': self.api_key
        }
        response = requests.get(self.elevation_url, params=params)
        elevation_data = response.json()

        if elevation_data['status'] == 'OK':
            url = self.compose_url("elevation", lat=locations[0]['lat'], lng=locations[0]['lng'])
            return {"elevations": elevation_data['results'], "url": url}
        else:
            raise Exception(f"Elevation API error: {elevation_data['status']}")

    def compose_url(self, endpoint, **params):

        # base_url = "http://localhost:3000/"

        url = BASE_URL + endpoint + "?"
        url += "&".join([f"{key}={value}" for key, value in params.items()])
        return url

    def get_current_location_by_gps(self, faux_identity, limit):

        user_gps_location = self.get_last_seen_user_location(faux_identity=faux_identity, limit=limit)

        user_gps_location = user_gps_location[0]

        lat, lng = user_gps_location['latitude'], user_gps_location['longitude']

        current_location = self.get_data_and_url("reverse-geocode", lat=lat, lng=lng)

        current_location['latitude'] = lat
        current_location['longitude'] = lng

        return current_location

    def get_places_near_by_gps(self, faux_identity, limit, place):

        user_gps_location = self.get_last_seen_user_location(faux_identity=faux_identity, limit=limit)

        user_gps_location = user_gps_location[0]

        lat, lng = user_gps_location['latitude'], user_gps_location['longitude']

        data = self.find_places_nearby({'lat': lat, 'lng': lng}, 1500, place)

        print(data)

        return data

    def get_data_and_url(self, endpoint, **params):

        if endpoint == "geocode":
            return self.geocode(**params)
        elif endpoint == "reverse-geocode":
            return self.reverse_geocode(**params)
        elif endpoint == "places-nearby":
            return self.find_places_nearby(**params)
        elif endpoint == "distance-matrix":
            return self.get_distance_matrix(**params)
        elif endpoint == "elevation":
            return self.get_elevation(**params)
        else:
            raise Exception(f"Invalid endpoint: {endpoint}")


if __name__ == "__main__":
    faux_identity = '6bd0041a-0f68-439c-a054-9b735142982c'  # Replace with the desired faux identity
    limit = 1
    place = 'restaurant'
    service = GoogleGeocodingService()
    service.get_current_location_by_gps(faux_identity, limit)
    service.get_places_near_by_gps(faux_identity, limit, place)

