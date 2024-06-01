from django.shortcuts import render,redirect
import pymongo,json
from django.conf import settings
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson import ObjectId
from django.middleware.csrf import get_token

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_NAME]
usercollection = db['users']
managementcollection = db['management']
doctorscollection = db['doctors']
ipaddress = "http://192.168.249.87:8000"


def index(request):
    email = request.COOKIES.get('email')
    print(email)
    if email:
        if request.method == "GET":
            print("================================")
            server_b_url = 'http://127.0.0.1:8001/userindex/'

            try:
                response = requests.get(server_b_url)
                response.raise_for_status()
                response_data = response.json()
                print(response_data['doctor_details'])
                context = {
                    'message': response_data['doctor_details'],
                    "email":email
                    }
                return render(request, 'index.html', context)

            except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")
                context = {'message': 'Error sending data to another service'}
                return render(request, 'index.html', context)
        else:
            doctor_name = request.POST["doctor_name"]
            doctor_email = request.POST["doctor_email"]
            doctor_study = request.POST["doctor_study"]
            doctor_specialist = request.POST["doctor_specialist"]
            print("================================")
            server_b_url = 'http://127.0.0.1:8001/get_doctor_schedule/'  # Ensure this URL is correct
            data = {
                "doctor_email": doctor_email,
            }
            try:
                response = requests.post(server_b_url, json=data)
                response.raise_for_status()
                response_data = response.json()
                booked_date=response_data["schedule_values"]
                print(booked_date)
                booked_date_json = json.dumps(booked_date)
                context ={
                    "doctor_name":doctor_name,
                    "doctor_email":doctor_email,
                    "doctor_study":doctor_study,
                    "doctor_specialist":doctor_specialist,
                    "booked_date":booked_date_json
                }
                return render(request,"booking.html",context)
            except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")
                return redirect('/')
    else:
        return redirect('/login/')


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
        if role == 'patient':
            user = usercollection.find_one({"mail": email, "password": password})
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

def createdoctor(request):
    email = request.COOKIES.get('email')
    user = managementcollection.find_one({"mail": email})
    if email == user["mail"]:
        if request.method == "POST":
            name = request.POST.get('name')
            dob = request.POST.get('dob')
            email = request.POST.get('email')
            study = request.POST.get('study')
            specialist = request.POST.get('specialist')
            if 'doctors' not in db.list_collection_names():
                db.create_collection('doctors')
            doctorscollection = db['doctors']
            if doctorscollection.find_one({"mail": email}):
                context={
                    'message':'Email has already been taken'
                }
                return render(request, 'createdoctor.html',context)

            doctor_data = {
                "name": name,
                "dob":dob,
                "mail": email,
                "study":study,
                "specialist":specialist
                
            }
            doctorscollection.insert_one(doctor_data)
            user = doctorscollection.find_one({"mail": email})
            send_email_with_link(email,user["_id"])
            return render(request, 'createdoctor.html')
        if request.method == "GET":
            return render(request, 'createdoctor.html')
    return redirect('/login/')

def logout(request):
    response = redirect('/login/')
    response.delete_cookie('email')
    return response


def doctorsetpassword(request):
    doctor_id = request.GET.get('id')
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        new_password = request.POST.get('password')
        db['doctors'].update_one({'_id': ObjectId(doctor_id)}, {'$set': {'password': new_password}})
        return redirect('/login/') 
    context={
        "doctor_id":doctor_id
    }
    return render(request,"doctorsetpassword.html",context)

def editdoctor(request):
    if request.method == "POST":
        name = request.POST["name"]
        dob = request.POST["dob"]
        email = request.POST["email"]
        study = request.POST["study"]
        specialist = request.POST["specialist"]
        doctorscollection.update_one({'mail': email}, {'$set': {'name': name,"dob":dob,"study":study,"specialist":specialist}})
    alldoctor = doctorscollection.find()
    alldoctor = list(alldoctor)
    context={
        "alldoctors":alldoctor
    }
    return render(request,"editdoctor.html",context)

def deletedoctor(request):
    if request.method == "POST":
        email = request.POST["name"]
        doctorscollection.delete_one({'mail': email})
    alldoctor = doctorscollection.find()
    alldoctor = list(alldoctor)
    context={
        "alldoctors":alldoctor
    }
    return render(request,"deletedoctor.html",context)

def book_appointment(request):
    email = request.COOKIES.get('email')
    print(email)
    if email:
        if request.method == "POST":
            print("================================")
            doctor_email = request.POST.get("doctor_email")
            date = request.POST.get("date")
            time = request.POST.get("time")
            server_b_url = 'http://127.0.0.1:8001/book_appointment/'  # Ensure this URL is correct
            data = {
                "email": email,
                "doctor_email": doctor_email,
                "date":date,
                "time":time
            }
            try:
                response = requests.post(server_b_url, json=data)
                response.raise_for_status()
                response_data = response.json()
                print(response_data)
                context = {
                    'message': response_data,
                    "email": email
                }
                return redirect('/')
            except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")
                context = {'message': 'Error sending data to another service'}
                return redirect('/')
    else:
        return redirect('/')

def send_email_with_link(email, doctor_id):
    message = MIMEMultipart()
    message["From"] = "Midical Department" 
    message["To"] = email
    message["Subject"] = "Set Password"
    body = f'<p>Click the following link to set your password: <a href="{ipaddress}/doctorsetpassword/?id={doctor_id}">Set Password</a></p>'
    message.attach(MIMEText(body, "html"))

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("sanjeevsanju929@gmail.com", "fhge kait cnqe mjba")
    s.sendmail("sanjeevsanju929@gmail.com", email, message.as_string())
    s.quit()
    return {"success"}