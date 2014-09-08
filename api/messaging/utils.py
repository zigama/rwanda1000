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
from rapidsmsrw1000.apps.api.utils import get_block_of_text_link, replace_block_of_text_link
from rapidsmsrw1000.apps.api.locations.models import *

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
                            field = SMSReportField.objects.filter(sms_report = sms_report, position_after_sms_keyword = pos, key = key)
                            if field.exists():  report.update({'%s' % key: validate_field(sms_report, field[0], value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)})
                            else:
                                report['error'] += ', %s(%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = None,
                                                                       message_type = 'unknown_field_code', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value)
                else:
                    if key:                        
                        field = SMSReportField.objects.filter(sms_report = sms_report, position_after_sms_keyword = pos, key = key)
                        if field.exists():  report.update({'%s' % key: validate_field(sms_report, field[0], value, DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)})
                        else:
                            report['error'] += ', %s(%s)' % (get_error_msg(sms_report = sms_report, sms_report_field = None,
                                                                   message_type = 'unknown_field_code', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), value)
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
    field = SMSReportField.objects.filter(sms_report = sms_report, required = True).order_by('position_after_sms_keyword')
    gots = SMSReportField.objects.filter(sms_report = sms_report, key__in = report.keys())
    onces = [] 
    for f in field:
        if f.key in report.keys():
            continue            
        else:
            if f.dependency == 'jam' and f.depends_on_value_of.key in report.keys():   continue
            elif gots.filter( position_after_sms_keyword = f.position_after_sms_keyword ).exists():   continue
            elif f.position_after_sms_keyword in onces:   continue
            else:
                title = 'title_%s' %  DEFAULT_LANGUAGE_ISO
                category = 'category_%s' %  DEFAULT_LANGUAGE_ISO 
                report['error'] += '%s (%s), -' % (get_error_msg(sms_report = sms_report, sms_report_field = None, 
                                           message_type = 'missing_sms_report_field', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO), 
                                                getattr(f, category) or  getattr(f, title))
                onces.append(f.position_after_sms_keyword)#;print f.position_after_sms_keyword, onces
    
    return True

def parse_db_constraint(sms_report, report, DEFAULT_LANGUAGE_ISO):
    got = None
    constraints = SMSDBConstraint.objects.filter( sms_report = sms_report )
    if constraints.filter(constraint = 'unique').exists():
        got = SMSReportTrack.objects.filter( nid = report['nid'] )
        if got.exists():
            period_start = constraints.get(constraint = 'unique')['minimum_period_value'] 
            period_end =  constraints.get(constraint = 'unique')['maximum_period_value']
            if period_start and period_end: got = got.filter( created__gte = period_start, created__lte = period_end )
            tolerance = constraints.filter( constraint = 'tolerance' )            
            if got.exists():
                if tolerance.exists():
                    tolerances = got.filter( keyword__in = tolerance.values_list('refer_sms_report__keyword'))
                    if tolerances.exists():
                        got1 = None
                        for t in tolerance:
                            got1 = tolerances.extra(where = ["%s = '%s'" % ( t.refer_sms_report_field.key , t.refer_sms_report_field.key )] )
                            if got1.exists():
                                return True
                else:
                    report['error'] += '%s , ' % (get_error_msg(sms_report = sms_report, sms_report_field = None, 
                                           message_type = 'duplication', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO) )

    if constraints.filter(constraint = 'stopper').exists():
        got = SMSReportTrack.objects.filter( nid = report['nid'] )
        if got.exists():
            stopper = constraints.filter( constraint = 'stopper' )
            if stopper.exists():
                stoppers = got.filter( keyword__in = stopper.values_list('refer_sms_report__keyword'))
                if stoppers.exists():
                    got1 = None
                    for s in stopper:
                        got1 = stoppers.extra(where = ["%s = '%s'" % ( s.refer_sms_report_field.key , s.refer_sms_report_field.key )] )
                        if got1.exists():
                            report['error'] += '%s , ' % (get_error_msg(sms_report = sms_report, sms_report_field = None, 
                                       message_type = 'expired_based_data', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO) )

    if constraints.filter(constraint = 'base').exists():
        got = SMSReportTrack.objects.filter( nid = report['nid'] )
        if got.exists():
            base = constraints.filter( constraint = 'base' )
            if base.exists():
                bases = got.filter( keyword__in = base.values_list('refer_sms_report__keyword'))
                if bases.exists():
                    got1 = None
                    for b in base:
                        got1 = bases.extra(where = ["%s = '%s'" % ( s.refer_sms_report_field.key , s.refer_sms_report_field.key )] )
                        if got1.exists():
                            return True
                        else:
                            report['error'] += '%s , ' % (get_error_msg(sms_report = sms_report, sms_report_field = None, 
                                       message_type = 'missing_based_data', DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO) )
                                
    return True    

def get_error_msg(sms_report , sms_report_field , DEFAULT_LANGUAGE_ISO , message_type = 'unknown_error'): 
    response = SMSMessage.objects.filter(sms_report = sms_report, sms_report_field = sms_report_field, message_type = message_type)
    if response.exists():
        return getattr(response[0], 'message_%s' % DEFAULT_LANGUAGE_ISO)
    else:
        if sms_report_field:
            title = 'title_%s' %  DEFAULT_LANGUAGE_ISO
            category = 'category_%s' %  DEFAULT_LANGUAGE_ISO   
            return ' %s (%s)' % (get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO),
                                     getattr(sms_report_field, category) or  getattr(sms_report_field, title))
        return ' %s' % get_appropriate_response( DEFAULT_LANGUAGE_ISO = DEFAULT_LANGUAGE_ISO)

def locate_object(object_inst, ref):
    for l in LocationType.objects.all():
        setattr(    object_inst, 
                    camel_to_underscore_lower(l.name), 
                    getattr(ref, camel_to_underscore_lower(l.name))
                )
    return object_inst

def distinct_sms_report_fields():
    """ 
        mysql backend does not support distinct
    """
   
    fs_keys = SMSReportField.objects.all().values_list('key').distinct()
    ans = [ SMSReportField.objects.filter(key__in = f)[0].id for f in fs_keys ]
    fs = SMSReportField.objects.filter( pk__in  = ans ) 
    
    return fs.order_by('key')


def get_field_name(f):
    f_key = getattr(f, 'key')
    f_key = "%s_key" % f_key
    return f_key

def get_model_object(app_label, model_name):
    app = get_app(app_label)
    m = get_models(app)
    for m1 in m:
        if m1.__name__ == model_name:
            return m1
    return None

def propagate_db(model_object):

    try:
        
        try: 
            obj = model_object()
            table = obj._meta.db_table
            cursor = connection.cursor()
            cursor.execute("drop table %s" % table)
            cursor.close()
        except Exception, e:
            pass
            
        return_code = subprocess.call("cd %s && ./manage.py syncdb" % os.getcwd(), shell=True)  
    except Exception,e:
        return False
        
    return True
    

def create_or_update_model(app_label = 'messaging', model_name = 'Test', model_fields = [], filters = [], custom = [],
                                         links = [], locations = [], default_return = 'raw_sms'):
    """
        Field in the form of {key, type_of_value, length(min, max), required, value(min,max)} 
        locations are all Location Types already defined        
    """

    try:
        tab = add_four_space()
        status = False
        start_text = "##Start of %s" % model_name
        end_text = "##End of %s" % model_name

        start_fields_text = "##Start of %s Fields" % model_name
        end_fields_text = "##End of %s Fields" % model_name

        start_meta_text = "##Start of %s Meta" % model_name
        end_meta_text = "##End of %s Meta" % model_name

        start_methods_text = "##Start of %s Methods" % model_name
        end_methods_text =  "##End of %s Methods" % model_name
        
        locs_data = "".join("\n%s%s = models.ForeignKey(%s, null = True, blank = True)" % (tab, camel_to_underscore_lower(l), camelCase(l)) for l in locations)
        links_data = "".join("\n%s%s = models.ForeignKey(%s, null = True, blank = True)" % (tab, camel_to_underscore_lower(l), camelCase(l)) for l in links)
        custom_data = "".join("%s" % c['data'] for c in custom)
        ans = []
        for f in model_fields:
            min_lf = getattr(f, 'minimum_length')
            max_lf = getattr(f, 'maximum_length')
            min_vf = getattr(f, 'minimum_value')
            max_vf = getattr(f, 'maximum_value')
            type_of_vf = getattr(f, 'type_of_value')
            required_f = getattr(f, 'required')
            
            if  type_of_vf == 'integer':
                
                vf = "\n%s%s = models.IntegerField(validators = [MinValueValidator(%d), MaxValueValidator(%d)], null = %s,  blank = %s)" % (tab,
                                                                                 get_field_name(f), min_vf, max_vf, required_f, required_f)
                
            elif  type_of_vf == 'float':
                
                vf = "\n%s%s = models.IntegerField(validators = [MinValueValidator(%d), MaxValueValidator(%d)], null = %s,  blank = %s)" % (tab,
                                                                                 get_field_name(f), min_vf, max_vf, required_f, required_f)
                
            elif type_of_vf == 'string':
                
                vf = "\n%s%s = models.CharField(max_length = %d , validators = [MinLengthValidator(%d)], null = %s,  blank = %s)" % (tab, 
                                                    get_field_name(f), max_lf, min_lf, required_f, required_f)
                
            elif type_of_vf == 'string_digit':
                
                vf = "\n%s%s = models.CharField(max_length = %d , validators = [MinLengthValidator(%d)], null = %s,  blank = %s)" % (tab,
                                                                         get_field_name(f), max_lf, min_lf, required_f, required_f)
                              
            elif type_of_vf == 'date':
                
                vf = "\n%s%s = models.DateField(validators = [MinValueValidator(%d), MaxValueValidator(%d)], null = %s,  blank = %s)" % (tab, 
                                                                            get_field_name(f), min_vf, max_vf, required_f, required_f)
                
            else:
                vf = "\n%s%s = models.TextField(validators = [MinLengthValidator(%d), MaxLengthValidator(%d)], null = %s,  blank = %s)" % (tab,
                                                                         get_field_name(f), min_lf, max_lf, required_f, required_f)
            ans.append(vf)
            
               
        default_value = "\n\n%sdef __unicode__(self):\n%s%sreturn self.%s" % (tab, tab, tab, default_return)
        meta_value = "\n\n%sclass Meta:\n%s%spermissions = (\n%s%s%s('can_view', 'Can view'),\n%s%s)" % (tab, tab, tab, tab, tab, tab, tab, tab )
        admin_locs = "".join("'%s', "  % camel_to_underscore_lower(l) for l in locations )
        admin_links = "".join("'%s', "  % camel_to_underscore_lower(l) for l in links )
        admin_fields = "".join("'%s', "  % get_field_name(f).lower() for f in model_fields )
        filter_fields = "".join("'%s', "  % f for f in filters )
        variables_data = "".join("%s" % an for an in ans)
        
        admin_value = "\n%s\nclass %sAdmin(admin.ModelAdmin):\
                                                        \n%slist_filter = (%s )\
                                                        \n%sexportable_fields = (%s %s )\
                                                        \n%ssearch_fields = (%s %s )\
                                                        \n%slist_display = (%s %s )\
                                                    \n%sactions = (export_model_as_csv, export_model_as_excel)\
                        \n\nadmin.site.register(%s, %sAdmin)\n%s\n" \
                        % (start_text, model_name, 
                           tab, filter_fields,
                           tab, filter_fields, admin_fields,
                           tab, filter_fields, admin_fields, 
                           tab, filter_fields, admin_fields,
                           tab,
                           model_name, model_name, end_text)
        admin_rep = "\nclass %sAdmin(admin.ModelAdmin):\
                                                        \n%slist_filter = (%s )\
                                                        \n%sexportable_fields = (%s %s )\
                                                        \n%ssearch_fields = (%s %s )\
                                                        \n%slist_display = (%s %s )\
                                                    \n%sactions = (export_model_as_csv, export_model_as_excel)\
                        \n\nadmin.site.register(%s, %sAdmin)\n" \
                        % (model_name, 
                           tab, filter_fields, 
                           tab, filter_fields, admin_fields,
                           tab, filter_fields, admin_fields,
                           tab, filter_fields, admin_fields,
                           tab,
                           model_name, model_name)
        data = "\n%s\nclass %s(models.Model):\n%s%s%s%s%s\n%s\n" \
                    % (start_text, model_name, custom_data, variables_data, locs_data, default_value, meta_value, end_text)
        data_rep = "\nclass %s(models.Model):\n%s%s%s%s%s\n" \
                    % (model_name, custom_data, variables_data, locs_data, default_value, meta_value)

                
        ##CHEK IF MODEL NOT DEFINED ALREADY
        m_filename = '%s/%s/models.py' % (API_PATH, app_label)
        m_f = get_block_of_text_link(m_filename, model_name, start_text,  end_text)
        
        if m_f:
            #print "THERE 1"
            if m_f['lines'] and m_f['start'] and m_f['end']:
                x = replace_block_of_text_link(m_filename, m_f['lines'], m_f['start'], m_f['end'], replace_with = data_rep)
                #print x 
            else:
                with open(m_filename, "a") as f:
                    f.write(data)
                    f.close()
        
        ##CHEK IF MODEL IN ADMIN NOT DEFINED ALREADY
        a_filename = '%s/%s/admin.py' % (API_PATH, app_label)
        a_f = get_block_of_text_link(a_filename, model_name, start_text,  end_text)
        if a_f:
            if a_f['lines'] and a_f['start'] and a_f['end']:
                y = replace_block_of_text_link(a_filename, a_f['lines'], a_f['start'], a_f['end'], replace_with = admin_rep) 
                #print y
            else:
                with open(a_filename, "a") as f:
                    f.write(admin_value)
                    f.close()

        status = propagate_db(get_model_object(app_label, model_name))
                                   
        return status

    except Exception, e:
        #print e
        return False

def import_sms_report(filepath = "rapidsmsrw1000/apps/api/messaging/smsreport.xls", sheetname = "smsreport"):
    book = open_workbook(filepath)
    sheet = book.sheet_by_name(sheetname)
    
    for row_index in range(sheet.nrows):
        if row_index < 1: continue   
        try:
            title_en            = sheet.cell(row_index,0).value
            title_rw            = sheet.cell(row_index,1).value
            keyword             = sheet.cell(row_index,2).value
            description         = sheet.cell(row_index,3).value
            field_separator     = sheet.cell(row_index,4).value
            in_use              = sheet.cell(row_index,5).value
            case_sensitive      = sheet.cell(row_index,6).value
            syntax_regex        = sheet.cell(row_index,7).value
            #created             = sheet.cell(row_index,8).value 

            #print title, keyword, description, field_separator, in_use , case_sensitive, syntax_regex, created
            sms_report, created = SMSReport.objects.get_or_create(keyword = keyword)

            sms_report.title_en = title_en
            sms_report.title_rw = title_rw
            sms_report.description = description
            sms_report.field_separator = field_separator
            sms_report.in_use = in_use
            sms_report.case_sensitive = case_sensitive
            sms_report.syntax_regex = syntax_regex
            #sms_report.created = created
                        
            sms_report.save()                   
            
            print "\ntitle : %s\n keyword : %s\n description : %s\n field_separator : %s\n in_use : %s\n case_sensitive: %s\n syntax_regex : %s\n \
                    created: %s \n" % (sms_report.title_en, sms_report.keyword, sms_report.description, sms_report.field_separator, sms_report.in_use, 
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
            title_en                    = sheet.cell(row_index, 0).value
            title_rw                    = sheet.cell(row_index, 1).value
            category_en                 = sheet.cell(row_index, 2).value
            category_rw                 = sheet.cell(row_index, 3).value
            sms_report_keyword          = sheet.cell(row_index, 4).value 
            prefix                      = sheet.cell(row_index, 5).value
            key                         = sheet.cell(row_index, 6).value 
            description                 = sheet.cell(row_index, 7).value 
            type_of_value               = sheet.cell(row_index, 8).value 
            upper_case                  = sheet.cell(row_index, 9).value 
            lower_case                  = sheet.cell(row_index, 10).value 
            try:    minimum_value               = int( sheet.cell(row_index, 11).value )
            except Exception, e: minimum_value = None
            try:    maximum_value               = int( sheet.cell(row_index, 12).value )
            except Exception, e: maximum_value = None
            try:    minimum_length              = int( sheet.cell(row_index, 13).value )
            except Exception, e: minimum_length = None
            try:    maximum_length              = int( sheet.cell(row_index, 14).value )
            except Exception, e: maximum_length = None 
            try:    position_after_sms_keyword  = int( sheet.cell(row_index, 15).value )
            except Exception, e: position_after_sms_keyword = None 
            depends_on_value_of         = sheet.cell(row_index, 16).value 
            dependency                  = sheet.cell(row_index, 17).value 
            allowed_value_list          = sheet.cell(row_index, 18).value 
            only_allow_one              = sheet.cell(row_index, 19).value 
            required                    = sheet.cell(row_index, 20).value 
            
            #print sms_report_keyword, prefix, key, description, type_of_value, upper_case, lower_case, minimum_value, maximum_value,\
            #        minimum_length, maximum_length, position_after_sms_keyword, depends_on_value_of, dependency, allowed_value_list, only_allow_one, required
            
            sms_report                                   = SMSReport.objects.get(keyword = sms_report_keyword)
            try:    dep                                  = SMSReportField.objects.get(key = depends_on_value_of)
            except Exception, e:    dep                  = None
            sms_report_field, created                    = SMSReportField.objects.get_or_create(key = key, sms_report = sms_report, 
                                                                                                    position_after_sms_keyword = position_after_sms_keyword)
            sms_report_field.title_en                    = title_en
            sms_report_field.title_rw                    = title_rw 
            sms_report_field.category_en                 = category_en
            sms_report_field.category_rw                 = category_rw            
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
            #print sms_report_field, minimum_value, maximum_value, minimum_length, maximum_length, position_after_sms_keyword
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

def import_sms_message(filepath = "rapidsmsrw1000/apps/api/messaging/smsmessage.xls", sheetname = "smsmessage"):
    book = open_workbook(filepath)
    sheet = book.sheet_by_name(sheetname)
    
    for row_index in range(sheet.nrows):
        if row_index < 1: continue   
        try:
            message_type                = sheet.cell(row_index, 0).value
            sms_report_keyword          = sheet.cell(row_index, 1).value 
            sms_report_field_key        = sheet.cell(row_index, 2).value
            message_en                  = sheet.cell(row_index, 3).value 
            message_rw                  = sheet.cell(row_index, 4).value 
            
            #print message_type, sms_report_keyword, sms_report_field_key, message_en, message_rw
            
            try:    sms_report                           = SMSReport.objects.get(keyword = sms_report_keyword)
            except Exception, e:    sms_report           = None
            try:    sms_report_field                     = SMSReportField.objects.get( key = sms_report_field_key, sms_report = sms_report)
            except Exception, e:    sms_report_field     = None
            
            sms_message, created                         = SMSMessage.objects.get_or_create(message_type = message_type, sms_report = sms_report,
                                                                                                 sms_report_field = sms_report_field)

            sms_message.sms_report                       = sms_report
            sms_message.sms_report_field                 = sms_report_field
            sms_message.message_en                       = message_en
            sms_message.message_rw                       = message_rw

            
            sms_message.save()                   
            
            print   sms_message.message_type                        ,\
                    sms_message.sms_report                          ,\
                    sms_message.sms_report_field                    ,\
                    sms_message.message_en                          ,\
                    sms_message.message_rw                          
            
        except Exception, e:
            print e, row_index
            pass
    
