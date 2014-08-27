#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.management.base import BaseCommand
from optparse import make_option
from django.conf import settings
import os
from rapidsmsrw1000.apps.api.rhea.hl7toxml import *


def handle_test():
    
    print "#### START TEST #####"
    #### CHECK FOR TESTING NOTIFICATIONS ####

    cmd = RheaNotification()

    patient = {'name': 'Patient Gatanu' , 'nid': '9900445566778843'}
    reporter = {'name': 'Patient Gatanu' , 'nid': '3525410'}
    ip = '41.74.172.115'
    port = '5000'

    birth   =   Report.objects.filter(type__name = 'Birth')[0]
    risk    =   Report.objects.filter(type__name = 'Risk')[0]
    death   =   Report.objects.filter(type__name = 'Death')[0] 

    print "#### BIRTH NOTIFICATION ####"
    
    try:
        
        url = "/ws/rest/v1/patient/NID-%s/encounters?notificationType=BIR" % patient['nid']
        birth.patient.national_id = patient['nid']
        birth.reporter.national_id = reporter['nid']
        report = birth
        notif, crated = Notification.objects.get_or_create(not_type = NotificationType.objects.get(name = report.type.name), report = report)
        data = cmd.createOutgoingNotification(report)
        print "\nURL: %s\n" % url
        print "\nDATA: %s\n" % data
        
        request = create_rhea_request(url,data.message)

        res = get_rhea_response(request)
        
        
        print "\nRESPONSE STATUS_REASON: %s\n RESPONSE MESSAGE: %s\n" % (res['status_reason'], res['response'])                  
                                 
    except Exception, e:
        print "Error: %s" % e
        pass

    print "#### END BIRTH NOTIFICATION ####"

    print "#### RISK NOTIFICATION ####"
    
    try:
        
        url = "/ws/rest/v1/patient/NID-%s/encounters?notificationType=RISK" % patient['nid']
        risk.patient.national_id = patient['nid']
        risk.reporter.national_id = reporter['nid']
        report = risk
        notif, crated = Notification.objects.get_or_create(not_type = NotificationType.objects.get(name = report.type.name), report = report)
        data = cmd.createOutgoingNotification(report)
        print "\nURL: %s\n" % url
        print "\nDATA: %s\n" % data
        
        request = create_rhea_request(url,data.message)

        res = get_rhea_response(request)
        
        
        print "\nRESPONSE STATUS_REASON: %s\n RESPONSE MESSAGE: %s\n" % (res['status_reason'], res['response'])                  
                                 
    except Exception, e:
        print "Error: %s" % e
        pass

    print "#### END RISK NOTIFICATION ####"

    print "#### DEATH NOTIFICATION ####"
    
    try:
        
        url = "/ws/rest/v1/patient/NID-%s/encounters?notificationType=MAT" % patient['nid']
        death.patient.national_id = patient['nid']
        death.reporter.national_id = reporter['nid']
        report = death
        notif, crated = Notification.objects.get_or_create(not_type = NotificationType.objects.get(name = report.type.name), report = report)
        data = cmd.createOutgoingNotification(report)
        print "\nURL: %s\n" % url
        print "\nDATA: %s\n" % data
        
        request = create_rhea_request(url,data.message)

        res = get_rhea_response(request)
        
        
        print "\nRESPONSE STATUS_REASON: %s\n RESPONSE MESSAGE: %s\n" % (res['status_reason'], res['response'])                  
                                 
    except Exception, e:
        print "Error: %s" % e
        pass

    print "#### END DEATH NOTIFICATION ####"

    return True
        
	

class Command(BaseCommand):
	help   = "Check for new Notifications and Send them ... NEED TO RUN THIS COMMAND IN CRON FOR EVERY MINUTES"	

	def handle(self, **options):
		print "CHECK NOTIFICATIONS"
		try:
    			print 'Use Control-C to exit or run ./manage stoprhea in another terminal'
        		handle_test()
		except KeyboardInterrupt:
			print 'CHECK NOTIFICATION COMPLETE'
		
			
			
