#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from django.core.exceptions import ObjectDoesNotExist
import re

from rapidsms.contrib.handlers.handlers.base import BaseHandler


from rapidsmsrw1000.apps.api.messaging.utils import get_appropriate_response, SMSReport
from rapidsmsrw1000.apps.chws.models import Reporter

#### YOU CAN STILL USE RAPIDSMS DEFINED KeywordHandler, INSTEAD 
#### ZIGAMA DIDIER chose to overwrite this in order to make sure RWANDA CHW receive proper responses

class SMSReportKeywordHandler(BaseHandler):

    @classmethod
    def _keyword(cls):
        if hasattr(cls, "keyword"):
            prefix = r"^\s*(?:%s)(?:[\s,;:]+(.+))?$" % (cls.keyword)
            return re.compile(prefix, re.IGNORECASE)

    @classmethod
    def dispatch(cls, router, msg):

        # spawn an instance of this handler, and stash
        # the low(er)-level router and message object
        inst = cls(router, msg)

        ### GET REPORTER
        try:
            cls.reporter = Reporter.objects.get(telephone_moh = msg.connection.identity, deactivated = False)
        except Exception, e:
            msg.respond( get_appropriate_response( DEFAULT_LANGUAGE_ISO = 'rw', message_type = 'sender_not_registered', destination = None,
                                                     sms_report = None, sms_report_field = None ) 
                         )
            return True
        
        if cls.reporter is None:
            msg.respond( get_appropriate_response( DEFAULT_LANGUAGE_ISO = "rw", message_type = 'sender_not_registered', destination = None,
                                                     sms_report = None, sms_report_field = None ) 
                            )
            return True

        keyword = cls._keyword()
        if keyword is None:
            msg.respond( get_appropriate_response( DEFAULT_LANGUAGE_ISO = cls.reporter.language, message_type = 'unknown_keyword', destination = None,
                                                         sms_report = None, sms_report_field = None ) 
                            )
            return True
            
        try:
                cls.sms_report = SMSReport.objects.filter(keyword = msg.text.split()[0])[0]
                cls.sms_report_keyword = cls.sms_report.keyword
        except Exception, e:
            #print e
            msg.respond( get_appropriate_response( DEFAULT_LANGUAGE_ISO = cls.reporter.language, message_type = 'unknown_keyword', destination = None,
                                                     sms_report = None, sms_report_field = None ) 
                        )
            return True

        match = keyword.match(msg.text)
        if match is None:   
            msg.respond( '%s, %s' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = cls.reporter.language, message_type = 'empty_sms_report', destination = None,
                                                     sms_report = None, sms_report_field = None ),
                                    get_appropriate_response( DEFAULT_LANGUAGE_ISO = cls.reporter.language, message_type = 'help', destination = None,
                                                     sms_report = cls.sms_report, sms_report_field = None )) 
                            )
            return True

        # if any non-whitespace content was send after the keyword, send
        # it along to the handle method. the instance can always find
        # the original text via self.msg if it really needs it.
        
        text = match.group(1)
        

        if text is None or text.strip() == '':
           msg.respond( '%s, %s' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = cls.reporter.language, message_type = 'empty_sms_report', destination = None,
                                                     sms_report = None, sms_report_field = None ),
                                    get_appropriate_response( DEFAULT_LANGUAGE_ISO = cls.reporter.language, message_type = 'help', destination = None,
                                                     sms_report = cls.sms_report, sms_report_field = None )) 
                            )
           return True
                
        if text is not None:
            try:
                inst.handle(text)

            # special case: if an object was expected but not found,
            # return the (rather appropriate) "%s matching query does
            # not exist." message. this can, of course, be overridden by
            # catching the exception within the ``handle`` method.
            except ObjectDoesNotExist, err:
                return inst.respond_error(
                    unicode(err))

            # another special case: if something was miscast to an int
            # (it was probably a string from the ``text``), return a
            # more friendly (and internationalizable) error.
            except ValueError, err:
                p = r"^invalid literal for int\(\) with base (\d+?): '(.+?)'$"
                m = re.match(p, unicode(err))

                # allow other valueerrors to propagate.
                if m is None:
                    raise

                return inst.respond_error(
                    "Not a valid number: %(string)s",
                    string=m.group(2))

        # if we received _just_ the keyword, with
        # no content, some help should be sent back
        else:
            inst.help()

        return True

