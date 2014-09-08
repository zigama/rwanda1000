#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

import re
import os
import subprocess
from django.db.models import get_app, get_models
from django.db import connection
import unicodecsv as csv
from django.contrib.admin import util as admin_util
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.http import HttpResponse
import datetime
import xlwt

API_PATH = os.path.dirname(os.path.abspath(__file__))

def add_four_space(data_space = "aaaa"):     
    return data_space.replace("a", " ")

def camelCase(st):
    output = ''.join(x for x in st.title() if x.isalpha())
    return output[0].upper() + output[1:]

def camel_to_underscore_lower(st):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', st)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(" ", "")

### As every model to be created needs to implemented with a feature to locate data it is linked to
### We thereby need to put a block starting with ##START OF (LOCATION TYPE) LINK and ending with ##END OF (LOCATION TYPE) LINK

def link_model_with(app_label, model_name, location_type):
    try:
        filename = "%s/%s/models.py" % (API_PATH, app_label)
        model_object = get_model_object(app_label, model_name)
        field_name = camel_to_underscore_lower(location_type)
        data = add_location_link_to_table(filename, model_object, field_name)
    except Exception, e:
        #print e
        return False
    return True
        

def add_location_link_to_table(filename, model_object, field_name):
    try:
        start_text = "##START OF %s LINK" % field_name.upper()
        field_text = "%s = models.ForeignKey(%s, null = True, blank = True)" % (field_name, camelCase(field_name))
        end_text = "##END OF %s LINK" % field_name.upper()
        #print field_text
        model_block = get_block_of_text_link(filename, model_name = model_object._meta.object_name, start = "##Start of %s" % model_object._meta.object_name,\
                                         end = "##End of %s" % model_object._meta.object_name)
        if model_block:
            #print model_block['start'], model_block['end']
            link_block = get_block_of_text_link(filename, model_name = model_object._meta.object_name, start = "##START OF LINK TO LOCATION TYPES" ,\
                               end = "##END OF LINK TO LOCATION TYPES")
            if link_block['start'] and link_block['end']:
                #print  link_block['start'], link_block['end']
                type_block = get_block_of_text_link(filename, model_name = model_object._meta.object_name, start = "##START OF %s LINK" % field_name.upper(),\
                               end = "##END OF %s LINK" % field_name.upper())
                
                syntax_link = "\n%s%s\n%s%s\n%s%s\n" % (add_four_space(), start_text, add_four_space(), field_text, add_four_space(), end_text)
                if type_block:
                    if type_block['start'] and type_block['end']:
                        pass
                    else:
                        y = update_block_of_text_link(filename, link_block['lines'], link_block['start'], link_block['end'], update_with = syntax_link)
                        try: 
                            obj = model_object()
                            table = obj._meta.db_table
                            print table, model_object
                            cursor = connection.cursor()
                            cursor.execute("ALTER TABLE `%s` ADD `%s_id` INT NOT NULL" % (table, field_name))
                            cursor.close()
                            return_code = subprocess.call("cd %s && ./manage.py syncdb" % os.getcwd(), shell=True)  
                        except Exception, e:
                            #print "DROPPING ERROR: %s" % e
                            pass
    except Exception, e:
        #print e
        return False
    return True

def add_column_textfield_to_table(filename, model_object, field_name, marker, help_text):
    #print filename, model_object, field_name, foreign_key, marker 
    try:
        start_text = "##START OF %s" % marker
        field_text = "%s = models.TextField(null = True, blank = True, help_text = '%s')" % (field_name, help_text)
        end_text = "##END OF %s" % marker
        #print field_text
        model_block = get_block_of_text_link(filename, model_name = model_object._meta.object_name, start = "##Start of %s" % model_object._meta.object_name,\
                                         end = "##End of %s" % model_object._meta.object_name)
        if model_block:
            #print model_block['start'], model_block['end']
            if model_block['start'] and model_block['end']:
        
                type_block = get_block_of_text_link(filename, model_name = model_object._meta.object_name, start = start_text, end = end_text)
                
                if type_block:
                    if type_block['start'] and type_block['end']:
                        #print type_block['start'], type_block['end'], field_text
                        syntax_link = "\n%s%s\n" % (add_four_space(), field_text)
                        if field_name in model_object._meta.get_all_field_names():
                            pass
                        else:
                            #print field_name, model_object._meta.get_all_field_names()
                            table = model_object._meta.db_table
                            cursor = connection.cursor()
                            cursor.execute("ALTER TABLE `%s` ADD `%s` TEXT NULL" % (table, field_name))
                            cursor.close()
                            y = update_block_of_text_link(filename, type_block['lines'], type_block['start'], type_block['end'], update_with = syntax_link)
                        
                    else:
                        print "NO BLOCK"
    except Exception, e:
        #print e
        return False
    return True
    

def get_block_of_text_link(filename, model_name, start,  end):
    
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

def replace_block_of_text_link(filename, lines, start, end, replace_with = ""):
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

def export_model_as_csv(modeladmin, request, queryset):
    if hasattr(modeladmin, 'exportable_fields'):
        field_list = modeladmin.exportable_fields
    else:
        # Copy modeladmin.list_display to remove action_checkbox
        field_list = modeladmin.list_display[:]
        #field_list.remove('action_checkbox')

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s-%s-export-%s.csv' % (
        __package__.lower(),
        queryset.model.__name__.lower(),
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
    )

    writer = csv.writer(response)
    writer.writerow(
        [admin_util.label_for_field(f, queryset.model, modeladmin).upper() for f in field_list],
    )

    for obj in queryset:
        csv_line_values = []
        for field in field_list:
            field_obj, attr, value = admin_util.lookup_field(field, obj, modeladmin)
            csv_line_values.append(value)

        writer.writerow(csv_line_values)

    return response
export_model_as_csv.short_description = _('Export to CSV')



def export_model_as_excel(modeladmin, request, queryset):
    has_name_fields = ['village', 'cell', 'sector', 'health_centre', 'referral_hospital', 'district', 'province','role', 'nation']
    is_date_fields = ['date_of_birth', 'dob', 'join_date']
    has_keys = ['sms_report_field', 'depends_on_value_of']
    has_keyword = ['sms_report']  
    is_datetime_fields = ['created']
    workbook = xlwt.Workbook()
    sheet_name = "%s" % ( queryset.model.__name__.lower(), )
    sheet = workbook.add_sheet(sheet_name)
    if hasattr(modeladmin, 'exportable_fields'):
        field_list = modeladmin.exportable_fields
    else:
        # Copy modeladmin.list_display to remove action_checkbox
        field_list = modeladmin.list_display[:]
        #field_list.remove('action_checkbox')

    response = HttpResponse(mimetype = "application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % sheet_name

    row = col = 0
    for f in field_list:
        sheet.write(row , col, admin_util.label_for_field(f, queryset.model, modeladmin).upper())
        col = col + 1

    row = row + 1
    for obj in queryset:
        excel_line_values = []
        col = 0
        for field in field_list:
            field_obj, attr, value = admin_util.lookup_field(field, obj, modeladmin)

            try:
                if field in has_name_fields:  sheet.write(row, col, value.name)
                elif field in has_keys: sheet.write(row, col, "%s" % (value.key))
                elif field in has_keyword: sheet.write(row, col, "%s" % (value.keyword))
                elif field in is_date_fields: sheet.write(row, col, "%d/%d/%d" % (value.day, value.month, value.year))
                elif field in is_datetime_fields: sheet.write(row, col, "%d/%d/%d %d:%d:%d" % (value.day, value.month, value.year,
                                                                                            value.hour, value.minute, value.second))
                else:   sheet.write(row, col, value)
            except Exception, e:
                try:    sheet.write(row, col, value)
                except: sheet.write(row, col, "NULL")
            col = col + 1
        row = row + 1

    workbook.save(response)
    return response

export_model_as_excel.short_description = _('Export to EXCEL')

