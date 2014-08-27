#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.management.base import BaseCommand
from optparse import make_option
from django.conf import settings
import os

def stop_server():

	os.system("fuser -k %s/tcp" % settings.RHEA_PORT) 		


class Command(BaseCommand):
	help   = "RHEA SUPPORT STOP RUNNING"
	
	def handle(self, **options):
        	
		stop_server()
			
		print "RHEA SUPPORT STOP RUNNING -- The RHEA Support for RAPIDSMS RWANDA 1000 system is now Down.\n\nExiting\n"
		return
