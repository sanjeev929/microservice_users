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
    if email:
        if request.method == "GET":
            server_b_url = 'http://127.0.0.1:8001/userindex/'

            try:
                response = requests.get(server_b_url)
                response.raise_for_status()
                response_data = response.json()
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
            server_b_url = 'http://127.0.0.1:8001/get_doctor_schedule/'
            data = {
                "doctor_email": doctor_email,
            }
            try:
                response = requests.post(server_b_url, json=data)
                response.raise_for_status()
                response_data = response.json()
                booked_date=response_data["schedule_values"]
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
        age = request.POST['age']
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
            "age":age,
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
            
        elif role == 'doctor':
            user = doctorscollection.find_one({"mail": email, "password": password})
            if user:
                response = redirect("/doctorindex/")
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
        if request.method == "GET":
                server_b_url = 'http://127.0.0.1:8001/management/'
                data = {
                    "managementemail": email,
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                    approvedcollection=response_data["approvedcollection"]
                    pendingcollection=response_data["pendingcollection"]
                    print(pendingcollection,"=======")
                    context = {
                        "pendingcollection":pendingcollection,
                        "approvedcollection":approvedcollection
                    }
                    return render(request,"management.html",context)
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                    return redirect('/')
        return render(request, 'management.html')
    return redirect('/login/')

def doctorindex(request):
    try:
        doctor_email = request.COOKIES.get('email')
        print(doctor_email)
        user = doctorscollection.find_one({"mail": doctor_email})
        if doctor_email == user["mail"]:
            if request.method == "GET":
                server_b_url = 'http://127.0.0.1:8001/doctor_index/'
                data = {
                    "doctor_email": doctor_email,
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                    pendingcollection=response_data["Pendingcollection"]
                    print(pendingcollection,"=======")
                    context = {
                        "pendingcollection":pendingcollection
                    }
                    return render(request,"doctorindex.html",context)
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                    return redirect('/')
            else:
                patient_email = request.POST["patient_email"]
                doctor_email = request.POST["doctor_email"]
                action = request.POST["action"]
                print("==========",patient_email,action)
                server_b_url = 'http://127.0.0.1:8001/status_change/'
                data = {
                    "patient_email": patient_email,
                    "doctor_email":doctor_email,
                    "action":action
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                return redirect("/doctorindex/")
    except:
        print("error")          
        return redirect('/login/')
def approved(request):
    try:
        doctor_email = request.COOKIES.get('email')
        print(doctor_email)
        user = doctorscollection.find_one({"mail": doctor_email})
        if doctor_email == user["mail"]:
            if request.method == "GET":
                server_b_url = 'http://127.0.0.1:8001/doctor_approved/'
                data = {
                    "doctor_email": doctor_email,
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                    approvedcollection=response_data["approvedcollection"]
                    print(approvedcollection,"=======")
                    context = {
                        "approvedcollection":approvedcollection
                    }
                    return render(request,"approved.html",context)
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                    return redirect('/')
            else:
                patient_email = request.POST["patient_email"]
                doctor_email = request.POST["doctor_email"]
                meeting_link = request.POST["meeting_link"]
                print("==========",patient_email,meeting_link)
                server_b_url = 'http://127.0.0.1:8001/create_meeting/'
                data = {
                    "patient_email": patient_email,
                    "doctor_email":doctor_email,
                    "meeting_link":meeting_link
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                return redirect("/approved/")
    except:
        print("error===================")
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
    email = request.COOKIES.get('email')
    user = managementcollection.find_one({"mail": email})
    if email == user["mail"]:
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
    else:
        return redirect("/login/")

def deletedoctor(request):
    email = request.COOKIES.get('email')
    user = managementcollection.find_one({"mail": email})
    if email == user["mail"]:
        if request.method == "POST":
            email = request.POST["name"]
            doctorscollection.delete_one({'mail': email})
        alldoctor = doctorscollection.find()
        alldoctor = list(alldoctor)
        context={
            "alldoctors":alldoctor
        }
        return render(request,"deletedoctor.html",context)
    else:
        return redirect("/login/")

def book_appointment(request):
    email = request.COOKIES.get('email')
    if email:
        if request.method == "POST":

            doctor_email = request.POST.get("doctor_email")
            doctor_name = request.POST.get("nadoctor_nameme")
            problem = request.POST.get("problem")
            date = request.POST.get("date")
            time = request.POST.get("time")
            server_b_url = 'http://127.0.0.1:8001/book_appointment/'  # Ensure this URL is correct
            data = {
                "doctor_name":doctor_name,
                "email": email,
                "problem":problem,
                "doctor_email": doctor_email,
                "date":date,
                "time":time
            }
            try:
                response = requests.post(server_b_url, json=data)
                response.raise_for_status()
                response_data = response.json()
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
    
def appointment(request):
    email = request.COOKIES.get('email')
    if email:
        server_b_url = 'http://127.0.0.1:8001/get_schedule_status/'
        data = {
            "email": email,
        }
        try:
            response = requests.post(server_b_url, json=data)
            response.raise_for_status()
            response_data = response.json()
            booked_data=response_data["bookingcollection"]
            print(booked_data)
            context={
                "message":booked_data
            }
            return render(request,"appointment.html",context)
        except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")
    return redirect('/') 

def endmeet(request):
    try:
        doctor_email = request.COOKIES.get('email')
        print(doctor_email)
        user = doctorscollection.find_one({"mail": doctor_email})
        if doctor_email == user["mail"]:
            if request.method == "POST":
                patient_email = request.POST["patient_email"]
                doctor_email = request.POST["doctor_email"]
                server_b_url = 'http://127.0.0.1:8001/endmeeting/'
                data = {
                    "patient_email": patient_email,
                    "doctor_email":doctor_email,
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                return redirect("/approved/")
            else:
                return redirect('/approved/')
    except:
        print("error===================")
        return redirect('/approved/')
def dashboard(request):
    email = request.COOKIES.get('email')
    user = managementcollection.find_one({"mail": email})
    if email == user["mail"]:
        try:
            if request.method == "GET":
                server_b_url = 'http://127.0.0.1:8001/dashboard/'
                data = {
                    "email": email,
                }
                try:
                    response = requests.post(server_b_url, json=data)
                    response.raise_for_status()
                    response_data = response.json()
                    # booked_data=response_data["bookingcollection"]
                    # print(booked_data)
                    # context={
                    #     "message":booked_data
                    # }
                    return render(request,"dashboard.html")
                except requests.exceptions.RequestException as e:
                    print(f"Error sending data: {e}")
                return redirect("/login/")
            else:
                return redirect('/login/')
        except:
            print("error===================")
            return redirect('/login/')
    else:
        return redirect("/login/")    
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