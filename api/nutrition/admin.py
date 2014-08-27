#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from django.contrib import admin
from rapidsmsrw1000.apps.api.nutrition.models import *

import unicodecsv as csv
import xlwt
import xlsxwriter
import cStringIO as StringIO
import datetime
from django.contrib.admin import util as admin_util
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse


class ChildAdmin(admin.ModelAdmin):
    list_display = ('id', 'chw', 'mother', 'child_number', 'date_of_birth', 'nation', 'province', 'district', 'health_centre', 'referral_hospital', 'sector', 'cell', 'village')


class BirthAdmin(admin.ModelAdmin):
    list_display = ('id', 'chw', 'mother', 'child_number', 'date_of_birth', 'nation', 'province', 'district', 'health_centre', 'referral_hospital', 'sector', 'cell', 'village')

class ChildNutritionAdmin(admin.ModelAdmin):
    list_display = ('id', 'chw', 'mother', 'child_number', 'date_of_birth', 'nation', 'province', 'district', 'health_centre', 'referral_hospital', 'sector', 'cell', 'village')

class ChildHealthAdmin(admin.ModelAdmin):
    list_display = ('id', 'chw', 'mother', 'child_number', 'date_of_birth', 'nation', 'province', 'district', 'health_centre', 'referral_hospital', 'sector', 'cell', 'village')


admin.site.register(Child, ChildAdmin)
admin.site.register(Birth, BirthAdmin)
admin.site.register(ChildNutrition, ChildNutritionAdmin)
admin.site.register(ChildHealth, ChildHealthAdmin)




