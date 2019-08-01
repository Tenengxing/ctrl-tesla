import requests

from django.shortcuts import render, redirect
from django.conf import settings


def login(request):
	if request.method == 'POST':
		session = requests.session()
		resp = session.post(settings.TESLA_BASE_URL+"oauth/token?grant_type=password", data={
			"grant_type": "password",
			"client_id": settings.TESLA_CLIENT_ID,
			"client_secret": settings.TESLA_CLIENT_SECRET,
			"email": request.POST['email'],
			"password": request.POST['password'],
		})
		print("http code:", resp.status_code)
		print(resp.json())
		if resp.status_code == 200:
			request.session['token'] = resp.json()
		
		return redirect('/car/')
	return render(request, "car/login.html")


def index(request):
	# print(request.session['token'])
	session = requests.session()
	resp = session.get(settings.TESLA_BASE_URL+"/api/1/vehicles", headers={
		"Authorization": "Bearer " + request.session['token']['access_token']
		})
	# print(resp.json())
	cars = resp.json()['response']
	return render(request, "car/index.html", {'cars': cars})


def car(request, car_id):
	print(car_id)
	session = requests.session()
	resp = session.get(settings.TESLA_BASE_URL+f"/api/1/vehicles/{car_id}/vehicle_data", headers={
		"Authorization": "Bearer " + request.session['token']['access_token']
		})
	# print(resp.json())
	car = resp.json()['response']
	return render(request, "car/car.html", {'car': car})