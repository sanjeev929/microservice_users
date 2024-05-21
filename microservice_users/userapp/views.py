from django.shortcuts import render,redirect
import pymongo
from django.conf import settings
import requests

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_NAME]
usercollection = db['users']
managementcollection = db['management']

def index(request):
    email = request.COOKIES.get('user_email')
    # if email:
    #     server_b_url = 'http://127.0.0.1:8001/indexget/'
    #     data = {'email': email}
    #     response = requests.post(server_b_url, data=data)

    #     if response.status_code == 200:
    #         return render(request, 'index.html')
    #     else:
    #        return redirect('/login/')
    # else:
    #     return redirect('/login/')
    return render(request, 'index.html')

def registration(request):
    if request.method == 'POST':
        name = request.POST['username']
        mail = request.POST['mail']
        password = request.POST['password1']
        if 'users' not in db.list_collection_names():
            db.create_collection('users')

        usercollection = db['users']
        if usercollection.find_one({"mail": mail}):
            context={
                'message':'Email has already been taken'
            }
            return render(request, 'registration.html',context)

        doctor_data = {
            "name": name,
            "mail": mail,
            "password": password
        }
        usercollection.insert_one(doctor_data)
        return redirect("/login/")
    return render(request, 'registration.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        print(role)
        if role == 'patient':
            user = usercollection.find_one({"mail": email, "password": password})
            print(user)
            if user:
                response = redirect("/")
                response.set_cookie('email', email)
                return response
            else:
                context = {
                    'message': 'Invalid email or password.'
                }
                return render(request, 'login.html', context)
            
        elif role == 'management':
            user = managementcollection.find_one({"mail": email, "password": password})
            print(user)
            if user:
                response = redirect("/management/")
                response.set_cookie('email', email)
                return response
            else:
                context = {
                    'message': 'Invalid email or password or role.'
                }
                return render(request, 'login.html', context)    
            

    return render(request, 'login.html')

def management(request):
    email = request.COOKIES.get('email')
    user = managementcollection.find_one({"mail": email})
    if email == user["mail"]:
        return render(request, 'management.html')
    return redirect('/login/')

def logout(request):
    response = redirect('/login/')
    response.delete_cookie('email')
    return response