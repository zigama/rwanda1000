#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from django.contrib import admin
from .models import *

class LocationTypeAdmin(admin.ModelAdmin):
	list_filter = ()                                                        
	exportable_fields = ('name', 'short_name', 'international_phone_code', 'phone_number_length', 'top_level', 'created' )                                                        
	search_fields = ('name', 'short_name', 'international_phone_code', 'phone_number_length', 'top_level', 'created' )                                                        
	list_display = ('name', 'short_name', 'international_phone_code', 'phone_number_length', 'top_level', 'created' )                                                    
	actions = (export_model_as_csv, export_model_as_excel)  
	
admin.site.register(LocationType, LocationTypeAdmin)

##Start of Nation
class NationAdmin(admin.ModelAdmin):                                                        
	list_filter = ()                                                        
	exportable_fields = ('name', 'code', )                                                        
	search_fields = ('name','code')                                                        
	list_display = ('name','code', )                                                    
	actions = (export_model_as_csv, export_model_as_excel)                        

admin.site.register(Nation, NationAdmin)
##End of Nation

##Start of Province
class ProvinceAdmin(admin.ModelAdmin):                                                        
	list_filter = ('nation', )                                                        
	exportable_fields = ('name', 'code', 'nation', )                                                        
	search_fields = ('name','code')                                                        
	list_display = ('name','code', 'nation', )                                                    
	actions = (export_model_as_csv, export_model_as_excel)                        

admin.site.register(Province, ProvinceAdmin)
##End of Province

##Start of District
class DistrictAdmin(admin.ModelAdmin):                                                        
	list_filter = ('nation', 'province', )                                                        
	exportable_fields = ('name', 'code', 'nation', 'province', )                                                        
	search_fields = ('name','code')                                                        
	list_display = ('name','code', 'nation', 'province', )                                                    
	actions = (export_model_as_csv, export_model_as_excel)                        

admin.site.register(District, DistrictAdmin)
##End of District

##Start of HealthFacility

class HealthFacilityAdmin(admin.ModelAdmin):                                                        
	list_filter = ('nation', 'province', 'district', )                                                        
	exportable_fields = ('name', 'code', 'nation', 'province', 'district', )                                                        
	search_fields = ('name','code')                                                        
	list_display = ('name','code', 'nation', 'province', 'district', )                                                    
	actions = (export_model_as_csv, export_model_as_excel)                    

admin.site.register(HealthFacility, HealthFacilityAdmin)
##End of HealthFacility
