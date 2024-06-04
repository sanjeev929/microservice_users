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
    if request.method == "GET":
        doctor_details = doctorscollection.find({})
        doctor_details_list = list(doctor_details)
        response_data = {'doctor_details': doctor_details_list}
        return JsonResponse(response_data, encoder=JSONEncoder, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def book_appointment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            doctor_email = data.get('doctor_email')
            doctor_name = data.get('doctor_name')
            problem = data.get('problem')
            date = data.get('date')
            time = data.get('time')
            if 'booking' not in db.list_collection_names():
                db.create_collection('booking')
            userdata = usercollection.find({"mail":email})
            userdata = list(userdata)
            print(userdata)
            patient_name = ''.join([item['name'] for item in userdata])
            patient_age = ''.join([item['age'] for item in userdata])
            bookingcollection = db['booking']
            book_data = {
                "doctor_name":doctor_name,
                "doctor_email": doctor_email,
                "patient_email": email,
                "patient_name":patient_name,
                "patient_age":patient_age,
                "problem":problem,
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
            schedule_values = [item['schedule'] for item in bookingcollection]
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
    
@csrf_exempt
def get_schedule_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            bookingcollection = db['booking']
            data = bookingcollection.find({"patient_email":email})
            bookingcollection = list(data)
            response_data = {
                "message": "Booked successfully",
                "bookingcollection":bookingcollection
            }
            return JsonResponse(response_data,encoder=JSONEncoder, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)    
    
@csrf_exempt
def doctor_index(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('doctor_email')
            bookingcollection = db['booking']
            data = bookingcollection.find({"doctor_email":email})
            bookingcollection = list(data)
            Pendingcollection = [item for item in bookingcollection if item.get('status') == 'Pending']
            response_data = {
                "message": "Booked successfully",
                "Pendingcollection":Pendingcollection
            }
            return JsonResponse(response_data,encoder=JSONEncoder, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)   

@csrf_exempt
def status_change(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            patient_email = data.get('patient_email')
            doctor_email  = data.get('doctor_email')
            action  = data.get('action')
            bookingcollection = db['booking']
            if action == "Approved":
                data = bookingcollection.update_many({"patient_email":patient_email,"doctor_email":doctor_email},{"$set":{"status":action}})
            if action == "Rejected":
                data =  bookingcollection.delete_many({"patient_email":patient_email,"doctor_email":doctor_email}) 
            response_data = {
                "message": "update successfully",
            }
            return JsonResponse(response_data,encoder=JSONEncoder, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)     
@csrf_exempt
def doctor_approved(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('doctor_email')
            bookingcollection = db['booking']
            data = bookingcollection.find({"doctor_email":email})
            bookingcollection = list(data)
            approvedcollection = [item for item in bookingcollection if item.get('status') == 'Approved']
            response_data = {
                "message": "Booked successfully",
                "approvedcollection":approvedcollection
            }
            return JsonResponse(response_data,encoder=JSONEncoder, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)  
    
@csrf_exempt
def create_meeting(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            patient_email = data.get('patient_email')
            doctor_email  = data.get('doctor_email')
            meeting_link  = data.get('meeting_link')
            bookingcollection = db['booking']
            data = bookingcollection.update_many({"patient_email":patient_email,"doctor_email":doctor_email},{"$set":{"meeting_link":meeting_link}})
            response_data = {
                "message": "update successfully",
            }
            return JsonResponse(response_data,encoder=JSONEncoder, status=200)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)         