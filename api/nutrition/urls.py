#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from django.conf.urls.defaults import *
from piston.resource import Resource
from rapidsmsrw1000.apps.api.nutrition.piston_handlers import *
import rapidsmsrw1000.apps.api.nutrition.views as views

#auth = HttpBasicAuthentication(realm="RapidSMS Rwanda 1000 WOMAN API")
#woman_handler = Resource(WomanHandler,authentication=auth)
child_handler = Resource(ChildHandler)
cbn_handler = Resource(ChildNutritionHandler)
stats_handler = Resource(StatisticsHandler)
province_handler = Resource(ProvinceHandler)
district_handler = Resource(DistrictHandler)
healthcentre_handler = Resource(HealthCentreHandler)

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^child$', child_handler),
    url(r'^cbn$', cbn_handler),
    url(r'^province$', province_handler),
    url(r'^district$', district_handler),
    url(r'^healthcentre$', healthcentre_handler),
    url(r'^child/(?P<pk>\d+)', child_handler),
    url(r'^stats/data$', stats_handler),
    url(r'^stats/key/(?P<key>\w+)', views.cbnindicator),
    url(r'^stats$', views.statistics),
    url(r'^cbnreport$', views.cbn),
       
)
