#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.management.base import BaseCommand
from optparse import make_option
from django.conf import settings
import os
from rapidsmsrw1000.apps.api.rhea.hl7toxml import *


def handle_notification():
    
    print "#### NEXT TRANSACTION #####"
    #### CHECK FOR NEW NOTIFICATIONS OR NON-SENT NOTICATIONS ####
    new_notifications = Notification.objects.all().exclude(pk__in = RheaRequest.objects.all().values('notification'))
    print "Nots: %d" % new_notifications.count()
    try:
        
        if new_notifications.exists():
            
            print "LAST NOTIFICATION: %s" % RheaRequest.objects.all().order_by('-id').values('notification')[0]
            
            print "Number of NEW NOTIFICATIONS : %d" % new_notifications.count()
            cmd = RheaNotification()
            for n in new_notifications:
                report = Report.objects.get(pk = n.report.pk)
                notif = cmd.createOutgoingNotification(report)
                response = cmd.sendNotification(notif)
                                    
        else:
            print "LAST NOTIFICATION :%s" % RheaRequest.objects.all().order_by('-id').values('notification')[0]
            
            print "THEARE ARE NO NEW NOTIFICATIONS "
                                 
    except Exception, e:
        print e
        pass
    print "######## END OF TRANSACTION #######"

    return True
        
	

class Command(BaseCommand):
	help   = "Check for new Notifications and Send them ... NEED TO RUN THIS COMMAND IN CRON FOR EVERY MINUTES"	

	def handle(self, **options):
		print "CHECK NOTIFICATIONS"
		try:
    			print 'Use Control-C to exit or run ./manage stoprhea in another terminal'
        		handle_notification()
		except KeyboardInterrupt:
			print 'CHECK NOTIFICATION COMPLETE'
		
			
			
