#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from .models import *
from django.contrib.auth.models import *
from rapidsmsrw1000.apps.api.reports.models import SMSReport

@permission_required('locations.can_view')
def index(req, **flts):
    req.base_template = "webapp/layout.html"
    
    error = ""
    if req.method == 'POST':
        try:
            name = req.POST['name']
            short_name = req.POST['short_name']
            max_name_l = int(req.POST['max_name_l'])
            max_code_l = int(req.POST['max_code_l'])
            locs = req.POST.getlist('locs')
            has_subtype = req.POST.getlist('subtype')
            #print name, short_name, max_name_l, max_code_l, locs
            try:
                international_phone_code = req.POST['phone_code']
                phone_number_length = int(req.POST['phone_l'])
                resp = create_location_type_model(name = name, short_name = short_name, code_max_length = max_code_l, name_max_length = max_name_l, locs = locs,\
                                                  international_phone_code = international_phone_code, phone_number_length = phone_number_length, subtype = has_subtype)
            except:
                resp = create_location_type_model(name = name, short_name = short_name, code_max_length = max_code_l, name_max_length = max_name_l, 
                                                  locs = locs, subtype = has_subtype)
        except Exception, e:
            #print e 
            error = "Invalid or Empty Data Supplied: %s" % e
    
    loc_types = LocationType.objects.all()
    
    return render_to_response("locations/admin.html",
                              dict(loc_types = loc_types, error = error),
                              context_instance=RequestContext(req))

@permission_required('locations.can_view')    
def add_user(req, **flts):
    req.base_template = "webapp/layout.html"
    loc_types = LocationType.objects.all()
    error = ""
    ugroups =Group.objects.all()
    sms_reports = SMSReport.objects.all()
    return render_to_response("locations/user.html",
                              dict(loc_types = loc_types, error = error, ugroups = ugroups, sms_reports = sms_reports),
                              context_instance=RequestContext(req))
    