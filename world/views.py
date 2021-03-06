from django.shortcuts import render, redirect
from django.views.generic import DetailView
from .forms import PropertySearchForm
from .models import TestProperty
import requests
from datetime import datetime
from django.utils import timezone
from bs4 import BeautifulSoup
import urllib.parse
import re
import overpy
import numpy as np

def home(request):
    return render(request, 'world/home.html')


def about(request):
    return render(request, 'world/about.html', {'title': 'About'})


class PropDetailView(DetailView):
    model = TestProperty
    context_object_name = 'prop'


# #property search form
# def search(request):
#     context = {}
#     prop_list = []
#
#     if request.method == 'POST':
#         form = PropertySearchForm(request.POST)
#
#         if form.is_valid():
#             city = form.cleaned_data['city']
#             #maxRent = form.cleaned_data['rent']
#             maxRent = request.POST['rent']
#             houseType = form.cleaned_data['house_type']
#             nlp = spacy.load("en_core_web_sm")
#
#             #get housing data from myHome
#             page = requests.get("https://www.myhome.ie/rentals/dublin/property-to-rent-in-{0}".format(city))
#             soup = BeautifulSoup(page.content, 'html.parser')
#             noProp = soup.find_all(class_="NoResultsCard py-5")
#             propertyCard = soup.find_all(class_="PropertyListingCard")
#
#             print(noProp)
#
#             if noProp:
#                 context['noProp'] = True
#                 return render(request, 'world/search.html', context)
#
#             else:
#                 #parsing content and assigning to variables
#                 for prop in propertyCard:
#                     propList = prop
#                     propAddress = propList.find(class_="PropertyListingCard__Address").get_text()
#                     rentPrice = propList.find(class_="PropertyListingCard__Price").get_text()
#
#                     #property info
#                     infoSpans = propList.find_all('span', {'class' : 'PropertyInfoStrip__Detail ng-star-inserted'})
#                     infoLines = [span.get_text() for span in infoSpans]
#
#                     print(infoLines)
#
#                     beds = baths = house = 'N/A'
#                     houseTypes = ['Apartment ', 'Terraced House ', 'Semi-Detached ',
#                                   'Detached ', 'Bungalow ', 'Country House ', 'Studio ']
#
#                     #assign values for prop info
#                     for line in infoLines:
#                         if ('bed' in line):
#                             beds = line
#                         if('bath' in line):
#                             baths = line
#                         if(line in houseTypes):
#                             house = line
#
#                     house_sim = 0
#                     # ideal vs actual house type
#                     if houseType:
#                         for ideal_house in houseType:
#                             if ideal_house in house:
#                                 house_sim = 1
#                         print(house_sim)
#
#                     print(beds, baths, house)
#
#                     #extract number from rent price p/m
#                     try:
#                         rentNumeric = re.search('€(.+?) ',rentPrice).group(1)
#                     except AttributeError:
#                         rentNumeric = ''
#
#                     #using Nominatim for lat/lon info of property
#                     url = 'https://nominatim.openstreetmap.org/search/'
#                     + urllib.parse.quote(propAddress) + '?format=json'
#                     response = requests.get(url).json()
#
#                     try:
#                         lat = response[0]["lat"]
#                         lon = response[0]["lon"]
#
#                     #find default coords of city if difficulties finding address
#                     except:
#                         url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(
#                             city) + '?format=json'
#                         response = requests.get(url).json()
#                         lat = response[0]["lat"]
#                         lon = response[0]["lon"]
#
#                     print(propAddress)
#                     print(lat + " " + lon)
#
#                     if maxRent != '' and rentNumeric != '':
#                         rentNumeric = rentNumeric.replace(',','')
#
#                         ideal_rent = int(maxRent)
#                         actual_rent = int(rentNumeric)
#
#                         diff = actual_rent - ideal_rent
#
#                         if(diff <= 0 or diff <= (ideal_rent * 0.33)):
#                             rent_sim = "High"
#                         elif(diff > (ideal_rent * 0.33) and diff <= (ideal_rent * 0.67)):
#                             rent_sim = "Medium"
#                         elif(diff > (ideal_rent * 0.67)):
#                             rent_sim = "Low"
#                         else:
#                             rent_sim = "Unknown"
#                     else:
#                         rent_sim = "Unknown"
#
#                     # making JSON object for property data
#                     property = {
#                         'address': propAddress,
#                         'city': city,
#                         'lat': lat,
#                         'lon': lon,
#                         'rent': rentPrice,
#                         'rent_sim' : rent_sim,
#                         'beds': beds,
#                         'baths': baths,
#                         'house': house,
#                         'house_sim': house_sim
#                     }
#
#                     prop_list.append(property)
#
#
#             #sort based on rent similarity
#             prop_list.sort(key = lambda k : k['rent_sim'], reverse=True)
#
#             #context
#             context['prop_list'] = prop_list
#             context['form'] = form
#
#             #search results if form is valid
#             return render(request, 'world/results.html', context)
#
#     else:
#         form = PropertySearchForm()
#     return render(request, 'world/search.html', {'form' : form})

def find_latest_info(city):
    search_props = []

    page = requests.get("https://www.daft.ie/property-for-rent/{0}-dublin".format(city.lower()))
    soup = BeautifulSoup(page.content, 'html.parser')

    noProp = soup.find_all(class_="ZeroResults__Container-sc-193ko9u-2 UZhCx")
    print("noProp = " + str(noProp))

    # if no properties match search
    if noProp:
        return []

    #if properties are found
    else:
        propertyCard = soup.find_all(class_="SearchPage__Result-gg133s-2 itNYNv")

        for prop in propertyCard:
            try:
                propList = prop
                propAddress = propList.find(class_="TitleBlock__Address-sc-1avkvav-7 knPImU").get_text()
                rentPrice = propList.find(class_="TitleBlock__Price-sc-1avkvav-3 pJtsY").p.text

                # property info
                beds = propList.find("p", {"data-testid": "beds"}).get_text()
                baths = propList.find("p", {"data-testid": "baths"}).get_text()
                daftHouse = propList.find("p", {"data-testid": "property-type"}).get_text()

                osm_address = propAddress + " Ireland"
                osm_city = city + " Dublin Ireland"

                #using Nominatim for lat/lon info of property
                url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(osm_address) + '?format=json'
                response = requests.get(url).json()

                try:
                    lat = response[0]["lat"]
                    lon = response[0]["lon"]

                #find default coords of city if difficulties finding address
                except:
                    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(
                        osm_city) + '?format=json'
                    response = requests.get(url).json()
                    lat = response[0]["lat"]
                    lon = response[0]["lon"]

                print(propAddress)
                print(lat + " " + lon)

                listing = TestProperty(address=propAddress, city = city, lat=lat,
                                       lon = lon, rent=rentPrice, beds = beds, baths = baths,
                                       propertyType = daftHouse)

                listing.save()
                search_props.append(listing)
            except:
                print("Incompatible property")

    return search_props


def search(request):
    context = {}
    prop_list = []
    houseTypes = ['Apartment', 'Terraced House', 'Semi-Detached',
                  'Detached', 'Bungalow', 'Country House', 'Studio']

    if request.method == 'POST':
        form = PropertySearchForm(request.POST)

        context['form'] = form

        if form.is_valid():
            city = form.cleaned_data['city']
            maxRent = request.POST['rent']
            rentPriority = request.POST['rent_priority']
            housePriority = request.POST['house_priority']
            houseType = form.cleaned_data['house_type']

            if not houseType or 'Any' in houseType:
                housePriority = 0

            print(city)
            print(rentPriority, housePriority, houseType)

            weights = np.array([rentPriority, housePriority]).astype(np.float)
            weight_sum = np.sum(weights)
            print(weights, weight_sum)

            balanced = weights/weight_sum
            print(balanced)

            #check if balanced to 1
            total_balanced = np.sum(balanced)
            print(total_balanced)

            rent_weight = balanced[0]
            house_weight = balanced[1]

            search_props = TestProperty.objects.filter(city=city)

            if not search_props:
                search_props = find_latest_info(city)
                print(search_props)

            # else:
            #     last_updated = datetime.strftime(search_props[0].date_posted, '%d-%m-%Y')
            #     time_now = datetime.strftime(timezone.now(), '%d-%m-%Y')
            #
            #     print(last_updated, time_now)
            #
            #     if last_updated != time_now:
            #         TestProperty.objects.filter(city=city).delete()
            #         search_props = find_latest_info(city)

            if not search_props:
                context['noProp'] = True
                return render(request, 'world/search.html', context)

            else:
                for prop in search_props:
                    #extract number from rent price p/m
                    try:
                        rentNumeric = re.search('€(.+?) ',prop.rent).group(1)
                        rentNumeric = rentNumeric.replace(',', '')
                    except AttributeError:
                        rentNumeric = 0

                    ideal_rent = int(maxRent)
                    actual_rent = int(rentNumeric)

                    print ("Ideal vs Actual " + str(ideal_rent) + " " + str(actual_rent))
                    rent_sim = 0
                    house_sim = 0

                    if actual_rent != 0:
                        diff = actual_rent - ideal_rent

                        if (diff <= 0):
                            rent_sim = 1
                        elif (diff > 0 and diff <= (ideal_rent * 0.33)):
                            rent_sim = 0.8
                        elif(diff > (ideal_rent * 0.33) and diff <= (ideal_rent * 0.67)):
                            rent_sim = 0.5
                        else:
                            rent_sim = 0

                    # ideal vs actual house type
                    for house in houseType:
                        if house in houseTypes or house == "Any":
                            house_sim = 1

                    rent_weighted = float(rent_sim * float(rent_weight))
                    house_weighted = float(house_sim * float(house_weight))

                    total_sim = rent_weighted + house_weighted

                    # making JSON object for property data
                    property = {
                        'id' : prop.id,
                        'address': prop.address,
                        'city': prop.city,
                        'date_posted':prop.date_posted,
                        'lat': prop.lat,
                        'lon': prop.lon,
                        'rent': prop.rent,
                        'rent_sim' : rent_sim,
                        'rent_eur' : actual_rent,
                        'beds': prop.beds,
                        'baths': prop.baths,
                        'house': prop.propertyType,
                        'house_sim': house_sim,
                        'total_sim' : total_sim
                    }

                    prop_list.append(property)

                if housePriority == 0:
                    prop_list.sort(key=lambda k: k['rent_eur'], reverse=False)
                else:
                    prop_list.sort(key=lambda k: k['total_sim'], reverse=True)

                #context
                context['prop_list'] = prop_list
                context['form'] = form

                #search results if form is valid
                return render(request, 'world/search.html', context)

    else:
        form = PropertySearchForm()
    return render(request, 'world/search.html', {'form' : form})


# def overpass_test(request):
#     context = {}
#
#     radius = float(request.POST['radius'])
#     radius *= 1000
#     lat = request.POST['lat']
#     lon = request.POST['lon']
#
#     print(radius,lat, lon)
#
#     amenity_list = get_amenities(radius, lat, lon)
#
#     source = {
#         'lat' : lat,
#         'lon' : lon,
#         'radius' : radius
#     }
#
#     context['amenity_list'] = amenity_list
#     context['source'] = source
#     return render(request, 'world/amenities.html', context)

def overpass_test(request):
    context = {}

    radius = float(request.POST['radius'])
    radius *= 1000
    lat = request.POST['lat']
    lon = request.POST['lon']

    print(radius,lat, lon)

    amenity_list = get_amenities(radius, lat, lon)

    source = {
        'lat' : lat,
        'lon' : lon,
        'radius' : radius
    }

    context['amenity_list'] = amenity_list
    context['source'] = source
    return render(request, 'world/amenities.html', context)

def get_amenities(radius, lat, lon):
    amenity_list = []
    api = overpy.Overpass()

    query = ("""
                (
                  node["amenity"](around:{0},{1}, {2});
                  way["amenity"](around:{0},{1}, {2});
                );
                out center;
                >;
            """).format(radius, lat, lon)
    result = api.query(query)

    for node in result.nodes:
        amenity = node.tags.get("amenity", "n/a")
        name = node.tags.get("name", "n/a")
        print(amenity, name, node.lat, node.lon)

        amenity_display_name = amenity.replace("_", " ")
        amenity_display_name = amenity_display_name.title()

        area_amenity = {
            'amenity' : amenity,
            'amenity_display_name' : amenity_display_name,
            'name' : name,
            'lat' : node.lat,
            'lon' : node.lon
        }

        amenity_list.append(area_amenity)

    for way in result.ways:
        amenity = way.tags.get("amenity", "n/a")
        name = way.tags.get("name", "n/a")
        print(amenity, name, way.center_lat, way.center_lon)

        amenity_display_name = amenity.replace("_", " ")
        amenity_display_name = amenity_display_name.title()


        area_amenity = {
            'amenity': amenity,
            'amenity_display_name': amenity_display_name,
            'name': name,
            'lat': node.lat,
            'lon': node.lon
        }

        amenity_list.append(area_amenity)

    return amenity_list