#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

import os 
import subprocess
from django.db import connection
from django.db.models import get_app, get_models
from django.db import models
from rapidsmsrw1000.apps.api.utils import *


THIS_PATH = os.path.dirname(os.path.abspath(__file__))


def create_location_type_model(name, short_name, code_max_length = 50, name_max_length = 50, locs = [], 
                               international_phone_code = "+250", phone_number_length = 9, subtype = False):

    try:
        status = False
        model_name = camelCase(name)
        locs_data = "".join("\n\t%s = models.ForeignKey(%s, null = True, blank = True)" % (camel_to_underscore_lower(l),camelCase(l)) for l in locs)
        variables_data = "\n\tname = models.CharField(max_length=%d)\
                         \n\tcode = models.CharField(max_length=%d, unique=True)\
                         \n\tcreated = models.DateTimeField(auto_now_add=True)" % (name_max_length, code_max_length)
        if subtype:
            variables_data = variables_data + "\n\ttype = models.CharField(max_length = 100, null = True, blank = True)"
            variables_data = variables_data + "\n\treferral = models.ForeignKey('%s', null = True, blank = True)" % model_name
            
        print variables_data, subtype
        default_value = "\n\n\tdef __unicode__(self):\n\t\treturn '%s' % (self.name)"
        meta_value = "\n\n\tclass Meta:\n\t\tpermissions = (\n\t\t\t('can_view', 'Can view'),\n\t\t)"
        start_value = "##Start of %s" % model_name
        end_value = "##End of %s" % model_name
        admin_locs = "".join("'%s', "  % l.lower() for l in locs )
        #print admin_locs
        admin_value = "\n%s\nclass %sAdmin(admin.ModelAdmin):\
                                                        \n\tlist_filter = (%s)\
                                                        \n\texportable_fields = ('name', 'code', %s)\
                                                        \n\tsearch_fields = ('name','code')\
                                                        \n\tlist_display = ('name','code', %s)\
                                                    \n\tactions = (export_model_as_csv, export_model_as_excel)\
                        \n\nadmin.site.register(%s, %sAdmin)\n%s\n" \
                        % (start_value, model_name, admin_locs, admin_locs, admin_locs, model_name, model_name, end_value)
        admin_rep = "\nclass %sAdmin(admin.ModelAdmin):\
                                                        \n\tlist_filter = (%s)\
                                                        \n\texportable_fields = ('name', 'code', %s)\
                                                        \n\tsearch_fields = ('name','code')\
                                                        \n\tlist_display = ('name','code', %s)\
                                                    \n\tactions = (export_model_as_csv, export_model_as_excel)\
                    \n\nadmin.site.register(%s, %sAdmin)\n" % (model_name, admin_locs, admin_locs, admin_locs, model_name, model_name)
        data = "\n%s\nclass %s(models.Model):\n%s%s%s%s\n%s\n" % (start_value, model_name, variables_data, locs_data, default_value, meta_value, end_value)
        data_rep = "\nclass %s(models.Model):\n%s%s%s%s\n" % (model_name, variables_data, locs_data, default_value, meta_value)

        ##print admin_value, admin_rep
        model_defined = False
        model_admin_defined = False 
        #print THIS_PATH
        
        """
        f = open("%s/models.py" % THIS_PATH, "r+a")
        for line in f:
            model_defined_name = "class %s(models.Model):" % model_name
            
            if model_defined_name in line:
                #print line
                model_defined = True                
                break
            else:   
                continue

        if not model_defined:   f.write(data)
        f.close()
        """

        
        """
        admin_f = open("%s/admin.py" % THIS_PATH, "r+a")
        for line in admin_f:
            admin_defined_name =  "class %sAdmin(admin.ModelAdmin):" % model_name
            if admin_defined_name in line:
                #print line
                model_admin_defined = True                
                break
            else:   
                continue
           
        if not model_admin_defined:   admin_f.write(admin_value)
        admin_f.close()
        """
        
        lt, created = LocationType.objects.get_or_create(name = name)
        lt.short_name = short_name
        lt.international_phone_code = international_phone_code
        lt.phone_number_length = phone_number_length
        lt.model_text = data
        lt.admin_text = admin_value
        lt.start_text = start_value
        lt.end_text = end_value
        lt.save()
        
        ##CHEK IF MODEL NOT DEFINED ALREADY
        m_filename = "%s/models.py" % THIS_PATH
        m_f = get_block_of_text(m_filename, model_name, lt.start_text,  lt.end_text)
        
        if m_f:
            #print "THERE 1"
            if m_f['lines'] and m_f['start'] and m_f['end']:
                x = replace_block_of_text(m_filename, m_f['lines'], m_f['start'], m_f['end'], replace_with = data_rep)
                #print x 
            else:
                with open(m_filename, "a") as f:
                    f.write(data)
                    f.close()
        
        ##CHEK IF MODEL IN ADMIN NOT DEFINED ALREADY
        a_filename = "%s/admin.py" % THIS_PATH
        a_f = get_block_of_text(a_filename, model_name, lt.start_text,  lt.end_text)
        if a_f:
            if a_f['lines'] and a_f['start'] and a_f['end']:
                y = replace_block_of_text(a_filename, a_f['lines'], a_f['start'], a_f['end'], replace_with = admin_rep) 
                #print y
            else:
                with open(a_filename, "a") as f:
                    f.write(admin_value)
                    f.close()
                                   
        dump_st = dump_fixtures_to_json(lt._meta.app_label, model_name)
        status = propagate_db(get_model_object(lt._meta.app_label, model_name))
        load_st = load_fixtures_from_json(lt._meta.app_label, model_name)

        return status

    except Exception, e:
        #print e
        return False
    
def get_block_of_text(filename, model_name, start,  end):
    
    start_index = None
    end_index = None
    
    input_data = open(filename, "r")
    lines = input_data.readlines()
    # Skips text before the beginning of the interesting block:
    for i, line in enumerate(lines):
        if line.strip() == start:  # Or whatever test is needed
            start_index = i
            break
    # Reads text until the end of the block:
    for i, line in enumerate(lines):  # This keeps reading the file
        if line.strip() == end:
            end_index = i 
            break 
    
    input_data.close()
    
    return {'lines': lines, 'start': start_index, 'end': end_index}


def replace_block_of_text(filename, lines, start, end, replace_with = ""):
    block_of_data = ""
    input_data = open(filename, "w")#; print start, end, replace_with                
    for i, line in enumerate(lines):
        if start < i < end:
            block_of_data = block_of_data + line
            if i == end - 1: 
                input_data.write(replace_with)
        else:
            input_data.write(line)
                
    input_data.close()
    
    return block_of_data

def get_model_object(app_label, model_name):
    app = get_app(app_label)
    m = get_models(app)
    #print m, model_name
    for m1 in m:
        if m1.__name__ == model_name:
            return m1
    return None

def propagate_db(model_object):

    try:
        
        try: 
            #print model_object
            obj = model_object()
            table = obj._meta.db_table
            cursor = connection.cursor()
            cursor.execute("drop table %s" % table)
            cursor.close()
        except Exception, e:
            #print "DROPPING ERROR: %s" % e
            pass
            
        return_code = subprocess.call("cd %s && ./manage.py syncdb" % os.getcwd(), shell=True)  
    except Exception,e:
        #print "ERROR DB: %s, %s" % (e, model_object)
        return False
        
    return True

def dump_fixtures_to_json(app_label, model_name):
    try:
        directory = "%s/fixtures/%s" % (os.getcwd(), app_label)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        return_code = subprocess.call("cd %s && ./manage.py dumpdata --format=json %s.%s > %s/%s.json" % (os.getcwd(), app_label, model_name.lower(), 
                                                                                                          directory, model_name.lower()), shell=True)
    
    except Exception, e:
        #print "DUMP ERROR: %s" % e
        return False
    
    return True

def load_fixtures_from_json(app_label, model_name):
    try:
        directory = "%s/fixtures/%s" % (os.getcwd(), app_label)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        return_code = subprocess.call("cd %s && ./manage.py loaddata %s/%s.json" % (os.getcwd(), directory, model_name.lower()),\
                                       shell=True)
    except Exception, e:
        #print "LOADING ERROR: %s" % e
        return False
    return True
    
    

class LocationType(models.Model):
    
    name = models.CharField(max_length=100, unique = True)
    short_name = models.CharField(max_length=30, null=True, blank=True)
    international_phone_code = models.CharField(max_length=30, null=True, blank=True)
    phone_number_length = models.IntegerField(null=True, blank=True)
    top_level = models.BooleanField(default = False)
    model_text = models.TextField(null=True, blank=True)
    admin_text = models.TextField(null=True, blank=True)
    start_text = models.TextField(null=True, blank=True)
    end_text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        permissions = (
            ('can_view', 'Can view'),
        )

##Start of Nation
class Nation(models.Model):

	name = models.CharField(max_length=30)                         
	code = models.CharField(max_length=2, unique=True)                         
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return '%s' % (self.name)

	class Meta:
		permissions = (
			('can_view', 'Can view'),
		)
##End of Nation

##Start of Province
class Province(models.Model):

	name = models.CharField(max_length=50)                         
	code = models.CharField(max_length=4, unique=True)                         
	created = models.DateTimeField(auto_now_add=True)
	nation = models.ForeignKey(Nation)

	def __unicode__(self):
		return '%s' % (self.name)

	class Meta:
		permissions = (
			('can_view', 'Can view'),
		)
##End of Province

##Start of District
class District(models.Model):

	name = models.CharField(max_length=60)                         
	code = models.CharField(max_length=6, unique=True)                         
	created = models.DateTimeField(auto_now_add=True)
	nation = models.ForeignKey(Nation)
	province = models.ForeignKey(Province)

	def __unicode__(self):
		return '%s' % (self.name)

	class Meta:
		permissions = (
			('can_view', 'Can view'),
		)
##End of District

##Start of HealthFacility

class HealthFacility(models.Model):

	name = models.CharField(max_length=60)                         
	code = models.CharField(max_length=4, unique=True)                         
	created = models.DateTimeField(auto_now_add=True)
	type = models.CharField(max_length = 100, null = True, blank = True)
	referral = models.ForeignKey('HealthFacility', null = True, blank = True)
	nation = models.ForeignKey(Nation)
	province = models.ForeignKey(Province)
	district = models.ForeignKey(District)

	def __unicode__(self):
		return '%s' % (self.name)

	class Meta:
		permissions = (
			('can_view', 'Can view'),
		)
##End of HealthFacility
