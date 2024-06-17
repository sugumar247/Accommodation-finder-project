from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import  render, redirect, HttpResponse
from .forms import SearchForm
from django.http import JsonResponse
from .models import Booking
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from geopy.geocoders import ArcGIS, Nominatim
import math
from geopandas.tools import geocode
import pymongo
import requests


MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "Student"
COLLECTION_NAME = "Rooms"

client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


class BSTNode:
    def __init__(self, price):
        self.price = price
        self.accommodation_ids = []
        self.left = None
        self.right = None

class PriceBST:
    def __init__(self):
        self.root = None

    def insert(self, price, accommodation_id):
        if self.root is None:
            self.root = BSTNode(price)
            self.root.accommodation_ids.append(accommodation_id)
        else:
            self._insert_recursive(self.root, price, accommodation_id)

    def _insert_recursive(self, node, price, accommodation_id):
        if price < node.price:
            if node.left is None:
                node.left = BSTNode(price)
                node.left.accommodation_ids.append(accommodation_id)
            else:
                self._insert_recursive(node.left, price, accommodation_id)
        elif price > node.price:
            if node.right is None:
                node.right = BSTNode(price)
                node.right.accommodation_ids.append(accommodation_id)
            else:
                self._insert_recursive(node.right, price, accommodation_id)
        else:
            node.accommodation_ids.append(accommodation_id)

    def search(self, price):
        results = []
        self._search_recursive(self.root, price, results)
        return results

    def _search_recursive(self, node, price, results):
        if node is None or price is None:
            return
        node_price = int(node.price)
        if node_price <= price:
            results.extend(node.accommodation_ids)
            self._search_recursive(node.left, price, results)
            self._search_recursive(node.right, price, results)
        else:
            self._search_recursive(node.left, price, results)

    def print_tree(self):
        self._print_in_order(self.root)

    def _print_in_order(self, node):
        if node:
            self._print_in_order(node.left)
            print(f"Price: {node.price}, Accommodation IDs: {node.accommodation_ids}")
            self._print_in_order(node.right)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.accommodation_ids = []

class AmenityTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, amenity, accommodation_id):
        node = self.root
        for char in amenity.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.accommodation_ids.append(accommodation_id)

    def search(self, amenity):
        node = self.root
        for char in amenity.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return node.accommodation_ids
    
    def print_trie(self):
        self._print_trie_recursive(self.root, "")

    def _print_trie_recursive(self, node, prefix):
        if node.accommodation_ids:
            print(f"Amenity: {prefix}, Accommodation IDs: {node.accommodation_ids}")
        for char, child_node in node.children.items():
            self._print_trie_recursive(child_node, prefix + char)

# Hash table for accommodations and trie for amenities
accommodations_hash_table = {}
amenities_trie = AmenityTrie()
price_bst = PriceBST()

# Process each accommodation
for document in collection.find():
    accommodation_id = document['_id']
    accommodation_aw = document['aw']
    accommodations_hash_table[accommodation_id] = document

    amenities = document.get('Amenities', '')
    if amenities:
        amenities_list = [amenity.strip() for amenity in amenities.split(',')]
        for amenity in amenities_list:
            amenities_trie.insert(amenity, accommodation_aw)

    price = document.get('Price')
    if price is not None:
        price_bst.insert(price, accommodation_aw)


def homepage(request):
    if request.user.is_authenticated:
        return render(request, 'myApp/index.html')
    return render(request, 'myApp/index.html')

def register(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1 != pass2:
            return render(request, 'myApp/register.html', {'error_message': 'Your password and confirm password are not the same!!'})
        else:
            try:
                my_user = User.objects.create_user(uname, email, pass1)
                my_user.save()
                return redirect('my-login')
            except IntegrityError:
                return render(request, 'myApp/register.html', {'error_message': 'Username already exists. Please choose a different username.'})
    
    return render(request, 'myApp/register.html')

def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', 'homepage')
            return redirect(next_url)
        else:
            return render(request, 'myApp/my_login.html', {'error_message': 'Username or Password is incorrect!!!'})

    return render(request, 'myApp/my_login.html')

def user_logout(request):
    logout(request)
    return redirect('homepage')

def accommodation_details(request, aw):
    accommodation = next((acc for acc in accommodations_hash_table.values() if acc['aw'] == aw), None)
    if accommodation:
        return render(request, 'myApp/accommodation_details.html', {'accommodation': accommodation})
    else:
        return HttpResponse("Accommodation not found", status=404)
    
@login_required(login_url='my-login')
def book_accommodation(request, aw):
    accommodation = collection.find_one({'aw': aw})

    if accommodation:
        Booking.objects.create(
            user=request.user,
            accommodation_id=str(accommodation['aw']),
            property_name=accommodation.get('Property_Name', ''),
            property_title=accommodation.get('Property Title', ''),
            price=accommodation.get('Price', 0.0),
            location=accommodation.get('Location', ''),
            total_area=accommodation.get('Total_Area(SQFT)', 0),
            description=accommodation.get('Description', ''),
            total_rooms=accommodation.get('Total_Rooms', 0),
            balcony=accommodation.get('Balcony', ''),
            city=accommodation.get('city', ''),
            property_type=accommodation.get('property_type', ''),
            bhk=accommodation.get('BHK', 0),
            room_type=accommodation.get('Room Type', ''),
            amenities=accommodation.get('Amenities', '')
        )
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'fail'}, status=400)

@login_required(login_url="my-login")
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'myApp/my_bookings.html', {'bookings': bookings})

def filter_accommodations(request):
    if request.method == 'GET':
        amenities = request.GET.get('amenities', '')
        price_option = request.GET.get('custom_price', None)
        nearby_accommodations = request.session.get('nearby_accommodations')

        if nearby_accommodations is None:
            return HttpResponse("No nearby accommodations found", status=400)

        # Handle amenities filter
        if amenities:
            amenities_list = [amenity.strip() for amenity in amenities.split(',')]
            accommodations_with_amenities = [set(amenities_trie.search(amenity)) for amenity in amenities_list]

            if accommodations_with_amenities:
                common_accommodations = set.intersection(*accommodations_with_amenities)
            else:
                common_accommodations = set()
        else:
            common_accommodations = set(acc['aw'] for acc in nearby_accommodations)

        # Handle price filter
        if price_option:
            try:
                price_option = int(price_option)
                accommodations_with_price_below_price = set(price_bst.search(price_option))
            except ValueError:
                return HttpResponse("Invalid price option", status=400)
        else:
            accommodations_with_price_below_price = set(acc['aw'] for acc in nearby_accommodations)

        # Combine filters
        filtered_accommodations_ids = common_accommodations & accommodations_with_price_below_price

        # Prepare filtered accommodations for display
        filtered_accommodations = [
            acc for acc in nearby_accommodations if acc['aw'] in filtered_accommodations_ids
        ]

        # Sort accommodations by distance
        filtered_accommodations = sorted(filtered_accommodations, key=lambda x: x['distance'])
        accommodations_count = len(filtered_accommodations)

        context = {
            'accommodations': filtered_accommodations,
            'city': request.session.get('location', ''),
            'accommodations_count': accommodations_count
        }

        return render(request, 'myApp/accommodations.html', context)
    else:
        return HttpResponse("Method not allowed", status=405)


def amenities_suggestions(request):
    term = request.GET.get('term')
    amenities = collection.distinct('Amenities', {'Amenities': {'$regex': term, '$options': 'i'}})
    return JsonResponse(amenities, safe=False)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in km
    return distance

def get_coordinates_from_location(location):
    response = requests.get('https://nominatim.openstreetmap.org/search', params={'q': location, 'format': 'json'})
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon']) 
    return 0.0, 0.0

def get_coordinates_from_location2(location):
    x = geocode(location, provider='nominatim', user_agent='xyz', timeout=10)
    if not x.empty:
        return x.geometry.loc[0].y, x.geometry.loc[0].x 
    
    return 0.0, 0.0
    

nearby_accommodations = None
def search_accommodations(request):
        global nearby_accommodations
        if request.method == 'POST':
            form = SearchForm(request.POST)
            if form.is_valid():
                location = form.cleaned_data['location']
                if not location:
                    return HttpResponse("Please provide a location", status=400)
                
                latitude, longitude = get_coordinates_from_location(location)
                if latitude == 0.0 and longitude == 0.0:
                    latitude, longitude = get_coordinates_from_location2(location)
                    if latitude == 0.0 and longitude == 0.0:
                        return HttpResponse("Invalid Location")

                accommodations = collection.find({})
                for acc in accommodations:
                    acc_id = acc['_id']
                    acc_lat = float(acc['latitude'])
                    acc_lon = float(acc['longitude'])
                    distance = haversine(latitude, longitude, acc_lat, acc_lon)

                    accommodations_hash_table[acc_id] = {
                        '_id': str(acc_id),
                        'aw': acc.get('aw', ''),
                        'Property_Name': acc.get('Property_Name', ''),
                        'Property_Title': acc.get('Property Title', ''),
                        'Price': acc.get('Price', ''),
                        'Location': acc.get('Location', ''),
                        'Total_Area(SQFT)': acc.get('Total_Area(SQFT)', ''),
                        'Description': acc.get('Description', ''),
                        'Total_Rooms': acc.get('Total_Rooms', ''),
                        'Balcony': acc.get('Balcony', ''),
                        'city': acc.get('city', ''),
                        'property_type': acc.get('property_type', ''),
                        'BHK': acc.get('BHK', ''),
                        'Amenities': acc.get('Amenities', ''),
                        'Room_Type': acc.get('Room_Type', ''),
                        'location': acc.get('location', ''),
                        'latitude': acc_lat,
                        'longitude': acc_lon,
                        'distance': distance
                    }

                nearby_accommodations = [acc for acc in accommodations_hash_table.values() if acc['distance'] < 15]
                nearby_accommodations = sorted(nearby_accommodations, key=lambda x: x['distance'])
                request.session['nearby_accommodations'] = nearby_accommodations
                request.session['location'] = location

                accommodations_count = len(nearby_accommodations)
                context = {'accommodations': nearby_accommodations, 'city':location, 'accommodations_count': accommodations_count}
                # price_bst.print_tree()
                # amenities_trie.print_trie()
                return render(request, 'myApp/accommodations.html', context)
        else:
            form = SearchForm()
    
        return render(request, 'myApp/index.html', {'form': form})
