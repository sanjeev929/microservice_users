from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
import pymongo,json
from django.conf import settings
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_NAME]
usercollection = db['users']
managementcollection = db['management']
doctorscollection = db['doctors']

@csrf_exempt
def userindex(request):
    print("inside")
    if request.method == 'POST':
        email = request.POST.get('email')
        print("process b")
        data = {'processed_email': email, 'additional_data': 'from_2nd_project'}
        print("process a")
        return JsonResponse(data, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)