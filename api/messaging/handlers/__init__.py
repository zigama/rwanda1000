#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf import settings


##ENABLED REPORT###
#1.Pregnancy Confirmation Report
#2.ANC Refusal Report
#3.Antenatal Consultation Report
#5.RISK Report
#6.Red Alert Report
#7.Child Health Report
#8.Birth Report
#9.Death Report
#10.Results Report
#11.Red Alert Results Report
#12.Newborn Care Report
#13.Community Based Nutrition Report
#14.Case Management Response Report
#15.Community Case Management Report
#16.Postnatal Care Report

def get_used_reports():
    from rapidsmsrw1000.apps.api.messaging.models import SMSReport
    sms_reports = SMSReport.objects.all().exclude(in_use = False)
    reps = 'HELP'
    i = 0
    while i < sms_reports.count():
        reps += "|%s" % sms_reports[i].keyword
        i += 1

    return reps 

settings.DEFAULT_LANGUAGE_ISO = 'rw'
settings.DEFINED_REPORTS = get_used_reports()


        
