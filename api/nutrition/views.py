#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count

from rapidsmsrw1000.apps.api.nutrition.models import *
from rapidsmsrw1000.apps.utils import *

### START OF HELPERS
@permission_required('ubuzima.can_view')
def paginated(req, data):
    req.base_template = "webapp/layout.html"
    paginator = Paginator(data, 20)

    try: page = int(req.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        data = paginator.page(page)
    except (InvalidPage, EmptyPage):
        data = paginator.page(paginator.num_pages)

    return data


def n_months_ago(n_months, given_date):
    return given_date - datetime.timedelta(n_months * 30.4375)

@permission_required('nutrition.can_view')
def index(req,**flts):
    req.base_template = "webapp/layout.html"
    
    return render_to_response("nutrition/index.html", context_instance=RequestContext(req))

@permission_required('nutrition.can_view')
def statistics(req,**flts):
    req.base_template = "webapp/layout.html"
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)} 
    
    
    return render_to_response("nutrition/statistics.html", {'filters':filters}, context_instance=RequestContext(req))

@permission_required('nutrition.can_view')
def cbn(req,**flts):
    req.base_template = "webapp/layout.html"
    filters = {'period':default_period(req),
             'location':default_location(req),
             'province':default_province(req),
             'district':default_district(req)} 
    
    
    return render_to_response("nutrition/cbn.html", {'filters':filters}, context_instance=RequestContext(req))

@permission_required('nutrition.can_view')
def cbnindicator(request, key, **flts):
    
    request.base_template = "webapp/layout.html"
    
    filters = {'period':default_period(request),
             'location':default_location(request),
             'province':default_province(request),
             'district':default_district(request)} 
    start, end = filters['period']['start'], filters['period']['end'] 
    #print start,end
    
    loc_f = {}
    
    if request.REQUEST.has_key('province'):
        loc_f['province__id'] = int(request.REQUEST['province'])
    if request.REQUEST.has_key('district'):
        loc_f['district__id'] = int(request.REQUEST['district'])
    if request.REQUEST.has_key('location'):
        loc_f['health_centre__id'] = int(request.REQUEST['location'])
                
    #print loc_f
    data = None
    type = None
        
    if key == 'mother_height':
        pregs = Pregnancy.objects.filter(expected_delivery_date__gte = start, **loc_f)  
        pregs_less_150cm = pregs.filter(height__lt = 150)
        data = {'key': 'mother_height','desc': "Proportion of pregnant women with height <150cm at 1st ANC", 'data': pregs_less_150cm}
        type = 'PREGNANCY'
        
    elif key == 'mother_weight':
        pregs = Pregnancy.objects.filter(expected_delivery_date__gte = start, **loc_f)
        pregs_bmi_less_18_5 = pregs.filter(bmi_anc1__lt = 18.5)
        data = {'key': 'mother_weight', 'desc': "Proportion of pregnant women with BMI <18.5 at 1st ANC", 'data': pregs_bmi_less_18_5}
        type = 'PREGNANCY'
        
    elif key == 'child_weight':
        births = Birth.objects.filter(date_of_birth__gte = start, date_of_birth__lte = end, **loc_f)        
        birth_weight_less_2_5 = births.filter(weight__lt = 2.5)
        data = {'key': 'child_weight','desc': "Proportion of live births with birth weight below 2.5kg", 'data': birth_weight_less_2_5}
        type = 'BIRTH'
    
    elif key == 'te':
        births = Birth.objects.filter(date_of_birth__gte = start, date_of_birth__lte = end, **loc_f)
        birth_not_premature = births.filter(child__is_premature = False)
        data = {'key': 'te','desc': "Proportion of live births born at term", 'data': birth_not_premature }
        type = 'BIRTH'
        
    elif key == 'ebf1':
        births = Birth.objects.filter(date_of_birth__gte = start, date_of_birth__lte = end, **loc_f)
        birth_bf1 = births.filter(breastfeeding = 'bf1')
        data = {'key': 'ebf1','desc':"Proportion of live births breastfed within 1st hour", 'data': birth_bf1 }
        type = 'BIRTH'
    
    elif key == 'child_height_6':
        children_6_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(6, start),  date_of_birth__lte = n_months_ago(6, end), **loc_f)
        cbn_6_months_old = ChildNutrition.objects.filter(child__in = children_6_months_old, age_in_months = 6, **loc_f)                
        heighted_6_months_old = cbn_6_months_old.exclude(height = None)
        data = {'key':'child_height_6' , 'desc': 'Proportion of children whose height is measured at 6 months old', 'data': heighted_6_months_old}
        type = "CBN"
        
    elif key == 'child_weight_6':
        children_6_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(6, start),  date_of_birth__lte = n_months_ago(6, end), **loc_f)
        cbn_6_months_old = ChildNutrition.objects.filter(child__in = children_6_months_old, age_in_months = 6, **loc_f)                
        weighted_6_months_old = cbn_6_months_old.exclude(weight = None)
        data = {'key': 'child_weight_6', 'desc': 'Proportion of children whose weight is measured at 6 months old', 'data': weighted_6_months_old}
        type = "CBN"
        
    elif key == 'child_stunted_6':
        children_6_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(6, start),  date_of_birth__lte = n_months_ago(6, end), **loc_f)
        cbn_6_months_old = ChildNutrition.objects.filter(child__in = children_6_months_old, age_in_months = 6, **loc_f)                
        stunted_6_months_old =  cbn_6_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
        data = {'key': 'child_stunted_6', 'desc': 'Proportion of U2 children stunted at 6 months of age', 'data': stunted_6_months_old }
        type = "CBN"
        
    elif key == 'child_wasted_6':
        children_6_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(6, start),  date_of_birth__lte = n_months_ago(6, end), **loc_f)
        cbn_6_months_old = ChildNutrition.objects.filter(child__in = children_6_months_old, age_in_months = 6, **loc_f)
        wasted_6_months_old =  cbn_6_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
        data = {'key': 'child_wasted_6', 'desc': 'Proportion of U2 children wasted at 6 months of age', 'data': wasted_6_months_old}
        type = "CBN"
        
    elif key == 'child_underweight_6':
        children_6_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(6, start),  date_of_birth__lte = n_months_ago(6, end), **loc_f)
        cbn_6_months_old = ChildNutrition.objects.filter(child__in = children_6_months_old, age_in_months = 6, **loc_f)                
        underweight_6_months_old =  cbn_6_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
        data = {'key': 'child_underweight_6', 'desc': 'Proportion of U2 children underweight at 6 months of age', 'data': underweight_6_months_old}
        type = "CBN"
         
    elif key == 'child_height_9':
        children_9_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(9, start),  date_of_birth__lte = n_months_ago(9, end), **loc_f)
        cbn_9_months_old = ChildNutrition.objects.filter(child__in = children_9_months_old, age_in_months = 9, **loc_f)
        heighted_9_months_old = cbn_9_months_old.exclude(height = None)
        data = {'key':'child_height_9' , 'desc': 'Proportion of children whose height is measured at 9 months old', 'data': heighted_9_months_old}
        type = "CBN"
        
        
    elif key == 'child_weight_9':
        children_9_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(9, start),  date_of_birth__lte = n_months_ago(9, end), **loc_f)
        cbn_9_months_old = ChildNutrition.objects.filter(child__in = children_9_months_old, age_in_months = 9, **loc_f)
        weighted_9_months_old = cbn_9_months_old.exclude(weight = None)
        data = {'key': 'child_weight_9', 'desc': 'Proportion of children whose weight is measured at 9 months old', 'data': weighted_9_months_old }
        type = "CBN"
    
        
    elif key == 'child_stunted_9':
        children_9_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(9, start),  date_of_birth__lte = n_months_ago(9, end), **loc_f)
        cbn_9_months_old = ChildNutrition.objects.filter(child__in = children_9_months_old, age_in_months = 9, **loc_f)
        stunted_9_months_old =  cbn_9_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
        data = {'key': 'child_stunted_9', 'desc': 'Proportion of U2 children stunted at 9 months of age', 'data': stunted_9_months_old}
        type = "CBN"
        
    elif key == 'child_wasted_9':
        children_9_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(9, start),  date_of_birth__lte = n_months_ago(9, end), **loc_f)
        cbn_9_months_old = ChildNutrition.objects.filter(child__in = children_9_months_old, age_in_months = 9, **loc_f)
        wasted_9_months_old =  cbn_9_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
        data = {'key': 'child_wasted_9', 'desc': 'Proportion of U2 children wasted at 9 months of age', 'data': wasted_9_months_old}
        type = "CBN"
        
        
    elif key == 'child_underweight_9':
        children_9_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(9, start),  date_of_birth__lte = n_months_ago(9, end), **loc_f)
        cbn_9_months_old = ChildNutrition.objects.filter(child__in = children_9_months_old, age_in_months = 9, **loc_f)
        underweight_9_months_old =  cbn_9_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
        data = {'key': 'child_underweight_9', 'desc': 'Proportion of U2 children underweight at 9 months of age', 'data': underweight_9_months_old}
        type = "CBN"
          
        
    elif key == 'child_height_18':
        children_18_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(18, start),  date_of_birth__lte = n_months_ago(18, end), **loc_f)
        cbn_18_months_old = ChildNutrition.objects.filter(child__in = children_18_months_old, age_in_months = 18, **loc_f)
        heighted_18_months_old = cbn_18_months_old.exclude(height = None)
        data = {'key':'child_height_18' , 'desc': 'Proportion of children whose height is measured at 18 months old', 'data': heighted_18_months_old}
        type = "CBN"
        
        
    elif key == 'child_weight_18':
        children_18_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(18, start),  date_of_birth__lte = n_months_ago(18, end), **loc_f)
        cbn_18_months_old = ChildNutrition.objects.filter(child__in = children_18_months_old, age_in_months = 18, **loc_f)
        weighted_18_months_old = cbn_18_months_old.exclude(weight = None)
        data = {'key': 'child_weight_18', 'desc': 'Proportion of children whose weight is measured at 18 months old', 'data': weighted_18_months_old}
        type = "CBN"
        
        
    elif key == 'child_stunted_18':
        children_18_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(18, start),  date_of_birth__lte = n_months_ago(18, end), **loc_f)
        cbn_18_months_old = ChildNutrition.objects.filter(child__in = children_18_months_old, age_in_months = 18, **loc_f)
        stunted_18_months_old =  cbn_18_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
        data = {'key': 'child_stunted_18', 'desc': 'Proportion of U2 children stunted at 18 months of age', 'data': stunted_18_months_old}
        type = "CBN"
        
        
    elif key == 'child_wasted_18':
        children_18_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(18, start),  date_of_birth__lte = n_months_ago(18, end), **loc_f)
        cbn_18_months_old = ChildNutrition.objects.filter(child__in = children_18_months_old, age_in_months = 18, **loc_f)
        wasted_18_months_old =  cbn_18_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
        data = {'key': 'child_wasted_18', 'desc': 'Proportion of U2 children wasted at 18 months of age', 'data': wasted_18_months_old}
        type = "CBN"
        
        
    elif key == 'child_underweight_18':
        children_18_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(18, start),  date_of_birth__lte = n_months_ago(18, end), **loc_f)
        cbn_18_months_old = ChildNutrition.objects.filter(child__in = children_18_months_old, age_in_months = 18, **loc_f)
        underweight_18_months_old =  cbn_18_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
        data = {'key': 'child_underweight_18', 'desc': 'Proportion of U2 children underweight at 18 months of age', 'data': underweight_18_months_old}
        type = "CBN"
         
        
    elif key == 'child_height_24':
        children_24_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(24, start),  date_of_birth__lte = n_months_ago(24, end), **loc_f)
        cbn_24_months_old = ChildNutrition.objects.filter(child__in = children_24_months_old, age_in_months = 24, **loc_f)
        heighted_24_months_old = cbn_24_months_old.exclude(height = None)
        data = {'key':'child_height_24' , 'desc': 'Proportion of children whose height is measured at 24 months old', 'data': heighted_24_months_old}
        type = "CBN"
        
        
    elif key == 'child_weight_24':
        children_24_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(24, start),  date_of_birth__lte = n_months_ago(24, end), **loc_f)
        cbn_24_months_old = ChildNutrition.objects.filter(child__in = children_24_months_old, age_in_months = 24, **loc_f)
        weighted_24_months_old = cbn_24_months_old.exclude(weight = None)
        data = {'key': 'child_weight_24', 'desc': 'Proportion of children whose weight is measured at 24 months old', 'data': weighted_24_months_old}
        type = "CBN"
        
        
    elif key == 'child_stunted_24':
        children_24_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(24, start),  date_of_birth__lte = n_months_ago(24, end), **loc_f)
        cbn_24_months_old = ChildNutrition.objects.filter(child__in = children_24_months_old, age_in_months = 24, **loc_f)
        stunted_24_months_old =  cbn_24_months_old.filter(length_height_for_age__lt = -2 ).exclude(length_height_for_age = None)
        data = {'key': 'child_stunted_24', 'desc': 'Proportion of U2 children stunted at 24 months of age', 'data': stunted_24_months_old}
        type = "CBN"
        
    
    elif key == 'child_wasted_24':
        children_24_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(24, start),  date_of_birth__lte = n_months_ago(24, end), **loc_f)
        cbn_24_months_old = ChildNutrition.objects.filter(child__in = children_24_months_old, age_in_months = 24, **loc_f)
        wasted_24_months_old =  cbn_24_months_old.filter( weight_for_length__lt = -2 ).exclude(weight_for_length = None)
        data = {'key': 'child_wasted_24', 'desc': 'Proportion of U2 children wasted at 24 months of age', 'data': wasted_24_months_old}
        type = "CBN"
    
    elif key == 'child_underweight_24':
        children_24_months_old = Child.objects.filter( date_of_birth__gte = n_months_ago(24, start),  date_of_birth__lte = n_months_ago(24, end), **loc_f)
        cbn_24_months_old = ChildNutrition.objects.filter(child__in = children_24_months_old, age_in_months = 24, **loc_f)
        underweight_24_months_old =  cbn_24_months_old.filter( weight_for_age__lt = -2 ).exclude(weight_for_age = None)
        data = {'key': 'child_underweight_24', 'desc': 'Proportion of U2 children underweight at 24 months of age', 'data': underweight_24_months_old}
        type = "CBN"
                
    
    return render_to_response("nutrition/indicator.html", {'filters':filters, 'records': paginated(request, data['data']), 'data': data, 'type': type}, context_instance=RequestContext(request))
