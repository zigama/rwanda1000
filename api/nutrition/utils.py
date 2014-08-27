#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from rapidsmsrw1000.apps.api.nutrition.models import *
from pygrowup import helpers, Calculator
from rapidsmsrw1000.apps.utils import write, load

def build_nutrition_birth():
    filename = 'rapidsmsrw1000/apps/api/nutrition/json/bir.json'
    data = load(filename)
    bir = Report.objects.filter(type__name = 'Birth', pk__gt = data['last']).order_by('id')
    print "BUILD Total: %d" % bir.count()     
    for  b in bir:
        try:
            child = ChildRecord(b)
            data['last'] = child.report.pk
            write(data, filename)
        except Exception, e:
            print "Error: %s, Report: %s" % (e, b)
            data['error'].append(b.pk)
            write(data, filename)
            continue
        
def build_nutrition_pregnancy():
    filename = 'rapidsmsrw1000/apps/api/nutrition/json/pre.json'
    data = load(filename)
    pre = Report.objects.filter(type__name = 'Pregnancy', pk__gt = data['last']).order_by('id')
    print "BUILD Total: %d" % pre.count()    
    for  p in pre:
        try:
            woman = PregnancyRecord(p)
            data['last'] = woman.preg.pk
            write(data, filename)
        except Exception, e:
            print "Error: %s, Report: %s" % (e, p)
            data['error'].append(p.pk)
            write(data, filename)
            continue
    
def build_nutrition_cbn():
    filename = 'rapidsmsrw1000/apps/api/nutrition/json/cbn.json'
    data = load(filename)
    cbn = Report.objects.filter(type__name = 'Community Based Nutrition', pk__gt = data['last']).order_by('id')
    print "BUILD Total: %d" % cbn.count()
    for  c in cbn:
        try:
            child = ChildNutritionRecord(c)
            data['last'] = c.pk#child.report.pk
            write(data, filename)
        except Exception, e:
            print "Error: %s, Report: %s" % (e, c)
            data['error'].append(c.pk)
            write(data, filename)
            continue
        
def build_nutrition_chi():
    filename = 'rapidsmsrw1000/apps/api/nutrition/json/chi.json'
    data = load(filename)
    chi = Report.objects.filter(type__name = 'Child Health', pk__gt = data['last']).order_by('id')
    print "BUILD Total: %d" % chi.count()    
    for  c in chi:
        try:
            child = ChildRecord(c)
            data['last'] = child.report.pk
            write(data, filename)
        except Exception, e:
            print "Error: %s, Report: %s" % (e, c)
            data['error'].append(c.pk)
            write(data, filename)
            continue
    

def get_my_child(report):
    sex = 'Male'
    if report.child.gender:
        sex = 'Female' if report.child.gender.lower() is 'gi' else sex
    valid_gender = helpers.get_good_sex( sex )
    valid_date = str(int(round((report.report.created.date() - report.date_of_birth).days / 30.4375)))
    weight = height = muac = None
    try:
        weight = report.weight
        height = report.height
        muac = report.muac
    except: pass
    return {'weight': weight, 'valid_age': valid_date, 'valid_gender': valid_gender, 'height': height, 'muac': muac}

def get_my_child_zscores(child):
    cg = Calculator(adjust_height_data=False, adjust_weight_scores=False)
    wfa = lhfa = wfh = wfl = None

    try: wfa = cg.zscore_for_measurement('wfa', child['weight'], child['valid_age'], child['valid_gender'])
    except: pass
    try: lhfa = cg.zscore_for_measurement('lhfa', child['height'] or child['muac'], child['valid_age'], child['valid_gender'])
    except: pass
    try: wfh = cg.zscore_for_measurement('wfh', child['weight'], child['valid_age'], child['valid_gender'], child['height'])
    except: pass
    try: wfl = cg.zscore_for_measurement('wfl', child['weight'], child['valid_age'], child['valid_gender'], child['muac'])
    except: pass

    return {'wfa': wfa, 'lhfa': lhfa, 'wfh' : wfh, 'wfl': wfl, 'age': child['valid_age'], 'sex' : child['valid_gender']}

class ChildRecord(object):

    def __init__ (self, report):
        self.record = None
        self.report = report
        if report.type.name == 'Community Based Nutrition':
            self.record = ChildNutritionRecord(self.report)
        if report.type.name == 'Child Health':
            self.record = ChildHealthRecord(self.report)
        if report.type.name == 'Birth':
            self.record = BirthRecord(self.report)
            
        self.mother = self.record.mother
        self.child_number = self.record.child_number
        self.date_of_birth = self.record.date_of_birth
        self.birth = None
        self.gender = None
        self.symptoms =  ""
        self.location = None
        self.breastfeeding = None
        self.birth_weight = None

        try:
            self.birth = BirthRecord(self.get_birth(self.record))
            self.gender = self.birth.gender
            self.symptoms =  self.birth.symptoms
            self.location = self.birth.location
            self.breastfeeding = self.birth.breastfeeding
            self.birth_weight = self.birth.weight
        except: pass

        child = self.save_or_update()
        self.record.save_or_update(child)

    def get_birth(self, record):
        births = Report.objects.filter( patient__national_id = self.record.mother, date = self.record.date_of_birth, type__name = 'Birth')
        birth = None
        for b in births:
            birth = b.fields.get(type__key = 'child_number', value = self.record.child_number).report
        return birth
        
    def save_or_update(self):
        child, created = Child.objects.get_or_create(mother = self.report.patient, chw = self.report.reporter, child_number = self.child_number, date_of_birth = self.date_of_birth)
        
        child.nation = self.report.nation
        child.province = self.report.province
        child.district = self.report.district
        child.sector = self.report.sector
        child.cell = self.report.cell
        child.village    = self.report.village
        child.health_centre = self.report.location
        child.referral_hospital = self.report.reporter.referral_hospital

        child.gender = self.gender 
        child.birth_symptoms = self.symptoms
        child.birth_location = self.location
        child.birth_breastfeeding = self.breastfeeding
        child.birth_weight = self.birth_weight

        try: child.is_premature = True if "pm" in self.symptoms.split(" ") else False
        except: pass

        child.save()

        return child
        

class BirthRecord(object):
    """
    The Birth report has to be parsed at receipt of the raw SMS and
    Its content has to be parsed and instantiate in this object.
    """
        
    def __init__(self, birth_report):
        self.birth = birth_report
        self.mother = None
        self.child_number = None
        self.date_of_birth = None
        self.gender = None
        self.symptoms = None
        self.location = None
        self.breastfeeding = None
        self.weight = None

        self.check_errors()             
        
    def check_errors(self):
        
           
        ## parse mother national_id
        try:
            self.mother = self.get_patient_id()
        except :
            pass
        
        ## parse child number
        try:
            self.child_number = self.get_child_number()
        except :
            pass
        
        ## parse date of birth
        try:
            self.date_of_birth = self.get_date_of_birth()
        except :
            pass
        
        ## parse child gender
        try:
            self.gender = self.get_gender()
        except :
            pass
        
        ## parse symptoms
        try:
            self.symptoms = self.get_symptoms()
        except :
            pass
        
        ## parse delivery location
        try:
            self.location = self.get_location( )
        except :
            pass
        
        ## parse breastfeeding
        try:
            self.breastfeeding = self.get_breastfeeding( )
        except :
            pass
        
        ## parse child weight
        try:
            self.weight = self.get_weight()
        except :
            pass
        
        return True
    
    def get_patient_id(self):
        nid = self.birth.patient.national_id
        return nid
        
    def get_child_number(self):
        chino = int(self.birth.fields.get(type__key = 'child_number').value)
        return chino
              
    def get_date_of_birth(self):
        dob = self.birth.date
        return dob
    
    def get_gender(self):
        gender = self.birth.fields.get(type__key__in = BIRTH_GENDER_PATTERN.split('|')).type.key
        return gender
                
    def get_symptoms(self):
        symptoms = ""
        symps = self.birth.fields.all().values('type__key')
        
        for s in symps:
            if s['type__key'] in BIRTH_SYMPTOMS_PATTERN.split("|"):
                symptoms = symptoms + "%s " % s['type__key']

        return symptoms.strip()
            
    def get_location(self):
        loc = self.birth.fields.get(type__key__in  = BIRTH_LOCATION_PATTERN.split("|")).type.key
        return loc
        
    def get_breastfeeding(self):
        bf = self.birth.fields.get(type__key__in = BIRTH_BREASTFEEDING_PATTERN.split('|')).type.key 
        return bf
                
    def get_weight(self):
        weight = self.birth.fields.get(type__key = 'child_weight').value
        return weight
    
    def save_or_update(self, child):

        bir, created = Birth.objects.get_or_create(mother = self.birth.patient, child = child, chw = self.birth.reporter, report = self.birth, child_number = self.child_number, date_of_birth = self.date_of_birth)
        
        bir.nation = self.birth.nation
        bir.province = self.birth.province
        bir.district = self.birth.district
        bir.sector = self.birth.sector
        bir.cell = self.birth.cell
        bir.village    = self.birth.village
        bir.health_centre = self.birth.location
        bir.referral_hospital = self.birth.reporter.referral_hospital

        bir.gender = self.gender 
        bir.symptoms = self.symptoms
        bir.located = self.location
        bir.breastfeeding = self.breastfeeding
        bir.weight = self.weight

        bir.is_premature = True if "pm" in bir.symptoms.split(" ") else False

        bir.save()
        child._get_status()



class ChildNutritionRecord(object):
    """
    The child nutrition report has to be parsed at receipt of the raw SMS and
    Its content has to be parsed and instantiate in this object.
    """
        
    def __init__(self, cbn_report):
        self.cbn = cbn_report
        self.mother = None
        self.child_number = None
        self.date_of_birth = None
        self.breastfeeding = None
        self.height = None
        self.weight = None
        self.muac = None
        self.zscore = None

        self.check_errors()
                    
    def check_errors(self):
        
        ## parse mother national_id
        try:
            self.mother = self.get_patient_id()
        except :
            pass
        
        ## parse child number
        try:
            self.child_number = self.get_child_number()
        except :
            pass
        
        ## parse date of birth
        try:
            self.date_of_birth = self.get_date_of_birth()
        except :
            pass
        
        ## parse breastfeeding
        try:
            self.breastfeeding = self.get_breastfeeding()
        except :
            pass
        
        ## parse Child height
        try:
            self.height = self.get_height()
        except :
            pass
        
        ## parse child weight
        try:
            self.weight = self.get_weight()
        except :
            pass

        ## parse child muac
        try:
            self.muac = self.get_muac()
        except :
            pass
        
        return True
    
    def get_patient_id(self):
        nid = self.cbn.patient.national_id
        return nid
        
    def get_child_number(self):
        chino = int(self.cbn.fields.get(type__key = 'child_number').value)
        return chino
              
    def get_date_of_birth(self):
        dob = self.cbn.date
        return dob
        
    def get_breastfeeding(self):
        bf = self.cbn.fields.get(type__key__in = CBN_BREASTFEEDING_PATTERN.split('|')).type.key 
        return bf

    def get_height(self):
        try:
            height = self.cbn.fields.get(type__key = 'child_height').value
            return height
        except: return None
                
    def get_weight(self):
        weight = self.cbn.fields.get(type__key = 'child_weight').value
        return weight

    def get_muac(self):
        muac = self.cbn.fields.get(type__key = 'muac').value
        return muac

    def get_child(self):
        child = Child.objects.get( mother__national_id = self.mother, date_of_birth = self.date_of_birth, child_number = int(self.child_number))
        return child

    def save_or_update(self):
        child = self.get_child()
        chn, created = ChildNutrition.objects.get_or_create(mother = self.cbn.patient, child = child, chw = self.cbn.reporter, report = self.cbn, child_number = self.child_number, date_of_birth = self.date_of_birth)
        
        chn.nation = self.cbn.nation
        chn.province = self.cbn.province
        chn.district = self.cbn.district
        chn.sector = self.cbn.sector
        chn.cell = self.cbn.cell
        chn.village    = self.cbn.village
        chn.health_centre = self.cbn.location
        chn.referral_hospital = self.cbn.reporter.referral_hospital
        
        chn.breastfeeding = self.breastfeeding
        chn.height = self.height
        chn.weight = self.weight
        chn.muac = self.muac
        
        self.zscore = get_my_child_zscores(get_my_child(chn))
        
        #chn.gender = self.zscore['sex']
        chn.age_in_months = self.zscore['age']
        chn.weight_for_age = self.zscore['wfa']
        chn.length_height_for_age = self.zscore['lhfa']
        chn.weight_for_height = self.zscore['wfh']
        chn.weight_for_length = self.zscore['wfl']

        chn.save()
        child._get_status()


class ChildHealthRecord(object):
    """
    The child health report has to be parsed at receipt of the raw SMS and
    Its content has to be parsed and instantiate in this object.
    """
        
    def __init__(self, chi_report):
        self.chi= chi_report
        self.mother = None
        self.child_number = None
        self.date_of_birth = None
        self.vaccination_received = None
        self.vaccination_status = None
        self.symptoms = None
        self.location = None
        self.weight = None
        self.muac = None
        self.zscore = None
    
        self.check_errors()
            
    def check_errors(self):
        
        ## parse mother national_id
        try:
            self.mother = self.get_patient_id()
        except :
            pass
        
        ## parse child number
        try:
            self.child_number = self.get_child_number()
        except :
            pass
        
        ## parse date of birth
        try:
            self.date_of_birth = self.get_date_of_birth()
        except :
            pass
        
        
        ## parse Vaccination series received
        try:
            self.vaccination_received = self.get_vaccination_received( )
        except :
            pass
        
        ## parse Vaccination series status
        try:
            self.vaccination_status = self.get_vaccination_status()
        except :
            pass
        
                
        ## parse symptoms
        try:
            self.symptoms = self.get_symptoms( )
        except :
            pass
        
        ## parse delivery location
        try:
            self.location = self.get_location( )
        except :
            pass
        
        ## parse child weight
        try:
            self.weight = self.get_weight()
        except :
            pass
        
        ## parse child muac
        try:
            self.muac = self.get_muac()
        except :
            pass
        
        return True
    
    def get_patient_id(self):
        nid = self.chi.patient.national_id
        return nid
        
    def get_child_number(self):
        chino = int(self.chi.fields.get(type__key = 'child_number').value)
        return chino
              
    def get_date_of_birth(self):
        dob = self.chi.date
        return dob
        
    def get_vaccination_received(self):
        vaccination_received = self.chi.fields.get(type__key__in  = CHI_VACCINATION_RECEIVED_PATTERN.split('|')).type.key
        return vaccination_received
        
    def get_vaccination_status(self):
        vaccination_status = self.chi.fields.get(type__key__in  = CHI_VACCINATION_STATUS_PATTERN.split('|')).type.key
        return vaccination_status
        
    def get_symptoms(self):
        symptoms = ""
        symps = self.chi.fields.all().values('type__key')
        
        for s in symps:
            if s['type__key'] in CHI_SYMPTOMS_PATTERN.split("|"):
                symptoms = symptoms + "%s " % s['type__key']

        return symptoms.strip()
            
    def get_location(self):
        loc = self.chi.fields.get(type__key__in  = CHI_LOCATION_PATTERN.split("|")).type.key
        return loc
        
    def get_weight(self):
        weight = self.chi.fields.get(type__key = 'child_weight').value
        return weight

    def get_muac(self):
        muac = self.chi.fields.get(type__key = 'muac').value
        return muac

    def get_child(self):
        child = Child.objects.get( mother__national_id = self.mother, date_of_birth = self.date_of_birth, child_number = int(self.child_number))
        return child

    def save_or_update(self):
        child = self.get_child()
        chh, created = ChildHealth.objects.get_or_create(mother = self.chi.patient, child = child, chw = self.chi.reporter, report = self.chi, child_number = self.child_number, date_of_birth = self.date_of_birth)
        
        chh.nation = self.chi.nation
        chh.province = self.chi.province
        chh.district = self.chi.district
        chh.sector = self.chi.sector
        chh.cell = self.chi.cell
        chh.village    = self.chi.village
        chh.health_centre = self.chi.location
        chh.referral_hospital = self.chi.reporter.referral_hospital

        chh.vaccination_received = self.vaccination_received
        chh.vaccination_status = self.vaccination_status
        chh.current_symptoms = self.symptoms
        chh.location = self.location
        chh.weight = self.weight
        chh.muac = self.muac

        self.zscore = get_my_child_zscores(get_my_child(chh))
        
        #chh.gender = self.zscore['sex']
        chh.age_in_months = self.zscore['age']
        chh.weight_for_age = self.zscore['wfa']
        chh.length_height_for_age = self.zscore['lhfa']
        chh.weight_for_height = self.zscore['wfh']
        chh.weight_for_length = self.zscore['wfl']

        chh.save()
        child._get_status()


class PregnancyRecord(object):
    """
    The Pregnancy report has to be parsed at receipt of the raw SMS and
    Its content has to be parsed and instantiate in this object.
    """
        
    def __init__(self, report):
        self.preg = report
        self.woman = None
        self.last_menstrual_period = None
        self.expected_anc2_date = None
        self.expected_delivery_date = None
        self.expected_anc2_date = None
        self.expected_anc3_date = None
        self.expected_anc4_date = None
        self.gravidity = None
        self.parity = None
        self.previous_symptoms = None
        self.current_symptoms = None
        self.location = None
        self.weight = None
        self.height = None
        self.bmi_anc1 = None
        self.toilet = None
        self.handwashing = None   
             
        self.check_errors()
        self.set_bmi()
        self.set_expected_delivery_date()
        self.set_expected_anc_dates()

        self.save_or_update()
        
    def check_errors(self):
        
        ## parse patient national_id
        try:
            self.woman = self.get_patient_id()
        except:
            pass
        
        ## parse last menstrual period date
        try:
            self.last_menstrual_period = self.get_last_menstrual_period()
        except:
            pass
        
        ## parse Second ANC Appointment Date
        try:
            self.expected_anc2_date = self.get_expected_anc2_date()
        except:
            pass
        
        ## parse gravidity
        try:
            self.gravidity = self.get_gravidity()
        except:
            pass
        
        ## parse parity
        try:
            self.parity = self.get_parity()
        except:
            pass
        
        ## parse previous symptoms
        try:
            self.previous_symptoms = self.get_previous_symptoms()
        except:
            pass
        
        ## parse current symptoms
        try:
            self.current_symptoms = self.get_current_symptoms()
        except:
            pass
        
        ## parse pregnancy confirmation location
        try:
            self.location = self.get_location( )
        except:
            pass
        
        ## parse Mother weight
        try:
            self.weight = self.get_weight()
        except:
            pass
        
        ## parse Mother height
        try:
            self.height = self.get_height()
        except:
            pass
        
        ## parse Toilet
        try:
            self.toilet = self.get_toilet()
        except:
            pass
        
        ## parse Handwashing
        try:
            self.handwashing = self.get_handwashing()
        except:
            pass
        
    def set_bmi(self):
        try:
            weight = self.weight
            height = self.height
            bmi = weight*100*100/(height*height)
            self.bmi_anc1 = round(bmi,2)
            return True
        except:
            pass
        
    def set_expected_delivery_date(self):
        try:
            self.expected_delivery_date = Pregnancy.calculate_edd(self.last_menstrual_period)
            return True
        except:
            pass
    
    def set_expected_anc_dates(self):
        try:
            self.expected_anc3_date =  self.expected_delivery_date - datetime.timedelta(DAYS_ANC3)
            self.expected_anc4_date =  self.expected_delivery_date - datetime.timedelta(DAYS_ANC4)
            return True
        except:
            pass
    
    def get_patient_id(self):
        nid = self.preg.patient.national_id
        return nid
        
    def get_last_menstrual_period(self):
        """
        Parse the date of last menstrual period from a raw SMS text.
        This date cannot be in the future or older than 9 moths.
        
        """
        lmp = self.preg.date
        return lmp
        
    def get_expected_anc2_date(self):
        """
        Parse the date of last menstrual period from a raw SMS text.
        This date cannot be in the future or older than 9 moths.
        
        """
        expected_anc2_date = self.preg.edd_anc2_date
        return expected_anc2_date
        
        
    def get_gravidity(self):
        gravidity = self.preg.fields.get(type__key = 'gravity').value
        return int(gravidity)

    def get_parity(self):
        parity = self.preg.fields.get(type__key = 'parity').value
        return int(parity)
            
        
    def get_previous_symptoms(self):
        symptoms = ""
        symps = self.preg.fields.all().values('type__key')
        
        for s in symps:
            if s['type__key'] in PREVIOUS_SYMPTOMS_PATTERN.split("|"):
                symptoms = symptoms + "%s " % s['type__key']

        return symptoms.strip()
                        
    def get_current_symptoms(self):
        symptoms = ""
        symps = self.preg.fields.all().values('type__key')
        
        for s in symps:
            if s['type__key'] in CURRENT_SYMPTOMS_PATTERN.split("|"):
                symptoms = symptoms + "%s " % s['type__key']

        return symptoms.strip()
            
    def get_location(self):
        loc = self.preg.fields.get(type__key__in  = PREGNANCY_LOCATION_PATTERN.split("|")).type.key
        return loc
        
    def get_weight(self):
        weight = self.preg.fields.get(type__key = 'mother_weight').value
        return float(weight)

    def get_height(self):
        height = self.preg.fields.get(type__key = 'mother_height').value
        return float(height)

    def get_toilet(self):
        toilet = self.preg.fields.get(type__key__in  = TOILET_PATTERN.split("|")).type.key
        return toilet
    
    def get_handwashing(self):
        handwashing = self.preg.fields.get(type__key__in  = HANDWASHING_PATTERN.split("|")).type.key
        return handwashing

    def save_or_update(self):
 
        preg, created = Pregnancy.objects.get_or_create(woman = self.preg.patient, chw = self.preg.reporter, report = self.preg, last_menstrual_period = self.last_menstrual_period)
        
        preg.nation = self.preg.nation or self.preg.reporter.nation
        preg.province = self.preg.province or self.preg.reporter.provinve
        preg.district = self.preg.district or self.preg.reporter.district
        preg.sector = self.preg.sector or self.preg.reporter.sector
        preg.cell = self.preg.cell or self.preg.reporter.cell
        preg.village    = self.preg.village or self.preg.reporter.village
        preg.health_centre = self.preg.location or self.preg.reporter.health_centre
        preg.referral_hospital = self.preg.reporter.referral_hospital or self.preg.reporter.referral_hospital

        preg.weight = self.weight 
        preg.height = self.height 
        preg.bmi_anc1 = self.bmi_anc1
        preg.gravidity = self.gravidity
        preg.parity = self.parity

        preg.previous_symptoms = self.previous_symptoms
        preg.current_symptoms = self.current_symptoms
        preg.location = self.location
        preg.toilet = self.toilet
        preg.handwashing = self.handwashing

        preg.last_menstrual_period = self.last_menstrual_period 
        preg.expected_delivery_date              =  self.expected_delivery_date
        preg.expected_anc2_date         =   self.expected_anc2_date
        preg.expected_anc3_date         =   self.expected_anc3_date 
        preg.expected_anc4_date         =   self.expected_anc4_date 

        preg.is_risky = False if "np" in self.current_symptoms.split(" ") else True
        preg.is_high_risky = False if "nr" in self.previous_symptoms.split(" ") else True

        preg.save()


#from rapidsmsrw1000.apps.api.nutrition.utils import *
#p = Report.objects.filter(type__name = 'Pregnancy')[200]
#pr = PregnancyRecord(p)


