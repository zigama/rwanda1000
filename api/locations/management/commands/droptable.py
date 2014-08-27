#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from rapidsmsrw1000.apps.api.locations.models import *
from django.core.management.base import BaseCommand
from optparse import make_option


def drop_tables():
    """ Please Drop table in the descending order of the one they have been created ..."""
    try:
        cursor = connection.cursor()
        lts = LocationType.objects.all().order_by('-id')
        for lt in lts:
            
            try:
                obj = get_model_object(lt._meta.app_label, lt.name)
                table = obj._meta.db_table
                #print obj, table, obj._meta.app_label, obj._meta.object_name

                dump_st = dump_fixtures_to_json(obj._meta.app_label, obj._meta.object_name)

                ##CHEK IF MODEL NOT DEFINED ALREADY
                m_filename = "%s/models.py" % THIS_PATH
                m_f = get_block_of_text(m_filename, obj._meta.object_name, lt.start_text,  lt.end_text)

                ##CHEK IF MODEL IN ADMIN NOT DEFINED ALREADY
                a_filename = "%s/admin.py" % THIS_PATH
                a_f = get_block_of_text(a_filename, obj._meta.object_name, lt.start_text,  lt.end_text)

                if m_f:
                    if m_f['lines'] and m_f['start'] and m_f['end']:
                        x = replace_block_of_text(m_filename, m_f['lines'], m_f['start'], m_f['end'], replace_with = "\n")

                if a_f:
                    if a_f['lines'] and a_f['start'] and a_f['end']:
                        y = replace_block_of_text(a_filename, a_f['lines'], a_f['start'], a_f['end'], replace_with = "\n") 

                cursor.execute("drop table %s" % table)

                
            except Exception, e:
                print e
                pass
        
        dlt = lts[0]
        dump_st = dump_fixtures_to_json(dlt._meta.app_label, dlt._meta.object_name)
        cursor.execute("drop table %s" % dlt._meta.db_table)            
        cursor.close()
        return_code = subprocess.call("cd %s && ./manage.py syncdb" % os.getcwd(), shell=True) 
    except Exception,e:
        print "ERROR DB: %s" % e
        pass        
    return True



class Command(BaseCommand):
    help = "Build our Table locations. Run in the cron, daily at 1 am"
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry',
                    action='store_true',
                    dest='dry',
                    default=False,
                    help='Executes a dry run, doesnt send messages or update the db.'),
        )
	
    def handle(self, **options):
        print "Running locations drop..."

        drop_tables()

        print " Droping tables Done"

