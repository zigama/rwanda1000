#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


##DJANGO LIBRARY
from django.utils.translation import activate, get_language
from django.utils.translation import ugettext as _
from django.conf import settings


###DEVELOPED APPS
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from rapidsmsrw1000.apps.api.messaging.utils import *
from rapidsmsrw1000.apps.chws.models import *

DEFAULT_LANGUAGE_ISO = settings.DEFAULT_LANGUAGE_ISO

class SMSReportHandler (KeywordHandler):
    """
    PREGNANCY REGISTRATION
    """

    keyword = settings.DEFINED_REPORTS
    
    def filter(self):
        """ CHECK IF WE HAVE A CONNECTION FOR THE SENDER """
        if not getattr(msg, 'connection', None):
            self.respond(get_appropriate_response( DEFAULT_LANGUAGE_ISO = 'rw', message_type = 'sender_not_registered', destination = None,
                                                     sms_report = None, sms_report_field = None ))
            return True 
    def help(self):
        try:
            chw = Reporter.objects.get(telephone_moh = self.msg.connection.identity, deactivated = False)
            self.reporter = chw
            self.keyword = self.msg.text.split()[0]
            sms_report = SMSReport.objects.get(keyword = self.keyword)
            self.respond(get_appropriate_response( DEFAULT_LANGUAGE_ISO = self.reporter.language, message_type = 'help', destination = None,
                                                     sms_report = sms_report, sms_report_field = None ))
        except Exception, e:
            self.respond(get_appropriate_response( DEFAULT_LANGUAGE_ISO = 'rw', message_type = 'unknown_error', destination = None,
                                                     sms_report = None, sms_report_field = None ))

    def handle(self, text):
        try:
            chw = Reporter.objects.get(telephone_moh = self.msg.connection.identity, deactivated = False)
            self.reporter = chw
            self.keyword = self.msg.text.replace(text, '').strip()
            return self.yemeze(self.msg)
        except Exception, e:
            self.respond(get_appropriate_response( DEFAULT_LANGUAGE_ISO = 'rw', message_type = 'sender_not_registered', destination = None,
                                                     sms_report = None, sms_report_field = None ))

    def yemeze(self, message):
        try:
            sms_report = SMSReport.objects.get(keyword = self.keyword)
            text = message.text
            p = get_sms_report_parts(sms_report, text, DEFAULT_LANGUAGE_ISO = self.reporter.language)
            pp = putme_in_sms_reports(sms_report, p, DEFAULT_LANGUAGE_ISO = self.reporter.language)
            cs = check_sms_report_semantics( sms_report, pp , DEFAULT_LANGUAGE_ISO = self.reporter.language)
            
            if cs['error'] != '':
                self.respond(cs['error'])
            
            else:
                self.respond(get_appropriate_response( DEFAULT_LANGUAGE_ISO = self.reporter.language, message_type = 'success', destination = None,
                                                     sms_report = sms_report, sms_report_field = None ))
        except Exception, e:
            self.respond(get_appropriate_response( DEFAULT_LANGUAGE_ISO = self.reporter.language, message_type = 'unknown_error', destination = None,
                                                     sms_report = None, sms_report_field = None ))    
        return True

