#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from django.conf.urls.defaults import *
from .views import * 

urlpatterns = patterns(
                       '',
                       url(r'^$', index),
                       url(r'adduser$', add_user),
    )