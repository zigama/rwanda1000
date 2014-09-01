#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from rapidsmsrw1000.apps.api.utils import *
from django.contrib.auth.models import Group

##Start of SMSReport
class SMSReport(models.Model):

    """
        This guide you building your own SMS Report ... the syntax of an SMS please, 
        don't think about other constraints your are not even able to figure out before you go into the DB  

    """
    SEPARATOR_CHOICES = (
        (' ','WhiteSpace ( )'),
        (',','Comma (,)'),
        (';','Semicolon (;)'),
        (':','Colon (:)'),
        ('*','Asterisk (*)'),
    )


    ### This has to be recognized in the language supported
    title = models.CharField(max_length=50,
                            help_text="Name your SMS Report.")
    keyword = models.CharField(max_length=30, unique=True)

    description =  models.TextField(max_length=255,
                               help_text="Why do we need this SMS Report?")

    field_separator = models.CharField(max_length=1, choices=SEPARATOR_CHOICES, null=True, blank=True,
                                 help_text="What is the separator of your SMS Report Fields?")

    case_sensitive = models.BooleanField(default=False,
                                 help_text="Do we need our SMS Report to react on either Upper or Lower Case?")

    in_use = models.BooleanField(default=True,
                                 help_text="Do we still use this SMS Report?")
    
    syntax_regex = models.TextField(blank = True, null = True,
                                help_text="For Developer ... Don't show on ADMIN SITE")
    
    """

    ### This has to be recognized in the language supported, language tables
    success_response = models.TextField(blank = True, null = True,
                                help_text="You need to define a SMS to be sent to acknowledge the message has been received successfully.")

    
    ### This has to be recognized in the language supported, language tables
    failure_response = models.TextField(blank = True, null = True,
                                help_text="You need to define a SMS to be sent to acknowledge the message has been received with errors.")

    ### This has to be recognized in the language supported, language tables
    failure_reason = models.TextField(blank = True, null = True,
                                help_text="You need to define a SMS to be sent to show the reason of failure.")
    
    """
    
    created = models.DateTimeField(auto_now_add=True)
    
    
    def __unicode__(self):
        return "%s" % self.title


##End of SMSReport

##Start of SMSReportField
class SMSReportField(models.Model):


    VALUE_TYPE_CHOICES = (

        ('integer','Integer'),
        ('float','Float'),
        ('date','Date'),
        ('string','String'),
        ('string_digit','String Digit'),
    )

    DEPEDENCY_CHOICES = (
                            ('greater', 'Greater than'),
                            ('greater_or_equal', 'Greater than or Equal'),
                            ('equal', 'Equal'),
                            ('different', 'Different'),
                            ('less', 'Less than'),
                            ('less_or_equal', 'Less than or Equal'),
                            ('jam', 'Jam'),
                         )
    
    sms_report = models.ForeignKey(SMSReport)
    
    prefix = models.CharField(max_length=5, null=True, blank=True,
                                      help_text="Do You prefix this field? E.G: WT50.8")
    key = models.CharField(max_length=30, null=True, blank=True,
                                      help_text="What is the unique key for this Field")
    description = models.TextField(max_length=255,
                               help_text="Why do we need this SMS Report Field?")
    type_of_value =  models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES, null=True, blank=True,
                                 help_text="The type of value the field will have.")
    
    upper_case = models.BooleanField(default=False,
                                 help_text="This SMS Report Field must be Upper Case.")
    lower_case = models.BooleanField(default=False,
                                 help_text="This SMS Report Field must be Lower Case.")
    
    minimum_value = models.FloatField(blank = True, null=True, 
                                      help_text="What is the minimum value for this SMS Report Field?")
    maximum_value = models.FloatField(blank = True, null=True, 
                                      help_text="What is the maximum value for this SMS Report Field?")
    
    minimum_length = models.FloatField(blank = True, null=True, 
                                      help_text="What is the minimum length for this SMS Report Field?")
    maximum_length = models.FloatField(blank = True, null=True, 
                                      help_text="What is the maximum length for this SMS Report Field?")
    
    position_after_sms_keyword = models.PositiveSmallIntegerField(validators = [MinValueValidator(1)])
    depends_on_value_of = models.ForeignKey("SMSReportField", null=True, blank=True, 
                                            related_name="dependent", help_text = "Does this SMS Report Field depend on another?")
    
    dependency = models.CharField(max_length=30, choices=DEPEDENCY_CHOICES, null=True, blank=True,
                                 help_text="How does this SMS Report Field depend on that?")
    
    allowed_value_list = models.TextField(max_length=255, null=True, blank=True,
                               help_text="Does this SMS Report Field have a list of values only allowed? Separate them with semi-colon (;)")
    only_allow_one =  models.BooleanField(default=False,
                                 help_text="Do we only allow one value of the above list for this SMS Report Field?")
    
    required =  models.BooleanField(default=True,
                                 help_text="Is this SMS Report Field mandatory?")
    
    created = models.DateTimeField(auto_now_add=True)
    
    unique_together = (("sms_report", "key", "position_after_sms_keyword"))
    
    def __unicode__(self):
        return "%s-%s" % (self.sms_report, self.description)
    
##End of SMSReportField
    
##Start of SMSLanguage
class SMSLanguage(models.Model):
    
    name = models.CharField(max_length=30, unique = True,
                                 help_text="Language Name or Title")
    
    iso_639_1_code = models.CharField(max_length = 5, unique = True,
                                 help_text="Language Code based on ISO 639-1")
    
    description = models.TextField(max_length=255, null=True, blank=True,
                               help_text="Description of the language")

    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s(%s)" % (self.name, self.iso_639_1_code)    
    
    
##End of SMSLanguage
    
##Start of SMSMessage
class SMSMessage(models.Model):

    """
        This Table Contains Error Code and Message thrown out by supported language, whoever need to customize
        This Messaging Api needs to define appropriate message per error code, where error code can only implemented by skilled developer
    
    """
    
    CODE_CHOICES = (
                            ('reminder', 'Reminder'),
                            ('notification', 'Notification'),
                            ('success', 'The SMS Report Has Been Submitted Successfully'),
                            ('unknown_keyword', 'Unknown Keyword'),
                            ('empty_sms_report', 'Empty SMS Report'),
                            ('missing_sms_report_field', 'Missing SMS Report Field'),
                            ('sequence_or_order', 'Sequence or Order Not Correct'),
                            ('unsupported_smsreport_fcode', 'Not Supported SMS Report Field Code'),
                            ('unsupported_prefix', 'Not Supported SMS Report Field Prefix'),
                            ('unknown_field_code', 'Unknown Field Code'),
                            ('only_integer', 'Only Integer Number Supported'),
                            ('only_float', 'Only Decimal Number Supported'),
                            ('only_date', 'Only Date Supported'),
                            ('only_string', 'Only String Supported'),
                            ('only_string_digit', 'Only String of Digit Supported'),
                            ('only_upper_case', 'Only Upper Case Supported'),
                            ('only_lower_case', 'Only Lower Case Supported'),
                            ('not_in_range', 'Length or Value is either Greater or Less Than Allowed'),
                            ('dependency_error', 'Dependency Error'),
                            ('not_in_allowed_values', 'Not In Allowed Values'),
                            ('one_value_of_list', 'Only One Value Is Allowed From The List'),
                            ('is_required', 'This SMS Report Field Is Mandatory'),
                            ('sender_not_registered', 'Sender Not Registered'),
                            ('unknown_error', 'Unknown Error'),
                            ('help', 'Help Text'),                            
                            
                          )
    
    message_type = models.CharField(max_length=100, choices = CODE_CHOICES,
                                      help_text="Feedback Message Code")
    sms_report =  models.ForeignKey(SMSReport, blank = True, null = True)
    sms_report_field = models.ForeignKey(SMSReportField, blank = True, null = True)
    destination = models.ForeignKey(Group, blank = True, null = True)
    description = models.TextField(null = True, blank = True, help_text = 'Why This SMS, Have you check none is similar?')
    #Reminder to user_group, of patient, base on sms report table, time column , after  x seconds, y minutes, z hour , m days, n months, p year
    
    ##START OF LANGUAGES
    
    message_en = models.TextField(max_length=255, null=True, blank=True, help_text="Message in English")
    message_rw = models.TextField(max_length=255, null=True, blank=True, help_text="Message in Kinyarwanda")

    message_fr = models.TextField(null = True, blank = True, help_text = 'Message in Francais ')

    message_ch = models.TextField(null = True, blank = True, help_text = 'Message in Chinese ')
    
    ##END OF LANGUAGES
    
    created = models.DateTimeField(auto_now_add=True)

    unique_together = (("message_type", "sms_report", "sms_report_field")) 
    
    def __unicode__(self):
        return "%s-%s" % (self.get_message_type_display(), self.description)   
    
##End of SMSMessage

##Start of SMSReportTrack

##End of SMSReportTrack


def ensure_new_language(sender, **kwargs):
    if kwargs.get('created', False):
        language = kwargs.get('instance')
        #print language
        field_name = 'message_%s' % language.iso_639_1_code
        marker = "LANGUAGES"
        help_text = "Message in %s " % language.name
        model_object = get_model_object(language._meta.app_label, "SMSMessage" )
        filename = '%s/%s/models.py' % (API_PATH, model_object._meta.app_label)
        lang_c = add_column_textfield_to_table(filename, model_object, field_name,  marker, help_text)
        if lang_c:    return True
        else:   return False
    
 
post_save.connect(ensure_new_language, sender = SMSLanguage)    
    



