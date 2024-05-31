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


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

@csrf_exempt
def userindex(request):
    print("inside")
    if request.method == "GET":
        doctor_details = doctorscollection.find({})
        doctor_details_list = list(doctor_details)
        response_data = {'doctor_details': doctor_details_list}
        return JsonResponse(response_data, encoder=JSONEncoder, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def book_appointment(request):
    print("inside")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            doctor_email = data.get('doctor_email')
            print(f"Received email: {email}, doctor_email: {doctor_email}")
            response_data = {
                'email': email,
                'doctor_email': doctor_email
            }
            return JsonResponse(response_data, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
