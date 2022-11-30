from django.shortcuts import render, redirect
from .models import Lab, Food
from .forms import LabForm
import requests
import environ

# Set env
env = environ.Env()

# Import functions
from .functions.searchFood import searchFood

# Create your views here.

def indexPageView(request):
    return render(request, 'tracking/index.html')

def dailyPageView(request):
    return render(request, 'tracking/daily.html')

def searchResultsPageView(request):
    """
    The page view with results from food searching
    """
    try:
        # Grab query param from request
        query = request.GET.__getitem__("query")

        # Search food
        data = searchFood(query)

        # Check for error
        if (data['result'] == 1):
            raise Exception("Error occured searching food")

        # Set context
        context = {
            "foods": data['data']['foods']
        }

        return render(request, 'tracking/searchResults.html', context)

    except Exception as e:
        # Log error
        print(e)

        # Render error page
        return render(request, 'tracking/error.html')

def saveAPIFood(request):

    try:
        # Grab query param from request
        food = request.GET.__getitem__("food")

        # Set body for request
        payload = {
            "api_key": env('FOOD_API_KEY'),
            "nutrients": "203,305,306,307"
        }

        # Send request
        outcome = (requests.get(f"{env('FOOD_API_URL')}/food/{food}", params=payload)).json()

        newFood = {}

        # If food is branded
        if (outcome['dataType'] == 'Branded'):

            protien = 0.00
            phosphorus = 0.00
            potassium = 0.00
            sodium = 0.00

            # Loop through nutrients
            for food in outcome['footNutrients']:
                if (food['nutrient']['name'] == 'Protein'):
                    protien = float(food['amount'])
                elif (food['nutrient']['name'] == 'Phosphorus, P'):
                    phosphorus = float(food['amount'])
                elif (food['nutrient']['name'] == 'Potassium, K'):
                    potassium = float(food['amount'])
                elif (food['nutrient']['name'] == 'Sodium, NA'):
                    sodium = float(food['amount'])

            # Add new food        
            newFood = Food(
                food_description=outcome['description'], 
                brand_name=outcome['brandName'], 
                serving_size=float(outcome['servingSize']), 
                serving_size_unit=outcome['servingSizeUnit'],
                protien_g=protien,
                phosphorus_mg=phosphorus,
                potassium_mg=potassium,
                sodium_mg=sodium
            )

        else:
            protien = 0.00
            phosphorus = 0.00
            potassium = 0.00
            sodium = 0.00

            # Loop through nutrients
            for food in outcome['footNutrients']:
                if (food['nutrient']['name'] == 'Protein'):
                    protien = float(food['amount'])
                elif (food['nutrient']['name'] == 'Phosphorus, P'):
                    phosphorus = float(food['amount'])
                elif (food['nutrient']['name'] == 'Potassium, K'):
                    potassium = float(food['amount'])
                elif (food['nutrient']['name'] == 'Sodium, NA'):
                    sodium = float(food['amount'])

            # Add new food        
            newFood = Food(
                food_description=outcome['description'], 
                protien_g=protien,
                phosphorus_mg=phosphorus,
                potassium_mg=potassium,
                sodium_mg=sodium
            )
        
        # Save new food
        newFood.save()
            
    except Exception as e:
        # Log error
        print(e)

        # Render error page
        return render(request, 'tracking/error.html')


def weeklyPageView(request):
    return render(request, 'tracking/weekly.html')

def monthlyPageView(request):
    return render(request, 'tracking/monthly.html')

def accountCreationPageView(request):
    return render(request, 'tracking/createAccount.html')

def viewUserInfoPageView(request):
    return render(request, 'tracking/userInfo.html')

def updateUserInfoPageView(request):
    return render(request, 'tracking/updateUserInfo.html')

def deleteUserPageView(request):
    return render(request, 'tracking/deleteUser.html')

def searchPageView(request):
    return render(request, 'tracking/search.html')

def viewLabsPageView(request):
    data = Lab.objects.all()
    if request.method == 'POST':
        form = LabForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/viewLabs')
    else:
        form = LabForm()
    context = {
        'data': data,
        'form': form,
    }

    return render(request, 'tracking/viewLabs.html', context)

def addLabsPageView(request):
    return render(request, 'tracking/addLabs.html')

def errorPageView(request):
    return render(request, 'tracking/error.html')

def tipsPageView(request):
    return render(request, 'tracking/tips.html')

def customFoodPageView(request):
    return render(request, 'tracking/customFood.html')