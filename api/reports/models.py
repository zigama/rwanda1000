#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

import os
from django.db import models
from rapidsmsrw1000.apps.api.messaging.models import *
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
import keyword

THIS_PATH = os.path.dirname(os.path.abspath(__file__))

def get_field_name(f):
    f_key = getattr(f, 'key')
    f_key = "%s_key" % f_key
    return f_key
    

def create_or_update_sms_report_model(filename = "%s/models.py" % THIS_PATH, sms_report = SMSReport(), sms_report_fields = [],
                                         links = {'app_lable': '', 'model_name': ''}, default_return = 'raw_sms'):
    """
        Field in the form of {key, type_of_value, length(min, max), required, value(min,max)} 
        locations are all Location Types already defined        
    """

    try:
        tab = add_four_space()
        status = False
        model_name = "%sTable" % camelCase(sms_report.keyword)

        start_text = "##Start of %s" % model_name
        end_text = "##End of %s" % model_name

        start_fields_text = "##Start of %s Fields" % model_name
        end_fields_text = "##End of %s Fields" % model_name

        start_meta_text = "##Start of %s Meta" % model_name
        end_meta_text = "##End of %s Meta" % model_name

        start_methods_text = "##Start of %s Methods" % model_name
        end_methods_text =  "##End of %s Methods" % model_name

        locs_data = "".join("\n%s%s = models.ForeignKey(%s, null = True, blank = True)" % (tab, camel_to_underscore_lower(l), camelCase(l)) for l in locations)
        links_data = "".join("\n%s%s = models.ForeignKey(%s, null = True, blank = True)" % (tab, camel_to_underscore_lower(l), camelCase(l)) for l in links)
        variables_data = ""
        
        for f in sms_report_fields:
            min_lf = getattr(f, 'minimum_length')
            max_lf = getattr(f, 'maximum_length')
            min_vf = getattr(f, 'minimum_value')
            max_vf = getattr(f, 'maximum_value')
            type_of_vf = getattr(f, 'type_of_value')
            required_f = getattr(f, 'required')

            if  type_of_vf == 'integer':
                
                vf = "\n%s%s = models.IntegerField(validators = [MinValueValidator(%d), MaxValueValidator(%d)], null = %s,  blank = %s\
                                                         )" % (tab, get_field_name(f), min_vf, max_vf, required_f, required_f) 
                variables_data = variables_data.join(vf)
                
            elif type_of_vf == 'string':
                
                vf = "\n%sname = models.CharField(max_length = %d , validators = [MinLengthValidator(%d)], null = %s,  blank = %s\
                                                         )" % (tab, get_field_name(f), max_lf, min_lf, required_f, required_f) 
                variables_data = variables_data.join(vf)
                
            elif type_of_vf == 'date':
                
                vf = "\n%sname = models.DateField(validators = [MinValueValidator(%d), MaxValueValidator(%d)], null = %s,  blank = %s\
                                                         )" % (tab, get_field_name(f), min_vf, max_vf, required_f, required_f) 
                variables_data = variables_data.join(vf)
            else:
                vf = "\n%sname = models.TextField(validators = [MinLengthValidator(%d), MaxLengthValidator(%d)], null = %s,  blank = %s\
                                                         )" % (tab, get_field_name(f), min_lf, max_lf, required_f, required_f) 
                variables_data = variables_data.join(vf)
        
        variables_data = variables_data.join("\n%sraw_sms = models.TextField()" % (tab)        
        default_value = "\n\n%sdef __unicode__(self):\n%s%sreturn self.%s" % (tab, tab, tab, default_return)
        meta_value = "\n\n%sclass Meta:\n%s%spermissions = (\n%s%s%s('can_view', 'Can view'),\n%s%s)" % (tab, tab, tab, tab, tab, tab, tab, tab )
        admin_locs = "".join("'%s', "  % camel_to_underscore_lower(l) for l in locations )
        admin_links = "".join("'%s', "  % camel_to_underscore_lower(l) for l in links )
        admin_fields = "".join("'%s', "  % get_field_name(f).lower() for f.key in sms_report_fields )
        
        admin_value = "\n%s\nclass %sAdmin(admin.ModelAdmin):\
                                                        \n%slist_filter = ()\
                                                        \n%sexportable_fields = (%s )\
                                                        \n%ssearch_fields = (%s )\
                                                        \n%slist_display = (%s )\
                                                    \n%sactions = (export_model_as_csv, export_model_as_excel)\
                        \n\nadmin.site.register(%s, %sAdmin)\n%s\n" \
                        % (start_text, model_name, 
                           tab,
                           tab, admin_fields,
                           tab, admin_fields, 
                           tab, admin_fields,
                           tab,
                           model_name, model_name, end_text)
        admin_rep = "\nclass %sAdmin(admin.ModelAdmin):\
                                                        \n%slist_filter = ()\
                                                        \n%sexportable_fields = (%s )\
                                                        \n%ssearch_fields = (%s )\
                                                        \n%slist_display = (%s )\
                                                    \n%sactions = (export_model_as_csv, export_model_as_excel)\
                        \n\nadmin.site.register(%s, %sAdmin)\n" \
                        % (model_name, 
                           tab,  
                           tab, admin_fields,
                           tab, admin_fields,
                           tab, admin_fields,
                           tab,
                           model_name, model_name)
        data = "\n%s\nclass %s(models.Model):\n%s%s%s%s\n%s\n" \
                    % (start_text, model_name, variables_data, locs_data, default_value, meta_value, end_text)
        data_rep = "\nclass %s(models.Model):\n%s%s%s%s\n" \
                    % (model_name, variables_data, locs_data, default_value, meta_value)

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
        
        
        lt, created = LocationType.objects.get_or_create(name = model_name)
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
                                   
        #dump_st = dump_fixtures_to_json(lt._meta.app_label, model_name)
        #status = propagate_db(get_model_object(lt._meta.app_label, model_name))
        #load_st = load_fixtures_from_json(lt._meta.app_label, model_name)

        return status
        """
        return data, admin_value

    except Exception, e:
        print e
        return False
    
