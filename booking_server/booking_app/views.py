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
bookingcollection =db['booking']


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
            date = data.get('date')
            time = data.get('time')
            if 'booking' not in db.list_collection_names():
                db.create_collection('booking')

            bookingcollection = db['booking']
            print(doctor_email,email,date,time)
            book_data = {
                "doctor_email": doctor_email,
                "patient_email": email,
                "schedule": str(date)+"/"+str(time),
                "status":"Pending"
            }
            bookingcollection.insert_one(book_data)
            response_data = {
                "message": "Booked successfully",
            }
            return JsonResponse(response_data, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_doctor_schedule(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            doctor_email = data.get('doctor_email')
            bookingcollection = db['booking']
            data = bookingcollection.find({"doctor_email":doctor_email})
            bookingcollection = list(data)
            print()
            schedule_values = [item['schedule'] for item in bookingcollection]
            print(schedule_values)
            response_data = {
                "message": "Booked successfully",
                "schedule_values":schedule_values
            }
            return JsonResponse(response_data, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)