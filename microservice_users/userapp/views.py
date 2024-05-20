from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def registration(request):
    if request.method == 'POST':
        name = request.POST['username']
        mail = request.POST['mail']
        password = request.POST['password1']
        print(name,mail,password)
    return render(request, 'registration.html')

def login(request):
    return render(request, 'login.html')
