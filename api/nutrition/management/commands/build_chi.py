#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsmsrw1000.apps.api.nutrition.utils import *
from django.core.management.base import BaseCommand
from optparse import make_option

class Command(BaseCommand):
    help = "Build our Nutrition Statistics."
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry',
                    action='store_true',
                    dest='dry',
                    default=False,
                    help='Executes a dry run, doesnt send messages or update the db.'),
        )
	
    def handle(self, **options):
        print "Running build nutrition.."

        self.dry = options['dry']

        if self.dry:
            self.dry = True
            print "DRY RUN -- No messages will be sent, no database commits made."

        try:
            build_nutrition_chi()                
            
        except Exception, e:
            print e

        print "Complete."

        if self.dry:
            print "DRY RUN Complete."
