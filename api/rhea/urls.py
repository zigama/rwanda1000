#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from piston.resource import Resource
from rapidsmsrw1000.apps.api.rhea.piston_handlers import *
import rapidsmsrw1000.apps.api.rhea.views as views



auth = HttpBasicAuthentication(realm="RapidSMS Rwanda 1000 RHEA API")
user_handler = Resource(UserHandler, authentication=auth)
patient_handler = Resource(PatientHandler,authentication=auth)
alert_handler = Resource(AlertHandler,authentication=auth)


#print auth

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^patients$', patient_handler),
    url(r'^users(?P<emitter_format>.+)$', user_handler,{ 'emitter_format': 'xml' }),
    url(r'^patients/(?P<patient_id>\d+)$', patient_handler,{'emitter_format': 'xml' }),
    url(r'^patients/alerts$', alert_handler),
    url(r'^ws/rest/v1/alerts/(?P<patient_id>\d+)$', alert_handler),
    url(r'^ws/rest/v1/alerts$', alert_handler,{ 'emitter_format': 'xml' }),
    
    
    
)
