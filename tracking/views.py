# Import dependencies
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Lab, Food, DailyEntry, Profile, FoodHistory
from .forms import LabForm, ExtendedUserCreationForm, ProfileForm
import requests
import environ
from datetime import date
from json import dumps
# import os

# Set env
env = environ.Env()

# ------------ VIEWS ------------#


def indexPageView(request):
    """
    The landing page view before the user logs in.
    """
    return render(request, 'tracking/index.html')


def dailyPageView(request):
    """
    Once logged in, this is the landing page view, displaying today's data for the user.
    """
    try:

        # Intialize foods array
        foods = []

        # Grab today's entry for the user
        today = (DailyEntry.objects.filter(entry_date=date.today(), user__id=request.user.id)).values()

        # If entry doesn't exist, create one
        if (len(today) < 1):

            # Grab current user
            currentUser = User.objects.get(id=request.user.id)

            # Add new entry
            newEntry = DailyEntry(user=currentUser, entry_date=date.today(), water_intake_liters=0)
            newEntry.save()

            # Grab today's entry for the user
            today = (DailyEntry.objects.filter(entry_date=date.today(), user__id=request.user.id)).values()[0]

        # Entry already exists, grab it
        else:
            today = today[0]

        # Grab food histories for today
        foodHistory = FoodHistory.objects.filter(entry__id=today['id']).values()

        # Initialize total variables for the entire day
        ProteinTotal = 0
        SodiumTotal = 0
        PhosphorusTotal = 0
        PotassiumTotal = 0

        # Calculate weight
        weight = float(request.user.profile.weight) * 0.453592

        # Set recommended daily values for each nutrient
        RecommendedProtein = round(.6 * weight, 2)
        RecommendedSodium = 2300
        RecommendedPhosphorus = 1000
        RecommendedPotassium = 3000
        RecommendedWater = 2.70

        # Change recommended water based on the user's gender
        if request.user.profile.gender.gender_description == "f":
            RecommendedWater = 2.7
        else :
            RecommendedWater = 3.7

        # Loop through food history items for today
        for item in foodHistory:

            # Grab the food
            food = Food.objects.get(id=item['food_id'])

            # Update totals with calculations
            ProteinTotal += float(food.protein_g * item['quantity'])
            SodiumTotal += float(food.sodium_mg * item['quantity'])
            PhosphorusTotal += float(food.phosphorus_mg * item['quantity'])
            PotassiumTotal += float(food.potassium_mg * item['quantity'])

            # Initialize food dict
            foodDict = {}

            # Update attributes
            foodDict['id'] = item['id']
            foodDict['food_description'] = food.food_description
            foodDict['brand_name'] = food.brand_name
            foodDict['quantity'] = float(item['quantity'])
            foodDict['protein'] = round(float(food.protein_g * item['quantity']), 2)
            foodDict['sodium'] = float(food.sodium_mg * item['quantity'])
            foodDict['phosphorus'] = float(food.phosphorus_mg * item['quantity'])
            foodDict['potassium'] = float(food.potassium_mg * item['quantity'])

            # Push to array
            foods.append(foodDict)

        # Calculate percentages
        WaterPercentage = (float(float(today['water_intake_liters'])/RecommendedWater)) * 100
        SodiumPercentage = (float(SodiumTotal/RecommendedSodium)) * 100
        ProteinPercentage = (float(ProteinTotal/RecommendedProtein)) * 100
        PotassiumPercentage = (float(PotassiumTotal/RecommendedPotassium)) * 100
        PhosphorusPercentage = (float(PhosphorusTotal/RecommendedPhosphorus)) * 100

        # Round protein total
        ProteinTotal = round(ProteinTotal, 2)

        # Set context variable
        context = {
            "currentWaterLevel": float(today['water_intake_liters']),
            "currentWaterPercentage": WaterPercentage,
            "currentProteinLevel": ProteinTotal,
            "currentProteinPercentage": ProteinPercentage,
            "currentSodiumLevel": SodiumTotal,
            "currentSodiumPercentage": SodiumPercentage,
            "currentPotassiumLevel": PotassiumTotal,
            "currentPotassiumPercentage": PotassiumPercentage,
            "currentPhosphorusLevel": PhosphorusTotal,
            "currentPhosphorusPercentage": PhosphorusPercentage,
            "recommendedProtein": RecommendedProtein,
            "recommendedSodium": RecommendedSodium,
            "recommendedWater": RecommendedWater,
            "recommendedPhosphorus": RecommendedPhosphorus,
            "recommendedPotassium": RecommendedPotassium,
            "foods": foods
        }

        return render(request, 'tracking/daily.html', context)
    
    except Exception as e:

        # log error
        print(e)

        # If error was caused because user does not have profile, notify and logout
        if (type(e) == User.profile.RelatedObjectDoesNotExist):
            return HttpResponse("<script>alert('User does not have a profile, please create one and try again.'); window.location.href='/logout'</script>")

        # Notify and logout
        else:
            return HttpResponse("<script>alert('An error occured, please login again'); window.location.href='/logout'</script>")


def updateWaterLevel(request):
    """
    Updates water level for today's entry.
    \n
    Request Method:
    - POST
    \n
    Request Body:
    - water | the updated water intake | FLOAT
    """
    try:

        # Grab body from request
        body = dict(request.POST.items())

        # Grab today's entry for the user
        today = DailyEntry.objects.filter(entry_date=date.today(), user__id=request.user.id)[0]

        # If entry exists, update it
        if (today):

            # Update water level
            today.water_intake_liters = float(body['water'])
            today.save()

        # No entry exists, create one
        else:
            # Grab current user
            currentUser = User.objects.get(id=request.user.id)

            # Add new entry
            newEntry = DailyEntry(user=currentUser, entry_date=date.today(), water_intake_liters=float(body['water']))
            newEntry.save()

        # Notify user of success and redirect
        return HttpResponse("<script>alert('Water level updated successfully!'); window.location.href='/daily'</script>")


    except Exception as e:

        # Log error
        print(e)

        # Notify of error and redirect
        return HttpResponse("<script>alert('Failed to update water intake'); window.location.href='/daily'</script>")


def searchAPIResultsPageView(request):
    """
    The page view with results from searching the food API.
    \n
    Request Method:
    - GET
    \n
    Query params:
    - query | the query string | STRING
    """
    try:

        # Grab query param from request
        query = request.GET.__getitem__("query")

        # Set body for request
        # payload = { 
        #     "query": query,
        #     "api_key": os.getenv('FOOD_API_KEY')
        # }

        # Set body for request
        payload = { 
            "query": query,
            "api_key": env('FOOD_API_KEY')
        }

        # Send request
        # data = (requests.get(f"{os.getenv('FOOD_API_URL')}/foods/search", params=payload)).json()

        # Send request
        data = (requests.get(f"{env('FOOD_API_URL')}/foods/search", params=payload)).json()

        # Set context
        context = {
            "foods": data['foods']
        }

        return render(request, 'tracking/foodApiSearchResults.html', context)

    except Exception as e:

        # Log error
        print(e)

        # Notify user and redirect
        return HttpResponse("<script>alert('Failed to load results, try again'); window.location.href='/api/search'</script>")



def searchFoodResultsPageView(request):
    """
    The page view with results from searching food in database
    \n
    Request Method:
    - GET
    \n
    Query params:
    - query | the query string | STRING
    """
    try:

        # Grab query param from request
        query = request.GET.__getitem__("query")

        # Grab foods
        foods = Food.objects.filter(food_description__contains=query).distinct('food_description', 'brand_name').values()

        # Set context
        context = {
            "foods": foods
        }

        return render(request, 'tracking/myPantry.html', context)

    except Exception as e:

        # Log error
        print(e)

        # Notify user and redirect
        return HttpResponse("<script>alert('Failed to load results, try again'); window.location.href='/daily'</script>")


def saveAPIFood(request):
    """
    Saves a food found in the food API to the food database.
    \n
    Request Method:
    - GET
    \n
    Query params:
    - food | the food id | INTEGER
    """
    try:

        # Grab query param from request
        food = request.GET.__getitem__("food")

        # Set body for request
        # payload = {
        #     "api_key": os.getenv('FOOD_API_KEY'),
        #     "nutrients": "203,305,306,307"
        # }

        # Set body for request
        payload = {
            "api_key": env('FOOD_API_KEY'),
            "nutrients": "203,305,306,307"
        }

        # Send request, parsing json response to dict
        # outcome = (requests.get(f"{os.getenv('FOOD_API_URL')}/food/{food}", params=payload)).json()

        # Send request, parsing json response to dict
        outcome = (requests.get(f"{env('FOOD_API_URL')}/food/{food}", params=payload)).json()

        # Initialize new food var
        newFood = {}

        # If food is branded
        if (outcome['dataType'] == 'Branded'):

            # Initialize nutrient levels
            protein = 0.00
            phosphorus = 0.00
            potassium = 0.00
            sodium = 0.00

            # Loop through nutrients, updating nutrient levels
            for nutrient in outcome['foodNutrients']:
                if (nutrient['nutrient']['name'] == 'Protein'):
                    protein = float(nutrient['amount'])
                elif (nutrient['nutrient']['name'] == 'Phosphorus, P'):
                    phosphorus = float(nutrient['amount'])
                elif (nutrient['nutrient']['name'] == 'Potassium, K'):
                    potassium = float(nutrient['amount'])
                elif (nutrient['nutrient']['name'] == 'Sodium, Na'):
                    sodium = float(nutrient['amount'])

            # Add new food        
            newFood = Food(
                food_description=outcome['description'].lower(), 
                brand_name=outcome['brandName'].lower(), 
                serving_size=float(outcome['servingSize']), 
                serving_size_unit=outcome['servingSizeUnit'],
                protein_g=protein,
                phosphorus_mg=phosphorus,
                potassium_mg=potassium,
                sodium_mg=sodium
            )

        # Food is not branded
        else:

            # Intialize nutrient levels
            protein = 0.00
            phosphorus = 0.00
            potassium = 0.00
            sodium = 0.00

            # Loop through nutrients, updating levels
            for nutrient in outcome['foodNutrients']:
                if (nutrient['nutrient']['name'] == 'Protein'):
                    protein = float(nutrient['amount'])
                elif (nutrient['nutrient']['name'] == 'Phosphorus, P'):
                    phosphorus = float(nutrient['amount'])
                elif (nutrient['nutrient']['name'] == 'Potassium, K'):
                    potassium = float(nutrient['amount'])
                elif (nutrient['nutrient']['name'] == 'Sodium, Na'):
                    sodium = float(nutrient['amount'])

            # Add new food        
            newFood = Food(
                food_description=outcome['description'].lower(), 
                brand_name='', 
                serving_size=0, 
                serving_size_unit='',
                protein_g=protein,
                phosphorus_mg=phosphorus,
                potassium_mg=potassium,
                sodium_mg=sodium
            )
        
        # Save new food
        newFood.save()

        # Notify user of success and redirect
        return HttpResponse("<script>alert('Food saved successfully!'); window.location.href='/api/search'</script>")
            
    except Exception as e:

        # Log error
        print(e)

        # Notify user and redirect
        return HttpResponse("<script>alert('Failed to save food, try again'); window.location.href='/api/search'</script>")


def saveCustomFood(request):
    """
    Saves a user custom food to the food database.
    \n
    Request Method:
    - POST
    \n
    Request body:
    - food_description | STRING
    - brand_name | STRING | optional
    - serving_size | FLOAT | optional
    - serving_size_unit | STRING | optional
    - protein_g | FLOAT
    - phosphorus_mg | FLOAT
    - potassium_mg | FLOAT
    - sodium_mg | FLOAT
    """
    try:

        # Grab body from request
        body = dict(request.POST.items())

        # Add new food        
        newFood = Food(
            food_description=body['food_description'].lower(), 
            brand_name=body['brand_name'].lower() if body['brand_name'] != '' else '', 
            serving_size=float(body['serving_size']) if body['serving_size'] != '' else 0, 
            serving_size_unit=body['serving_size_unit'] if body['serving_size_unit'] != '' else '',
            protein_g=body['protein_g'],
            phosphorus_mg=body['phosphorus_mg'],
            potassium_mg=body['potassium_mg'],
            sodium_mg=body['sodium_mg']
        )
        
        # Save new food
        newFood.save()

        # Notify user of success and redirect
        return HttpResponse("<script>alert('Food saved successfully!'); window.location.href='/customFood'</script>")
            
    except Exception as e:

        # Log error
        print(e)

        # Notify user and redirect
        return HttpResponse("<script>alert('Failed to save food, try again'); window.location.href='/customFood'</script>")



def addFoodToEntry(request):
    """
    Adds a food to the users daily entry for the day.
    \n
    Request Method:
    - POST
    \n
    Request body:
    - food | the food id | INTEGER
    - quantity | the quantity eaten | FLOAT
    """
    try:

        # Grab body from request
        body = dict(request.POST.items())

        # Grab today's entry for the user
        today = DailyEntry.objects.filter(entry_date=date.today(), user__id=request.user.id)[0]

        # If entry exists, update it
        if (today):

            # Grab food
            food = Food.objects.get(id=body['food'])

            # Create new food history
            newFoodHistory = FoodHistory(entry=today, food=food, quantity=float(body['quantity']))
            newFoodHistory.save()

        # Entry doesn't exist, create one
        else:

            # Grab current user
            currentUser = User.objects.get(id=request.user.id)

            # Add new entry
            newEntry = DailyEntry(user=currentUser, entry_date=date.today(), water_intake_liters=0)
            newEntry.save()

            # Grab food
            food = Food.objects.get(id=body['food'])

            # Create new food history
            newFoodHistory = FoodHistory(entry=newEntry, food=food, quantity=float(body['quantity']))
            newFoodHistory.save()

        # Notify user of success and redirect
        return HttpResponse("<script>alert('Food added successfully!'); window.location.href='/daily'</script>")

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('Failed to add food, try again'); window.location.href='/daily'</script>")



def monthlyPageView(request):
    """
    This grabs the data for all history of the user and displays the calendar visualization.
    """
    try:

        # Intialize return array
        returnData = []

        # Calculate weight
        weight = float(request.user.profile.weight) * 0.453592

        # Set recommended nutrient values
        RecommendedProtein = weight * .6
        RecommendedSodium = 2300
        RecommendedPhosphorus = 1000
        RecommendedPotassium = 3000
        RecommendedWater = 0.00

        # Change recommended water based on user gender
        if request.user.profile.gender.gender_description == "f":
            RecommendedWater = 2.7
        else :
            RecommendedWater = 3.7

        # Grab current user
        currentUser = User.objects.get(id=request.user.id)

        # Grab all daily entries
        allEntries = DailyEntry.objects.filter(user=currentUser).values()

        # Loop through each daily entry
        for entry in allEntries:

            # Grab all food histories
            foodHistories = FoodHistory.objects.filter(entry__id=entry['id']).values()

            # Initialize totals
            ProteinTotal = 0
            SodiumTotal = 0
            PhosphorusTotal = 0
            PotassiumTotal = 0

            # Loop through food histories for the current day in loop
            for item in foodHistories:

                # Grab the food
                food = Food.objects.get(id=item['food_id'])

                # Grab nutrient totals for the food
                ProteinTotal += float(food.protein_g * item['quantity'])
                SodiumTotal += float(food.sodium_mg * item['quantity'])
                PhosphorusTotal += float(food.phosphorus_mg * item['quantity'])
                PotassiumTotal += float(food.potassium_mg * item['quantity'])

            # Intialize counter
            counter = 0

            # Update counter with healthy levels for the day
            if (ProteinTotal <= RecommendedProtein):
                counter = counter + 1
            if (SodiumTotal <= RecommendedSodium):
                counter = counter + 1
            if (PhosphorusTotal <= RecommendedPhosphorus):
                counter = counter + 1
            if (PotassiumTotal <= RecommendedPotassium):
                counter = counter + 1
            if (float(entry['water_intake_liters']) <= RecommendedWater):
                counter = counter + 1

            # Push current entry to return data array
            returnData.append({
                "date": entry['entry_date'],
                "healthyCount": counter
            })

        # Set context
        context = {
            "array": returnData
        }

        # Convert to json
        json = dumps(context, default=str)

        return render(request, 'tracking/monthly.html', { "data": json })

    except Exception as e:

        # Log error
        print(e)

        # Notify user and redirect
        return HttpResponse("<script>alert('Failed to load monthly view'); window.location.href='/daily'</script>")



def register(request):
    """
    This renders the registration (user account creation) form and handles submission of the form.
    """
    try:

        # If the request is post (form is being submitted)
        if request.method == 'POST':

            # Create forms
            form = ExtendedUserCreationForm(request.POST)
            profile_form = ProfileForm(request.POST)

            # If forms are valid
            if form.is_valid() and profile_form.is_valid():

                # Save user form
                user = form.save()

                # Configure profile form
                profile = profile_form.save(commit=False)
                profile.user = user

                # Save profile form
                profile.save()

                # Authenticate and login user
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)

                return redirect('/daily')

        # Need to render forms
        else: 

            # Create forms
            form = ExtendedUserCreationForm()
            profile_form = ProfileForm()

        # Set context with forms
        context = {'form' : form, 'profile_form' : profile_form}

        return render(request, 'tracking/register.html', context)

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('An error occured, please try again'); window.location.href='/login'</script>")


def viewUserInfoPageView(request):
    """
    Page view to see current user account info.
    """
    return render(request, 'tracking/userInfo.html')



def updateUserInfoPageView(request):
    """
    Renders form or handles form submission for updating user info.
    \n
    If request method was a post =>
    \n
    Request body:
    - email | STRING
    - first_name | STRING
    - last_name | STRING
    - phone | STRING
    - weight | FLOAT
    - height | FLOAT
    """
    try:

        # If request was a post (form was submitted)
        if request.method == 'POST':

            # Grab body from request
            body = dict(request.POST.items())

            # Grab the user and user profile
            user = User.objects.get(id=request.user.id)
            profile = Profile.objects.get(user__id=request.user.id)

            # Update the user and profile with new values
            user.email = body['email']
            user.first_name = body['first_name']
            user.last_name = body['last_name']
            profile.phone = body['phone']
            profile.weight = float(body['weight'])
            profile.height = float(body['height'])

            # Save user and profile
            user.save()
            profile.save()

            return redirect('/userInfo')

        # Render the updateUserInfo form
        else:
            return render(request, 'tracking/updateUserInfo.html')

    except Exception as e:

        # Log error
        print(e)

        # Notify user and redirect
        return HttpResponse("<script>alert('Failed to update user info, please try again'); window.location.href='/userInfo'</script>")



def deleteUserPageView(request):
    """
    The confirmation window for deleting a user.
    """
    return render(request, 'tracking/deleteUser.html')


def deleteUser(request):
    """
    Deletes the current logged in user.
    """
    try:

        # Grab current user
        user = User.objects.get(id=request.user.id)

        # Delete it
        user.delete()

        # Notify success and redirect
        return HttpResponse("<script>alert('Your account has been deleted successfully. Goodbye!'); window.location.href='/logout'</script>")

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('Failed to delete user, please try again'); window.location.href='/userInfo'</script>")


def deleteFoodHistory(request):
    """
    Deletes a food history object by id
    \n
    Request method:
    - POST
    \n
    Request body:
    - id | the food history id | INTEGER
    """
    try:

        # Grab body from request
        body = dict(request.POST.items())

        # Grab food history object by id
        food = FoodHistory.objects.get(id=body['id'])

        # Delete it
        food.delete()

        # Notify success and redirect
        return HttpResponse("<script>alert('Food removed successfully from your journal!'); window.location.href='/daily'</script>")

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('Failed to remove food, please try again'); window.location.href='/daily'</script>")


def searchPageView(request):
    """
    The form to search for a food in the API.
    """
    return render(request, 'tracking/foodApiSearch.html')


def viewLabsPageView(request):
    """
    The view labs page view.
    """
    try:

        # Grab current user
        currentUser = User.objects.get(id=request.user.id)

        # Grab lab data for user
        data = Lab.objects.filter(user=currentUser)

        # If request is a post (form submitted)
        if request.method == 'POST':

            # Create lab form
            form = LabForm(request.POST)

            # If form is valid, save it
            if form.is_valid():

                form.save()
           
                return redirect('/viewLabs')

        # Create form
        else:
            form = LabForm()

        # Set context with data and form
        context = {
            'data': data,
            'form': form,
        }

        return render(request, 'tracking/viewLabs.html', context)

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('An error occurred'); window.location.href='/daily'</script>")


def editFoodHistoryPageView(request, id, name, quantity):
    """
    The view to edit a specific food.
    \n
    URL params:
    - id | the food id | INTEGER
    - name | the food_description of the food | STRING
    - quantity | the quantity of the food | FLOAT
    """

    try:

        # Set context with passed variables and render the form view
        context = {
            "id": id,
            "name": name,
            "quantity": float(quantity)
        }

        return render(request, 'tracking/editDailyEntry.html', context)

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('An error occurred'); window.location.href='/daily'</script>")


def editFoodHistory(request):
    """
    Handles form submission to update food history object by id.
    \n
    Request method:
    - POST
    \n
    Request body:
    - id | the food history id | INTEGER
    """
    try:

        # Grab body from request
        body = dict(request.POST.items())

        # Grab food history object
        food = FoodHistory.objects.get(id=body['id'])

        # Update quantity
        food.quantity = body['quantity']

        # Save it
        food.save()

        # Notify success and redirect
        return HttpResponse("<script>alert('Food successfully updated in your journal!'); window.location.href='/daily'</script>")

    except Exception as e:

        # Log error
        print(e)

        # Notify and redirect
        return HttpResponse("<script>alert('Failed to update food, please try again'); window.location.href='/daily'</script>")



def tipsPageView(request):
    """
    Static info page with tips and information.
    """
    return render(request, 'tracking/tips.html')


def customFoodPageView(request):
    """
    Custom food submission form.
    """
    return render(request, 'tracking/customFood.html')

def myPantryPageView(request):
    """
    The user's pantry page view.
    """
    return render(request, 'tracking/myPantry.html')
