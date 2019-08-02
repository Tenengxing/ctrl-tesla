import requests

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseBadRequest


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


def command(request, car_id, command):
	commands = ['door_unlock',
	            'door_lock',
	            'flash_lights',
	            'honk_horn',
	            'auto_conditioning_start',
	            'auto_conditioning_stop',
	            'set_temps',
	            'actuate_trunk',
	            'actuate_trunk_rear',
	            'actuate_trunk_front',
	            'media_next_track',]
	if command not in commands:
		return HttpResponseBadRequest
	data = {}
	if command == 'actuate_trunk_rear':
		command = 'actuate_trunk'
		data['which_trunk'] = 'rear'
	elif command == 'actuate_trunk_front':
		command = 'actuate_trunk'
		data['which_trunk'] = 'front'
	if command == 'set_temps':
		data['driver_temp'] = request.POST['driver_temp']
		data['passenger_temp'] = request.POST['passenger_temp']
	session = requests.session()
	resp = session.post(settings.TESLA_BASE_URL+f"/api/1/vehicles/{car_id}/command/{command}", headers={
		"Authorization": "Bearer " + request.session['token']['access_token']
		}, data=data)
	print(resp.json())
	return redirect(f"/car/{car_id}/")


