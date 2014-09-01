#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from .models import *
from xlrd import open_workbook ,cellname,XL_CELL_NUMBER,XLRDError

def get_appropriate_response( DEFAULT_LANGUAGE_ISO = 'rw', message_type = 'unknown_error', sms_report = None, sms_report_field = None, destination = None ):
    try:
        colm = 'message_%s' % DEFAULT_LANGUAGE_ISO
        msg = SMSMessage.objects.get(message_type = message_type, sms_report = sms_report, sms_report_field = sms_report_field)
        return getattr(msg, colm)
    except Exception, e:
        try:
            msg = SMSMessage.objects.get(message_type = message_type, sms_report = sms_report, sms_report_field = sms_report_field)
            return msg.get_message_type_display()
        except Exception, e:
            return get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO )
    

def get_sms_report_parts(sms_report = None , text = None, DEFAULT_LANGUAGE_ISO = 'rw'):
    """
        You need to return appropriate sms, per appropriate position
    """
    sms_parts = [] ## Store parts of appropriate SMS
    try:
        p = text.split(sms_report.field_separator)### use defined SMS separator to split our sms into parts
        ans = []###store parts that has data
        i = 0 ## i position in parts
        while i < len(p):
            an = p[i]
            if an:
                ans.append(an)
            i += 1
        ### Push all our parts into correct position based on the SMSReport of the Database
        sms_parts = ans
    except Exception, e:
        return e
        
    return sms_parts

def putme_in_sms_reports(sms_report = None, sms_parts = None, DEFAULT_LANGUAGE_ISO = 'rw'):
    positioned_sms = []
    i = 0
    fields = SMSReportField.objects.filter(sms_report = sms_report)
    ##DO I exists as a key the SMSReport?? Then push me to the right position, else leave me where the CHW choose to report me
    while i < len(sms_parts):
        val = sms_parts[i]
        found = False
        try:
            for fp in fields:
                #print val, fp
                ### get in field the ones with key 
                if val == fp.key or val.lower() == fp.key :
                    #print val, fp, i, fp.position_after_sms_keyword
                    positioned_sms = get_my_position(sms_report, positioned_sms, fp, val)
                    #print positioned_sms
                    found = True
                    break
                ### get field with prefix based on data
                elif fp.prefix:
                    if val.__contains__(fp.prefix) or val.__contains__(fp.prefix.upper()):
                        #print val, fp, i, fp.position_after_sms_keyword
                        positioned_sms = get_my_position(sms_report, positioned_sms, fp, val)
                        #print positioned_sms
                        found = True                        
                        break
           
            ### if not found get field at the position then
            if found == False:
                sf = SMSReportField.objects.filter(sms_report = sms_report, position_after_sms_keyword = i)
                key = ''
                if sf.count() > 1:
                    key = val
                elif sf.count() == 1:
                    key = sf[0].key#; print sf
                positioned_sms.append({'position': i, 'value': val, 'key': key })            
                
        except Exception, e:
            print e, val
        i += 1 
    return positioned_sms
        

def get_my_position(sms_report, positioned_sms, fp, val, DEFAULT_LANGUAGE_ISO = 'rw'):
    found = False
    if len(positioned_sms) > 0:         
        for ps in positioned_sms:
            if ps['position'] == int(fp.position_after_sms_keyword):
                new_val = '%s%s%s' % ( ps['value'], sms_report.field_separator, val)
                key_val = ps['key']
                if fp.key in key_val.split(sms_report.field_separator): pass
                else:   key_val = '%s%s%s' % ( ps['key'], sms_report.field_separator, fp.key )
                positioned_sms[positioned_sms.index(ps)] = {'position': int(fp.position_after_sms_keyword), 'value': new_val, 'key': key_val}
                found = True
                break
            else:
                continue
        if found == False  :
            positioned_sms.append({'position': int(fp.position_after_sms_keyword), 'value': val, 'key': fp.key })
    else  :
        positioned_sms.append({'position': int(fp.position_after_sms_keyword), 'value': val, 'key': fp.key })

    return positioned_sms

#from rapidsmsrw1000.apps.api.messaging.utils import *
#sms = SMSReport.objects.get(pk = 1)
#text = 'PRE            1198270072829064                 25.08.2013           11.11.2013        03 02        NR GS YG NP MA DI CL HP WT64.0 HT115 TO NT NH HW 0788660270'
#p = get_sms_report_parts(sms, text)
#pp = putme_in_sms_reports(sms, p)
#check_sms_report_semantics( sms, pp )


def check_sms_report_semantics( sms_report, positioned_sms , DEFAULT_LANGUAGE_ISO = 'rw'):
    report = { 'error': '' }
    for ps in positioned_sms:
        try:
            pos = ps['position']
            value = ps['value']
            key = ps['key']
            got = key.split(sms_report.field_separator)
            if pos == 0:    continue
            #print value, key
            if len(got) > 1:
                for value in got:
                    field = SMSReportField.objects.filter(sms_report = sms_report, position_after_sms_keyword = pos, key = value)
                    if field.exists():
                        report.update({'%s' % value: validate_field(sms_report, field[0], value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)})
                    else:
                        report['error'] += ', %s(%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = None,
                                                               message_type = 'unknown_field_code', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value)
            else:
                if len(value.split(sms_report.field_separator)) > 1:
                    for value in value.split(sms_report.field_separator):
                        if value.lower()  != key.lower():
                            report['error'] += ', %s(%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = None,
                                                               message_type = 'unknown_field_code', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value)
                        else:
                            field = SMSReportField.objects.get(sms_report = sms_report, position_after_sms_keyword = pos, key = key)
                            report.update({'%s' % key: validate_field(sms_report, field, value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)})
                else:
                    if key:                        
                        field = SMSReportField.objects.get(sms_report = sms_report, position_after_sms_keyword = pos, key = key)
                        report.update({'%s' % key: validate_field(sms_report, field, value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)})
                    else:
                        report['error'] += ', %s(%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = None,
                                                               message_type = 'unknown_field_code', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value)
        except Exception, e:
            #print e, DEFAULT_LANGUAGE_ISO
            report['error'] += '%s, ' % e.message

    ## Check for dependencies
    parse_dependencies(sms_report, report, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
    ## Check for one allowed 
    parse_only_one(sms_report, report, DEFAULT_LANGUAGE_ISO  = DEFAULT_LANGUAGE_ISO)
    ## Check for required and not there
    parse_missing(sms_report, report, DEFAULT_LANGUAGE_ISO  = DEFAULT_LANGUAGE_ISO)
        
    return report

def validate_field(sms_report, field, value, DEFAULT_LANGUAGE_ISO ):
    #integer
    #float
    #date
    #string
    #string_digit
 
    if field.prefix:
        if value.__contains__(field.prefix): value = value.replace(field.prefix, '')
        else:   value = value.replace(field.prefix.upper(), '')

    if field.type_of_value == 'string_digit':
        value = parse_length(sms_report, field, value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)

    elif field.type_of_value == 'string':
        value = parse_length(sms_report, field, value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)

    elif field.type_of_value == 'date':
        value = parse_date(sms_report, field, value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)

    elif field.type_of_value == 'integer':
        try:
            value = parse_value(sms_report, field, int(value), DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
        except Exception, e:
            raise Exception( ' %s (%s)' % (get_appropriate_response( sms_report = sms_report, sms_report_field = field,
                                             message_type = 'only_integer', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value ) )

    elif field.type_of_value == 'float':
        try:
            value = parse_value(sms_report, field, float(value), DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
        except Exception, e:
            raise Exception( ' %s (%s)' % (get_appropriate_response( sms_report = sms_report, sms_report_field = field,
                                             message_type = 'only_float', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value ) )

    return value
        
def parse_length(sms_report, field, value, DEFAULT_LANGUAGE_ISO ):
    if field.minimum_length <= len(value.strip()) <= field.maximum_length:
        return value.strip()
    else:
        response = SMSMessage.objects.filter(sms_report = sms_report, sms_report_field = field, message_type = 'not_in_range')
        if response.exists():
            raise Exception( getattr(response[0], 'message_%s' % DEFAULT_LANGUAGE_ISO) )
        else:
            raise Exception( ' %s (%s)' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value ) )

def parse_value(sms_report, field, value, DEFAULT_LANGUAGE_ISO ):
    if field.minimum_value <= value <= field.maximum_value:
        return value
    else:
        response = SMSMessage.objects.filter(sms_report = sms_report, sms_report_field = field, message_type = 'not_in_range')
        if response.exists():
            raise Exception( getattr(response[0], 'message_%s' % DEFAULT_LANGUAGE_ISO) )
        else:
            raise Exception( ' %s (%s)' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value ) )

def parse_date(sms_report, field, value, DEFAULT_LANGUAGE_ISO):

    m3 = re.search("^(\d+)\.(\d+)\.(\d+)$", value) 
    if m3:
        dd = int(m3.group(1))
        mm = int(m3.group(2))
        yyyy = int(m3.group(3))

        d = datetime.date( yyyy, mm, dd )

        if datetime.date.today() + datetime.timedelta(days = field.minimum_value) <= d <= datetime.date.today() + datetime.timedelta(days = field.maximum_value):
            return d
        else:
            response = SMSMessage.objects.filter(sms_report = sms_report, sms_report_field = field, message_type = 'not_in_range')
            if response.exists():
                raise Exception( getattr(response[0], 'message_%s' % DEFAULT_LANGUAGE_ISO) )
            else:
                raise Exception( ' %s (%s)' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value ) )
        
    else:
        response = SMSMessage.objects.filter(sms_report = sms_report, sms_report_field = field, message_type = 'only_date')
        if response.exists():
            raise Exception( getattr(response[0], 'message_%s' % DEFAULT_LANGUAGE_ISO) )
        else:
            raise Exception( ' %s (%s)' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value ) )

def parse_dependencies(sms_report, report, DEFAULT_LANGUAGE_ISO ):

    for r in report.keys():
        field = SMSReportField.objects.filter(sms_report = sms_report, key = r)
        if field.exists():
            field = field[0]
            if field.depends_on_value_of:
                dep  = None
                try:    dep = report[field.depends_on_value_of.key]
                except: continue
                if field.dependency == 'greater':
                    if report[r] > dep:
                        continue
                    else:
                        report['error'] += ', %s' % get_error_msg(sms_report = sms_report, sms_report_field = field, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
                elif field.dependency == 'greater_or_equal':
                    if report[r] >= dep:
                        continue
                    else:
                        report['error'] += ', %s' % get_error_msg(sms_report = sms_report, sms_report_field = field, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
                elif field.dependency == 'equal':
                    if report[r] == dep:
                        continue
                    else:
                        report['error'] += ', %s' % get_error_msg(sms_report = sms_report, sms_report_field = field, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)

                elif field.dependency == 'different':
                    if report[r] != dep:
                        continue
                    else:
                        report['error'] += ', %s' % get_error_msg(sms_report = sms_report, sms_report_field = field, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
                elif field.dependency == 'less':
                    if report[r] < dep:
                        continue
                    else:
                        report['error'] += ', %s' % get_error_msg(sms_report = sms_report, sms_report_field = field, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
                elif field.dependency == 'less_or_equal':
                    if report[r] <= dep:
                        continue
                    else:
                        report['error'] += ', %s' % get_error_msg(sms_report = sms_report, sms_report_field = field, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)
                elif field.dependency == 'jam':                    
                    if dep:
                        jam = SMSReportField.objects.filter(sms_report = sms_report, key = dep)[0]
                        report['error'] += ', %s (%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = jam, 
                                                                    message_type = 'dependency_error', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), field.key)
                    else:
                        continue
                else:
                    pass
            else:
                continue

    return True

def parse_only_one(sms_report, report, DEFAULT_LANGUAGE_ISO ):
    seens = {}    
    for r in report.keys():
        field = SMSReportField.objects.filter(sms_report = sms_report, only_allow_one = True, key = r )
        if field.exists():
            for f in field:
                if f.position_after_sms_keyword in seens.keys():
                    seens[f.position_after_sms_keyword] += ' %s' % r
                    report['error'] += ' %s (%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = None, 
                                                   message_type = 'one_value_of_list', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), seens[f.position_after_sms_keyword])
                    
                else:
                    seens[f.position_after_sms_keyword] = ' %s' % r
                    continue
    #print "THERE : %s" % DEFAULT_LANGUAGE_ISO
    return True


def parse_missing(sms_report, report, DEFAULT_LANGUAGE_ISO ):
    field = SMSReportField.objects.filter(sms_report = sms_report, required = True)
    gots = SMSReportField.objects.filter(sms_report = sms_report, key__in = report.keys())
    for f in field:
        if f.key in report.keys():
            continue            
        else:
            if f.dependency == 'jam' and f.depends_on_value_of.key in report.keys():   continue
            elif gots.filter( position_after_sms_keyword = f.position_after_sms_keyword ).exists():   continue
            else: 
                report['error'] += '%s (%s), -' % (get_error_msg(sms_report = sms_report, sms_report_field = None, 
                                           message_type = 'missing_sms_report_field', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), f.key)
            
    return True
    

    

def get_error_msg(sms_report , sms_report_field , DEFAULT_LANGUAGE_ISO , message_type = 'unknown_error'):
    response = SMSMessage.objects.filter(sms_report = sms_report, sms_report_field = sms_report_field, message_type = message_type)
    if response.exists():
        return getattr(response[0], 'message_%s' % DEFAULT_LANGUAGE_ISO)
    else:
        if sms_report_field:    return ' %s (%s)' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), sms_report_field.key)
        return ' %s' % get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)

def locate_object(object_inst, ref):
    for l in LocationType.objects.all():
        setattr(    object_inst, 
                    camel_to_underscore_lower(l.name), 
                    getattr(ref, camel_to_underscore_lower(l.name))
                )
    return object_inst
    


def import_sms_report(filepath = "rapidsmsrw1000/apps/api/messaging/smsreport.xls", sheetname = "smsreport"):
    book = open_workbook(filepath)
    sheet = book.sheet_by_name(sheetname)
    
    for row_index in range(sheet.nrows):
        if row_index < 1: continue   
        try:
            title               = sheet.cell(row_index,0).value
            keyword             = sheet.cell(row_index,1).value
            description         = sheet.cell(row_index,2).value
            field_separator     = sheet.cell(row_index,3).value
            in_use              = sheet.cell(row_index,4).value
            case_sensitive      = sheet.cell(row_index,5).value
            syntax_regex        = sheet.cell(row_index,6).value
            #created             = sheet.cell(row_index,7).value 

            #print title, keyword, description, field_separator, in_use , case_sensitive, syntax_regex, created
            sms_report, created = SMSReport.objects.get_or_create(keyword = keyword)

            sms_report.title = title
            sms_report.description = description
            sms_report.field_separator = field_separator
            sms_report.in_use = in_use
            sms_report.case_sensitive = case_sensitive
            sms_report.syntax_regex = syntax_regex
            #sms_report.created = created
                        
            sms_report.save()                   
            
            print "\ntitle : %s\n keyword : %s\n description : %s\n field_separator : %s\n in_use : %s\n case_sensitive: %s\n syntax_regex : %s\n \
                    created: %s \n" % (sms_report.title, sms_report.keyword, sms_report.description, sms_report.field_separator, sms_report.in_use, 
                        sms_report.case_sensitive, sms_report.syntax_regex, sms_report.created)
            
        except Exception, e:
            print e, row_index
            pass

def import_sms_report_field(filepath = "rapidsmsrw1000/apps/api/messaging/smsreportfield.xls", sheetname = "smsreportfield"):
    book = open_workbook(filepath)
    sheet = book.sheet_by_name(sheetname)
    
    for row_index in range(sheet.nrows):
        if row_index < 1: continue   
        try:
            sms_report_keyword          = sheet.cell(row_index, 0).value 
            prefix                      = sheet.cell(row_index, 1).value
            key                         = sheet.cell(row_index, 2).value 
            description                 = sheet.cell(row_index, 3).value 
            type_of_value               = sheet.cell(row_index, 4).value 
            upper_case                  = sheet.cell(row_index, 5).value 
            lower_case                  = sheet.cell(row_index, 6).value 
            try:    minimum_value               = int( sheet.cell(row_index, 7).value )
            except Exception, e: minimum_value = None
            try:    maximum_value               = int( sheet.cell(row_index, 8).value )
            except Exception, e: maximum_value = None
            try:    minimum_length              = int( sheet.cell(row_index, 9).value )
            except Exception, e: minimum_length = None
            try:    maximum_length              = int( sheet.cell(row_index, 10).value )
            except Exception, e: maximum_length = None 
            try:    position_after_sms_keyword  = int( sheet.cell(row_index, 11).value )
            except Exception, e: position_after_sms_keyword = None 
            depends_on_value_of         = sheet.cell(row_index, 12).value 
            dependency                  = sheet.cell(row_index, 13).value 
            allowed_value_list          = sheet.cell(row_index, 14).value 
            only_allow_one              = sheet.cell(row_index, 15).value 
            required                    = sheet.cell(row_index, 16).value 
            
            #print sms_report_keyword, prefix, key, description, type_of_value, upper_case, lower_case, minimum_value, maximum_value,\
            #        minimum_length, maximum_length, position_after_sms_keyword, depends_on_value_of, dependency, allowed_value_list, only_allow_one, required
            
            sms_report                                   = SMSReport.objects.get(keyword = sms_report_keyword)
            try:    dep                                  = SMSReportField.objects.get(key = depends_on_value_of)
            except Exception, e:    dep                  = None
            sms_report_field, created                    = SMSReportField.objects.get_or_create(key = key, sms_report = sms_report, 
                                                                                                    position_after_sms_keyword = position_after_sms_keyword)
            sms_report_field.prefix                      = prefix
            sms_report_field.description                 = description
            sms_report_field.type_of_value               = type_of_value
            sms_report_field.upper_case                  = upper_case
            sms_report_field.lower_case                  = lower_case
            sms_report_field.minimum_value               = minimum_value
            sms_report_field.maximum_value               = maximum_value
            sms_report_field.minimum_length              = minimum_length
            sms_report_field.maximum_length              = maximum_length
            sms_report_field.depends_on_value_of         = dep
            sms_report_field.dependency                  = dependency
            sms_report_field.allowed_value_list          = allowed_value_list
            sms_report_field.only_allow_one              = only_allow_one
            sms_report_field.required                    = required
            print sms_report_field, minimum_value, maximum_value, minimum_length, maximum_length, position_after_sms_keyword
            sms_report_field.save()                   
            
            print   sms_report_field.sms_report                  ,\
                    sms_report_field.prefix                      ,\
                    sms_report_field.key                         ,\
                    sms_report_field.description                 ,\
                    sms_report_field.type_of_value               ,\
                    sms_report_field.upper_case                  ,\
                    sms_report_field.lower_case                  ,\
                    sms_report_field.minimum_value               ,\
                    sms_report_field.maximum_value               ,\
                    sms_report_field.minimum_length              ,\
                    sms_report_field.maximum_length              ,\
                    sms_report_field.position_after_sms_keyword  ,\
                    sms_report_field.depends_on_value_of         ,\
                    sms_report_field.dependency                  ,\
                    sms_report_field.allowed_value_list          ,\
                    sms_report_field.only_allow_one              ,\
                    sms_report_field.required                    

            
        except Exception, e:
            print e, row_index
            pass

    
