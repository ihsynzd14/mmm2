from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import NotFound
from datetime import datetime, timedelta
from backend.models import *
import logging
import re

log = logging.getLogger("django.request")
#HEX-RE : mymedbook.netfarm.it/mymedtag/?code=.*[EOL]
DATAHEXRE=r"2F6D796D65647461672F3F636F64653D(.*?)FE"
ERROR = 'UI=950830\t'
SUCCESS = 'UI=AA0599\tHB=0005\t'
HANDLESUCCESS = 'UI=550830\tHB=0300\t'
MUTESUCCESS = 'UI=150830\tHB=0300\t'
@csrf_exempt
def orbitHandler(request):
	cmd = request.GET.get('cmd', None)
	mac = request.GET.get('mac', None)
	response="<html><body><ORBIT>%s</ORBIT></body></html>"
	if cmd == 'CO':
		uid = request.GET.get('uid', None)
		data = request.GET.get('data', None)
		try:
			sensor = Sensor.objects.get(identifier=mac)
			mmtcode=None
			matches = re.search(DATAHEXRE, data)
			if matches and len(matches.groups())>0:
				mmtcode = matches.groups(0)[0].decode('hex')
				log.info("READ TAG: %s" % mmtcode)
			else:
				try:
					serial = Serial.objects.get(serial_tag=uid)
					mmtcode=serial.MMTCode
					log.info("FOUND TAG: %s" % mmtcode)
				except:
					pass
			if mmtcode is None:
				log.error("TAG NOT FOUND %s %s" % (uid,data))
				return HttpResponse(response % ERROR) 
			user = None
			mmtag = MyMedTag.objects.get(code=mmtcode)
			membership_tag = False
			if mmtag.structure_affiliation:
				user = mmtag.structure_affiliation.user
			elif mmtag.structure_membership:
				membership_tag = True
				user = mmtag.structure_membership.user
			if user is None:
				raise NotFound()

			lowerbound = datetime.now() - timedelta(hours=1)
			for alarm in Alarm.objects.filter(sensor=sensor,handled=False,date__gt=lowerbound)[:1]:
				if membership_tag and alarm.caller.id!=user.id:
					alarm.handled=True
					alarm.handler=user
					alarm.save()
					log.info("HANDLED ALARM BY: %s" % mmtcode)
					return HttpResponse(response % HANDLESUCCESS)
				break
			else:
				log.info("FIRED ALARM BY: %s" % mmtcode)
				alarm = Alarm.objects.create(message='Richiesta di assistenza ',caller=user,sensor=sensor,date=datetime.now())
			return HttpResponse(response % SUCCESS)
		except Exception as e:
			log.exception(e)
			return HttpResponse(response % ERROR)
	elif mac is not None:
		try:
			sensor = Sensor.objects.get(identifier=mac)
			suffix=''
			lowerbound = datetime.now() - timedelta(minutes=5)
			if Alarm.objects.filter(sensor=sensor,handled=False,date__gt=lowerbound).count()>0:
				suffix=SUCCESS
				log.info("RELAUNCH ALARM")
			else:
				log.info("NO ALARMS FOUND")
				suffix=MUTESUCCESS
			return HttpResponse(response % "MAUTH=3\tNSTART=03\tNEND=18\t%s" % suffix);
		except Exception as e:
			log.exception(e)
			return HttpResponse(response % '')
	log.error("")
	return HttpResponse(response % '')
