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
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        print("process b")
        data = {'processed_email': email, 'additional_data': 'from_2nd_project'}
        print("process a",data)
        return JsonResponse(data, status=200)
    else:
        doctor_details = doctorscollection.find({})
        doctor_details_list = list(doctor_details)
        response_data = {'doctor_details': doctor_details_list}
        return JsonResponse(response_data, encoder=JSONEncoder, status=200)
