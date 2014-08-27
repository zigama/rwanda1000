#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from rapidsmsrw1000.apps.utils import *
from rapidsmsrw1000.apps.api.nutrition.models import *
from piston.handler import BaseHandler
from django.contrib.auth import authenticate
from django.http import HttpResponse

from piston.utils import require_mime,rc
from django.contrib.auth.models import User
from django.core import serializers

def n_months_ago(n_months, given_date):
    return given_date - datetime.timedelta(n_months * 30.4375)

class StatisticsHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = [Pregnancy, Child, Birth, ChildNutrition]
    def read(self, request, key = None):
        
        data = []
        loc_f = {}
        try:
            filters = {'period':default_period(request),
                         'location':default_location(request),
                         'province':default_province(request),
                         'district':default_district(request)}
        
            start, end = filters['period']['start'], filters['period']['end'] 
            #print start,end
            
            if request.REQUEST.has_key('province'):
                loc_f['province__id'] = int(request.REQUEST['province'])
            if request.REQUEST.has_key('district'):
                loc_f['district__id'] = int(request.REQUEST['district'])
            if request.REQUEST.has_key('location'):
                loc_f['health_centre__id'] = int(request.REQUEST['location'])
                        
            #print loc_f
            
            pregs = Pregnancy.objects.filter(expected_delivery_date__gte = start, **loc_f)
            pregs_less_150cm = pregs.filter(height__lt = 150)
            maternal_height = {'key': 'mother_height','desc': "Proportion of pregnant women with height <150cm at 1st ANC", 'total': "%d / %d" % (pregs_less_150cm.count(),pregs.count())}        
            data.append(maternal_height)
            
            pregs_bmi_less_18_5 = pregs.filter(bmi_anc1__lt = 18.5)
            maternal_bmi = {'key': 'mother_weight', 'desc': "Proportion of pregnant women with BMI <18.5 at 1st ANC", 'total': "%d / %d" % (pregs_bmi_less_18_5.count(), pregs.count())}
            data.append(maternal_bmi)
            
            births = Birth.objects.filter(date_of_birth__gte = start, date_of_birth__lte = end, **loc_f)
            birth_weight_less_2_5 = births.filter(weight__lt = 2.5)
            birth_weight = {'key': 'child_weight','desc': "Proportion of live births with birth weight below 2.5kg", 'total': "%d / %d" % (birth_weight_less_2_5.count(), births.count())}
            data.append(birth_weight)
            
            birth_not_premature = births.filter(child__is_premature = False)
            birth_term = {'key': 'te','desc': "Proportion of live births born at term", 'total': "%d / %d" % (birth_not_premature.count(), births.count())}
            data.append(birth_term)
            
            birth_bf1 = births.filter(breastfeeding = 'bf1')
            bf1 = {'key': 'ebf1','desc':"Proportion of live births breastfed within 1st hour", 'total': "%d / %d" % (birth_bf1.count(), births.count())}
            data.append(bf1)
            
            children_6_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(6, start),  date_of_birth__lte = n_months_ago(6, end), **loc_f)
            cbn_6_months_old = ChildNutrition.objects.filter(child__in = children_6_months_old, age_in_months = 6, **loc_f)
            heighted_6_months_old = cbn_6_months_old.exclude(height = None)
            cbn_height_6 = {'key':'child_height_6' , 'desc': 'Proportion of children whose height is measured at 6 months old', 'total': "%d / %d" % (heighted_6_months_old.count(), children_6_months_old.count())}
            data.append(cbn_height_6)
            weighted_6_months_old = cbn_6_months_old.exclude(weight = None)
            cbn_weight_6 = {'key': 'child_weight_6', 'desc': 'Proportion of children whose weight is measured at 6 months old', 'total': "%d / %d" % (weighted_6_months_old.count(), children_6_months_old.count())}
            data.append(cbn_weight_6)
            stunted_6_months_old =  cbn_6_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
            cbn_stunted_6 = {'key': 'child_stunted_6', 'desc': 'Proportion of U2 children stunted at 6 months of age', 'total': "%d / %d" % (stunted_6_months_old.count(), children_6_months_old.count())}
            data.append(cbn_stunted_6)
            wasted_6_months_old =  cbn_6_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
            cbn_wasted_6 = {'key': 'child_wasted_6', 'desc': 'Proportion of U2 children wasted at 6 months of age', 'total': "%d / %d" % (wasted_6_months_old.count(), children_6_months_old.count())}
            data.append(cbn_wasted_6)
            underweight_6_months_old =  cbn_6_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
            cbn_underweight_6 = {'key': 'child_underweight_6', 'desc': 'Proportion of U2 children underweight at 6 months of age', 'total': "%d / %d" % (underweight_6_months_old.count(), children_6_months_old.count())}
            data.append(cbn_underweight_6) 
            
            children_9_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(9, start),  date_of_birth__lte = n_months_ago(9, end), **loc_f)
            cbn_9_months_old = ChildNutrition.objects.filter(child__in = children_9_months_old, age_in_months = 9, **loc_f)
            heighted_9_months_old = cbn_9_months_old.exclude(height = None)
            cbn_height_9 = {'key':'child_height_9' , 'desc': 'Proportion of children whose height is measured at 9 months old', 'total': "%d / %d" % (heighted_9_months_old.count(), children_9_months_old.count())}
            data.append(cbn_height_9)
            weighted_9_months_old = cbn_9_months_old.exclude(weight = None)
            cbn_weight_9 = {'key': 'child_weight_9', 'desc': 'Proportion of children whose weight is measured at 9 months old', 'total': "%d / %d" % (weighted_9_months_old.count(), children_9_months_old.count())}
            data.append(cbn_weight_9)
            stunted_9_months_old =  cbn_9_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
            cbn_stunted_9 = {'key': 'child_stunted_9', 'desc': 'Proportion of U2 children stunted at 9 months of age', 'total': "%d / %d" % (stunted_9_months_old.count(), children_9_months_old.count())}
            data.append(cbn_stunted_9)
            wasted_9_months_old =  cbn_9_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
            cbn_wasted_9 = {'key': 'child_wasted_9', 'desc': 'Proportion of U2 children wasted at 9 months of age', 'total': "%d / %d" % (wasted_9_months_old.count(), children_9_months_old.count())}
            data.append(cbn_wasted_9)
            underweight_9_months_old =  cbn_9_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
            cbn_underweight_9 = {'key': 'child_underweight_9', 'desc': 'Proportion of U2 children underweight at 9 months of age', 'total': "%d / %d" % (underweight_9_months_old.count(), children_9_months_old.count())}
            data.append(cbn_underweight_9)  
            
            children_18_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(18, start),  date_of_birth__lte = n_months_ago(18, end), **loc_f)
            cbn_18_months_old = ChildNutrition.objects.filter(child__in = children_18_months_old, age_in_months = 18, **loc_f)
            heighted_18_months_old = cbn_18_months_old.exclude(height = None)
            cbn_height_18 = {'key':'child_height_18' , 'desc': 'Proportion of children whose height is measured at 18 months old', 'total': "%d / %d" % (heighted_18_months_old.count(), children_18_months_old.count())}
            data.append(cbn_height_18)
            weighted_18_months_old = cbn_18_months_old.exclude(weight = None)
            cbn_weight_18 = {'key': 'child_weight_18', 'desc': 'Proportion of children whose weight is measured at 18 months old', 'total': "%d / %d" % (weighted_18_months_old.count(), children_18_months_old.count())}
            data.append(cbn_weight_18)
            stunted_18_months_old =  cbn_18_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
            cbn_stunted_18 = {'key': 'child_stunted_18', 'desc': 'Proportion of U2 children stunted at 18 months of age', 'total': "%d / %d" % (stunted_18_months_old.count(), children_18_months_old.count())}
            data.append(cbn_stunted_18)
            wasted_18_months_old =  cbn_18_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
            cbn_wasted_18 = {'key': 'child_wasted_18', 'desc': 'Proportion of U2 children wasted at 18 months of age', 'total': "%d / %d" % (wasted_18_months_old.count(), children_18_months_old.count())}
            data.append(cbn_wasted_18)
            underweight_18_months_old =  cbn_18_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
            cbn_underweight_18 = {'key': 'child_underweight_18', 'desc': 'Proportion of U2 children underweight at 18 months of age', 'total': "%d / %d" % (underweight_18_months_old.count(), children_18_months_old.count())}
            data.append(cbn_underweight_18) 
            
            children_24_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(24, start),  date_of_birth__lte = n_months_ago(24, end), **loc_f)
            cbn_24_months_old = ChildNutrition.objects.filter(child__in = children_24_months_old, age_in_months = 24, **loc_f)
            heighted_24_months_old = cbn_24_months_old.exclude(height = None)
            cbn_height_24 = {'key':'child_height_24' , 'desc': 'Proportion of children whose height is measured at 24 months old', 'total': "%d / %d" % (heighted_24_months_old.count(), children_24_months_old.count())}
            data.append(cbn_height_24)
            weighted_24_months_old = cbn_24_months_old.exclude(weight = None)
            cbn_weight_24 = {'key': 'child_weight_24', 'desc': 'Proportion of children whose weight is measured at 24 months old', 'total': "%d / %d" % (weighted_24_months_old.count(), children_24_months_old.count())}
            data.append(cbn_weight_24)
            stunted_24_months_old =  cbn_24_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
            cbn_stunted_24 = {'key': 'child_stunted_24', 'desc': 'Proportion of U2 children stunted at 24 months of age', 'total': "%d / %d" % (stunted_24_months_old.count(), children_24_months_old.count())}
            data.append(cbn_stunted_24)
            wasted_24_months_old =  cbn_24_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
            cbn_wasted_24 = {'key': 'child_wasted_24', 'desc': 'Proportion of U2 children wasted at 24 months of age', 'total': "%d / %d" % (wasted_24_months_old.count(), children_24_months_old.count())}
            data.append(cbn_wasted_24)
            underweight_24_months_old =  cbn_24_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
            cbn_underweight_24 = {'key': 'child_underweight_24', 'desc': 'Proportion of U2 children underweight at 24 months of age', 'total': "%d / %d" % (underweight_24_months_old.count(), children_24_months_old.count())}
            data.append(cbn_underweight_24) 
            
        except Exception,e:
            #print e 
            pass
        
        stats = {'count': len(data), 'records': data}
        
        return stats


class ChildHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Child
    fields=('id','mother','child_number', 'date_of_birth', 'valid_gender', 'status', 'details', 'history', 'village', 'cell', 'sector', 'health_centre', 'referral_hospital', 'district', 'province', 'history')

    def read(self, request, pk = None):
        
        loc_f = {}
        data = {}
        try:
        
            if request.REQUEST.has_key('province'):
                loc_f['province__id'] = int(request.REQUEST['province'])
            if request.REQUEST.has_key('district'):
                loc_f['district__id'] = int(request.REQUEST['district'])
            if request.REQUEST.has_key('location'):
                loc_f['health_centre__id'] = int(request.REQUEST['location'])
                        
            #print loc_f,request.REQUEST
            
            children = Child.objects.filter( **loc_f)
            
            if pk:
                data = children.filter(pk = pk)
                #history = data[0]
                #print "HISTORY : %s" %history
            else:
                data = children
    
            if request.REQUEST.has_key('filter'):
                filters = {}
                query_str = json.loads(request.REQUEST['filter'])
                for f in query_str:
                    if 'comparison' in f.keys():
                        filters[f['field']] = {}
                
                for f in query_str:
                    if 'comparison' in f.keys():
                        comp = f['comparison']                        
                        filters[f['field']][comp] = f['value']
                    else:
                        filters[f['field']] = f['value']
                    
                #for f in filters.keys():
                    #print f, query_str
                try: 
                    ### by cstatus
                    if 'status' in filters.keys(): 
                        status = filters['status']
                        data = data.filter(status__icontains = status)
                    
                    ### by Mother
                    if 'mother' in filters.keys():
                        mother = filters['mother']
                        data = data.filter(mother__national_id__icontains = mother)
                        
                    ### by Mother
                    if 'valid_gender' in filters.keys():
                        if filters['valid_gender'].lower() == 'f':
                            gender = 'gi'
                        elif filters['valid_gender'].lower() == 'm':
                            gender = 'bo'
                        else:
                            gender = ""
                        data = data.filter(gender__icontains = gender)
                        
                    ### by date_of_birth
                    if 'date_of_birth' in filters.keys():
                        dob = filters['date_of_birth']
                        if 'lt' in dob.keys() and 'gt' in dob.keys():
                            #print dob['gt'],dob['lt']
                            data = data.filter(date_of_birth__gt = datetime.datetime.strptime(dob['gt'], "%m/%d/%Y").date(), date_of_birth__lt = datetime.datetime.strptime(dob['lt'], "%m/%d/%Y").date())
                        elif 'eq' in dob.keys():
                            #print datetime.datetime.strptime(dob['eq'], "%m/%d/%Y").date()
                            data = data.filter(date_of_birth = datetime.datetime.strptime(dob['eq'], "%m/%d/%Y").date())
                    
                except Exception, e:
                    #print e
                    pass
                
            stats = {'count': data.count(), 'records': data}
            
            if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
                start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
                data = data[start:limit]
                stats['records'] = data
            else:
                data = data[0:10]
                stats['records'] = data
                      
            return stats
        
        except Exception, e:
            #print e
            
            return {'count': None, 'records': None}
    
class ChildNutritionHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = ChildNutrition
    fields=('id', 'mother', 'child_number', 'date_of_birth', 'gender', 'breastfeeding', 'weight', 'height','muac', 'village', 'cell', 'sector', 'health_centre', 'referral_hospital', 'district', 'province')

    def read(self, request, pk = None):
        
        loc_f = {}
        data = {}
        
        try:
            #filters = {'period':default_period(request),}
            #start_date, end_date = filters['period']['start'], filters['period']['end']
            #print start_date, end_date
            
            if request.REQUEST.has_key('province'):
                loc_f['province__id'] = int(request.REQUEST['province'])
            if request.REQUEST.has_key('district'):
                loc_f['district__id'] = int(request.REQUEST['district'])
            if request.REQUEST.has_key('location'):
                loc_f['health_centre__id'] = int(request.REQUEST['location'])
                        
            print loc_f
            
            cbn = ChildNutrition.objects.filter(**loc_f).order_by('-report__created')
            
            if pk:
                data = cbn.filter(pk = pk)
            else:
                data = cbn
                
            stats = {'count': data.count(), 'records': data}
    
            if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
                start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
                data = data[start:limit]
                stats['records'] = data
            else:
                data = data[0:10]
                stats['records'] = data
            
            #print stats    
            return stats
        
        except Exception, e:
            #print e
            return {'count': None, 'records': None}

    
class PregnancyHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Pregnancy
    fields=('id','woman','child_number', 'last_menstrual_period', 'expected_anc2_date', 'expected_delivery_date', 'gravidity', 'parity', 'previous_symptoms', 'current_symptoms', 'location', 'weight', 'height', 'toilet', 'handwashing', 'village', 'cell', 'sector', 'health_centre', 'referral_hospital', 'district', 'province')

    def read(self, request, pk = None):
        
        pregs = Pregnancy.objects.all()
        if pk:
            data = pregs.filter(pk = pk)
        else:
            data = pregs
            
        stats = {'count': data.count(), 'records': data}

        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:10]
            stats['records'] = data

        return stats


class ProvinceHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Province
    fields=('id','name','code')

    def read(self, request, code = None):
        
        data = {}
        provinces = Province.objects.all().exclude(name = 'TEST')
        if code:
            data = provinces.filter(code = code)
            
        else:
            data = provinces
            
        stats = {'count': data.count(), 'records': data}
        
        return stats

class DistrictHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = District
    fields=('id','name','code', 'province_id')

    def read(self, request, code = None):
        data = {}
        districts = District.objects.all().exclude(name = 'TEST')
        if code:
            data = districts.filter(code = code)
        else:
            data = districts
        
        if request.REQUEST.has_key('province_id') :
            data = data.filter(province__id = int(request.REQUEST['province_id']))
            
        stats = {'count': data.count(), 'records': data}
        
        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:10]
            stats['records'] = data
                
        return stats

class HospitalHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Hospital
    fields=('id','name','code', 'district_id')

    def read(self, request, code = None):
        
        hospitals = Hospital.objects.all()
        if code:
            data = hospitals.filter(code = code)
            
        else:
            data = hospitals
            
        stats = {'count': data.count(), 'records': data}
            
        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:10]
            stats['records'] = data
        
        return stats	

class HealthCentreHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = HealthCentre
    fields=('id','name','code', 'province_id','district_id')

    def read(self, request, code = None):
        data = {}
        healthcentres = HealthCentre.objects.all().exclude(name = 'TEST')
        if code:
            data = healthcentres.filter(code = code)
        else:
            data = healthcentres
        
        if request.REQUEST.has_key('province_id') :
            data = data.filter(province__id = int(request.REQUEST['province_id']))
        if request.REQUEST.has_key('district_id') :
            data = data.filter(district__id = int(request.REQUEST['district_id']))
            
        stats = {'count': data.count(), 'records': data }
        
        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:10]
            stats['records'] = data
                
        return stats

class SectorHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Sector
    fields=('id','name','code', 'district_id')

    def read(self, request, code = None):
        
        sectors = Sector.objects.all()
        if code:
            data = sectors.filter(code = code)
            
        else:
            data = sectors
            
        stats = {'count': data.count(), 'records': data}
            
        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:10]
            stats['records'] = data
                
        return stats	

class CellHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Cell
    fields=('id','name','code', 'sector_id')

    def read(self, request, code = None):
        
        cells = Cell.objects.all()
        if code:
            data = cells.filter(code = code)
            
        else:
            data = cells
            
        stats = {'count': data.count(), 'records': data}
        
        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:10]
            stats['records'] = data
                
        return stats	

class VillageHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Village
    fields=('id','name','code', 'cell_id')

    def read(self, request, code = None):
        
        villages = Village.objects.all()
        if code:
            data = villages.filter(code = code)
            
        else:
            data = villages
            
        stats = {'count': data.count(), 'records': data}
            
        if request.REQUEST.has_key('start') and request.REQUEST.has_key('limit'):
            start,limit = int(request.REQUEST['start']),int(request.REQUEST['start'])+int(request.REQUEST['limit'])
            data = data[start:limit]
            
        else:
            data = data[0:50]
            stats['records'] = data
            
        return stats			
