#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from django.contrib.auth.models import Group, User
from django.db import models
from rapidsmsrw1000.apps.api.utils import *
from rapidsmsrw1000.apps.api.locations.models import *
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator


def get_phone_number_validators(top_level_location = LocationType.objects.filter(top_level = True) ):
    
    if top_level_location.exists():
        top_level_location = top_level_location[0]
        return {'min': len(top_level_location.international_phone_code) + top_level_location.phone_number_length , \
                                        'max': len(top_level_location.international_phone_code) + top_level_location.phone_number_length }   
    return {'min': 13, 'max': 13}

__TELEPHONE_VALIDATOR__ = get_phone_number_validators()



class Provider(models.Model):
    """ Whoever registered in the system is host in this table referenced with his user accounts """
    
    user = models.ForeignKey(User)
    telephone = models.CharField( max_length = __TELEPHONE_VALIDATOR__['max'], validators = [RegexValidator(regex='^.{%d}$' % __TELEPHONE_VALIDATOR__['max'],\
                                         message='Length has to be %d' % __TELEPHONE_VALIDATOR__['max'], code='nomatch')], null=True, unique = True)
    
    working_level = models.ForeignKey(LocationType)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField()  
    ##START OF LINK TO LOCATION TYPES


    ##START OF NATION LINK
    nation = models.ForeignKey(Nation)
    ##END OF NATION LINK

    ##START OF PROVINCE LINK
    province = models.ForeignKey(Province)
    ##END OF PROVINCE LINK

    ##START OF DISTRICT LINK
    district = models.ForeignKey(District)
    ##END OF DISTRICT LINK

    ##START OF HEALTH_FACILITY LINK
    health_facility = models.ForeignKey(HealthFacility)
    ##END OF HEALTH_FACILITY LINK
    ##END OF LINK TO LOCATION TYPES
    
    class Meta:
        verbose_name = "System User"
        permissions = (
            ('can_view', 'Can view'),
        )

def ensure_new_location(sender, **kwargs):
    if kwargs.get('created', False):
        location = kwargs.get('instance')
        model_object = Provider()
        app_label = model_object._meta.app_label
        model_name = model_object._meta.object_name
        location_type = location.name
        print app_label, model_name, location_type
        loc_c = link_model_with(app_label, model_name, location_type)
        if loc_c:    return True
        else:   return False    
    
post_save.connect(ensure_new_location, sender = LocationType)    
