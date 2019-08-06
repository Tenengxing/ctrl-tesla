import requests
import base64
import websocket

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
			request.session['token']['email'] = request.POST['email']
		
		return redirect('/car/')
	return render(request, "car/login.html")


def index(request):
	# print(request.session['token'])
	session = requests.session()
	resp = session.get(settings.TESLA_BASE_URL+"/api/1/vehicles", headers={
		"Authorization": "Bearer " + request.session['token']['access_token']
		})
	print(resp.json())
	cars = resp.json()['response']
	return render(request, "car/index.html", {'cars': cars})


def car(request, car_id):
	print(car_id)
	session = requests.session()
	resp = session.get(settings.TESLA_BASE_URL+f"/api/1/vehicles/{car_id}/vehicle_data", headers={
		"Authorization": "Bearer " + request.session['token']['access_token']
		})
	print(resp.status_code)
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


def summon(request, vehicle_id):
	if request.method == 'POST':
	    second = int(request.POST['second'])
	    enp = "%s:%s" % (request.session['token']['email'], request.GET['token'])
	    auth = base64.b64encode(bytes(enp, "utf-8")).decode("utf-8")
	    url = f"{settings.TESLA_BASE_WS}{vehicle_id}"
	    print("url: " + url)
	    ws = websocket.WebSocketApp(url,
	          header={"Authorization": f"Basic {auth}"},
	          on_message = on_message,
	          on_error = on_error,
	          on_close = on_close)
	    ws.on_open = on_open
	    ws.run_forever()

	return render(request, "car/summon.html")

def on_open(ws):
    def run(*args):
        time.sleep(1)
        ws.send(b'{"msg_type":"control:hello"}')
        time.sleep(0.5)
        ws.send(b'{"msg_type":"autopark:cmd_reverse","latitude":39.901695,"longitude":116.466088}')
        for i in range(8):
            time.sleep(1)
            ws.send(b'{"msg_type":"autopark:heartbeat_app","timestamp":39.91957}')
        time.sleep(5)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

def on_message(ws, message):
    print(f"### msg: {message}")

def on_error(ws, error):
    print(f"### error msg: {error}")

def on_close(ws):
    print("### closed ###")