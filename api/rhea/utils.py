#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf import settings

from rapidsmsrw1000.apps.smser import Smser
from rapidsmsrw1000.apps.api.rhea.models import *

import pycurl, StringIO
from BaseHTTPServer import BaseHTTPRequestHandler


conf = settings.RHEA["api"]


def create_rhea_request(url,data):
	try:
		curl = pycurl.Curl()
		curl.setopt(pycurl.SSL_VERIFYPEER, 0)
		curl.setopt(pycurl.POSTFIELDS, "%s" % str(data))
		url = "https://%s:%s%s"%(conf["host"],conf["port"],url)
		curl.setopt(pycurl.URL, "%s" % str(url))
		curl.setopt(pycurl.USERPWD, "%s:%s" % (conf["user"], conf["pass"]))
		
		return [curl,data]
	except Exception ,e :
		pass
	return False
	
def get_rhea_response(request):
	response = {}
	try:
		data = request[1]
		request = request[0]
		contents = StringIO.StringIO()
		hdr = StringIO.StringIO()
		request.setopt(pycurl.WRITEFUNCTION, contents.write)
		request.setopt(pycurl.HEADERFUNCTION, hdr.write)
		request.perform()
		response_code = request.getinfo(pycurl.HTTP_CODE)
		header = request.getinfo(pycurl.EFFECTIVE_URL)

		try:
			response_msg = BaseHTTPRequestHandler.responses[response_code][0]
		except:
			response_msg = "No Reason"

		
		response = {'request':header ,'data':data, 'response':contents.getvalue(), 'status_reason':"%s_%s"%(response_code, response_msg)}

	except Exception, e:
		response_code = e

	response['response_code'] = response_code

	return response


def send_reminder_message(reminder):
    #print reminder
    try:
        message = "Umubyeyi ufite irangamuntu numero %s uherereye (Akarere: %s, Umurenge %s, Akagari: %s, Umudugudu: %s) \
                 agomba kujya ku bitaro kubonana na muganga. Gerageza umwibutse kandi urebe uko wamufasha. Murakoze!"

        identity  = "250788660270"
        reporter =  Reporter.objects.get(national_id = reminder['reporter']['nid'])
        patient = Patient.objects.get(national_id = reminder['patient']['nid'])
        identity = reporter.connection().identity
        message = message % (patient.national_id, patient.district, patient.sector, patient.cell, patient.village)

        #print "\nReporter Telephone Number : %s\nMessage: %s\n" % (identity, message)
        sent = Smser().send_message_via_kannel(identity, message)
        if sent == True:    return (True, message)
        else:   return (False, message)   
    except Exception, e:
        return e
	


