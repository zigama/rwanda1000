#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from rapidsmsrw1000.apps.api.rhea.models import *

import unicodecsv as csv
import xlwt
import datetime
from django.contrib.admin import util as admin_util
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse


import unicodecsv as csv
import xlwt
import datetime
from django.contrib.admin import util as admin_util
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

def export_model_as_excel(modeladmin, request, queryset):
    has_name_fields = ['village', 'cell', 'sector', 'health_centre', 'referral_hospital', 'district', 'province','role']
    is_date_fields = ['date_of_birth', 'dob', 'join_date']
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
                elif field in is_date_fields: sheet.write(row, col, "%d/%d/%d" % (value.day, value.month, value.year))
                else:   sheet.write(row, col, value)
            except Exception, e:
                try:    sheet.write(row, col, value)
                except: sheet.write(row, col, "NULL")
            col = col + 1
        row = row + 1

    workbook.save(response)
    return response

export_model_as_excel.short_description = _('Export to EXCEL')



class ConceptAdmin(admin.ModelAdmin):
    actions = (export_model_as_excel, )
    exportable_fields = ('name', 'answer', 'mapping', 'mapping_code', 'data_type', 'value',)
    list_display = ('name', 'answer', 'mapping', 'mapping_code', 'data_type', 'value',)
    pass

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('not_type', 'message', 'report')
    pass

class RheaRequestAdmin(admin.ModelAdmin):
    actions = (export_model_as_excel, )
    exportable_fields = ('request', 'data', 'response', 'status_reason')
    list_display = ('request', 'data', 'notification', 'notif_status', 'response', 'status_reason')
    
    pass

class HIERequestAdmin(admin.ModelAdmin):
    actions = (export_model_as_excel, )
    exportable_fields = ('request', 'data', 'concepts', 'patient_reporter', 'message', 'sent', 'response')
    list_display = ('request', 'data', 'concepts', 'patient_reporter', 'message', 'sent', 'response')
    pass

class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    pass

admin.site.register(HIERequest, HIERequestAdmin)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(RheaRequest, RheaRequestAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationType, NotificationTypeAdmin)




