#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com/zigdidier@gmail.com
##

from django.contrib import admin
from .models import *

class SMSReportAdmin(admin.ModelAdmin):                                                        
    list_filter = ()                                                        
    exportable_fields = ( 'keyword', 'description', 'field_separator', 'in_use' , 'case_sensitive', 'syntax_regex', 'created', )                                                        
    search_fields = ( 'keyword', 'description', 'field_separator', 'in_use' , 'case_sensitive', 'syntax_regex', 'created', )                                                        
    list_display = ( 'keyword', 'description', 'field_separator', 'in_use' , 'case_sensitive', 'syntax_regex', 'created', )                                                    
    actions = (export_model_as_csv, export_model_as_excel)
    
class SMSReportFieldAdmin(admin.ModelAdmin):                                                        
    list_filter = ('sms_report',)                                                        
    exportable_fields = ('sms_report', 'prefix', 'key', 'description', 'type_of_value', 'upper_case', 'lower_case', 'minimum_value', 'maximum_value', 
                            'minimum_length', 'maximum_length', 'position_after_sms_keyword', 'depends_on_value_of', 'dependency', 
                        'allowed_value_list', 'only_allow_one', 'required', 'created', 
                        )                                                        
    search_fields = ('key', 'description', 'prefix', 'type_of_value' , 'position_after_sms_keyword', 'required', 'created', )                                                                 
    list_display = ('sms_report', 'prefix', 'key', 'description', 'type_of_value', 'upper_case', 'lower_case', 'minimum_value', 'maximum_value', 
                            'minimum_length', 'maximum_length', 'position_after_sms_keyword', 'depends_on_value_of', 'dependency', 
                        'allowed_value_list', 'only_allow_one', 'required', 'created', 
                        ) 
    actions = (export_model_as_csv, export_model_as_excel)  
    
class SMSLanguageAdmin(admin.ModelAdmin):                                                        
    list_filter = ()                                                        
    exportable_fields = ('name', 'iso_639_1_code', 'description', 'created', )                                                        
    search_fields = ('name', 'iso_639_1_code', 'description', 'created', )                                                           
    list_display = ('name', 'iso_639_1_code', 'description', 'created', )                                                       
    actions = (export_model_as_csv, export_model_as_excel)
    
class SMSMessageAdmin(admin.ModelAdmin):                                                        
    list_filter = ('destination', 'message_type', 'sms_report', 'sms_report_field',)                                                        
    exportable_fields = ('message_type', 'sms_report', 'sms_report_field', 'created', )                                                        
    search_fields = ('message_type', 'sms_report', 'sms_report_field', 'created', )                                                                   
    list_display = ('message_type', 'sms_report', 'sms_report_field', 'created', )                                                               
    actions = (export_model_as_csv, export_model_as_excel)

class SMSReportDBConstraintAdmin(admin.ModelAdmin):                                                        
    list_filter = ()                                                        
    exportable_fields = ( 'sms_report', 'sms_report_field', 'constraint', 'minimum_period_value', 'maximum_period_value' , 'refer_sms_report',
                             'refer_sms_report_field', 'created', )                                                        
    search_fields = ( 'sms_report', 'sms_report_field', 'constraint', 'minimum_period_value', 'maximum_period_value' , 'refer_sms_report',
                             'refer_sms_report_field', 'created', )                                   
    list_display = ( 'sms_report', 'sms_report_field', 'constraint', 'minimum_period_value', 'maximum_period_value' , 'refer_sms_report',
                             'refer_sms_report_field', 'created', )                               
    actions = (export_model_as_csv, export_model_as_excel)     

admin.site.register(SMSReport, SMSReportAdmin)
admin.site.register(SMSReportField, SMSReportFieldAdmin)
admin.site.register(SMSLanguage, SMSLanguageAdmin)
admin.site.register(SMSMessage, SMSMessageAdmin)


##Start of SMSReportTrack

class SMSReportTrackAdmin(admin.ModelAdmin):                                                        
    list_filter = ('keyword',  )                                                        
    exportable_fields = ('keyword',  'aa_key', 'af_key', 'al_key', 'anc2_key', 'anc2_date_key', 'anc3_key', 'anc4_key', 'anc_date_key', 'ap_key', 'at_key', 'bf1_key', 'bo_key', 'cbf_key', 'cd_key', 'ch_key', 'child_height_key', 'child_number_key', 'child_weight_key', 'ci_key', 'cl_key', 'cm_key', 'co_key', 'cs_key', 'cw_key', 'date_of_birth_key', 'date_of_emergency_key', 'db_key', 'di_key', 'ds_key', 'ebf_key', 'fe_key', 'fp_key', 'gi_key', 'gravidity_key', 'gs_key', 'hd_key', 'he_key', 'ho_key', 'hp_key', 'hw_key', 'hy_key', 'ib_key', 'ja_key', 'kx_key', 'la_key', 'lmp_key', 'lz_key', 'ma_key', 'mc_key', 'md_key', 'mother_height_key', 'mother_phone_key', 'mother_weight_key', 'ms_key', 'mu_key', 'muac_key', 'mw_key', 'na_key', 'nb_key', 'nbc1_key', 'nbc2_key', 'nbc3_key', 'nbc4_key', 'nbc5_key', 'nd_key', 'nh_key', 'nid_key', 'np_key', 'nr_key', 'ns_key', 'nt_key', 'nv_key', 'oe_key', 'oi_key', 'ol_key', 'or_key', 'pa_key', 'parity_key', 'pc_key', 'pm_key', 'pnc1_key', 'pnc2_key', 'pnc3_key', 'pr_key', 'ps_key', 'pt_key', 'rb_key', 'rm_key', 'sa_key', 'sb_key', 'sc_key', 'sl_key', 'to_key', 'tr_key', 'un_key', 'v1_key', 'v2_key', 'v3_key', 'v4_key', 'v5_key', 'v6_key', 'vc_key', 'vi_key', 'vo_key', 'yg_key', 'yj_key',  )                                                        
    search_fields = ('keyword',  'aa_key', 'af_key', 'al_key', 'anc2_key', 'anc2_date_key', 'anc3_key', 'anc4_key', 'anc_date_key', 'ap_key', 'at_key', 'bf1_key', 'bo_key', 'cbf_key', 'cd_key', 'ch_key', 'child_height_key', 'child_number_key', 'child_weight_key', 'ci_key', 'cl_key', 'cm_key', 'co_key', 'cs_key', 'cw_key', 'date_of_birth_key', 'date_of_emergency_key', 'db_key', 'di_key', 'ds_key', 'ebf_key', 'fe_key', 'fp_key', 'gi_key', 'gravidity_key', 'gs_key', 'hd_key', 'he_key', 'ho_key', 'hp_key', 'hw_key', 'hy_key', 'ib_key', 'ja_key', 'kx_key', 'la_key', 'lmp_key', 'lz_key', 'ma_key', 'mc_key', 'md_key', 'mother_height_key', 'mother_phone_key', 'mother_weight_key', 'ms_key', 'mu_key', 'muac_key', 'mw_key', 'na_key', 'nb_key', 'nbc1_key', 'nbc2_key', 'nbc3_key', 'nbc4_key', 'nbc5_key', 'nd_key', 'nh_key', 'nid_key', 'np_key', 'nr_key', 'ns_key', 'nt_key', 'nv_key', 'oe_key', 'oi_key', 'ol_key', 'or_key', 'pa_key', 'parity_key', 'pc_key', 'pm_key', 'pnc1_key', 'pnc2_key', 'pnc3_key', 'pr_key', 'ps_key', 'pt_key', 'rb_key', 'rm_key', 'sa_key', 'sb_key', 'sc_key', 'sl_key', 'to_key', 'tr_key', 'un_key', 'v1_key', 'v2_key', 'v3_key', 'v4_key', 'v5_key', 'v6_key', 'vc_key', 'vi_key', 'vo_key', 'yg_key', 'yj_key',  )                                                        
    list_display = ('keyword',  'aa_key', 'af_key', 'al_key', 'anc2_key', 'anc2_date_key', 'anc3_key', 'anc4_key', 'anc_date_key', 'ap_key', 'at_key', 'bf1_key', 'bo_key', 'cbf_key', 'cd_key', 'ch_key', 'child_height_key', 'child_number_key', 'child_weight_key', 'ci_key', 'cl_key', 'cm_key', 'co_key', 'cs_key', 'cw_key', 'date_of_birth_key', 'date_of_emergency_key', 'db_key', 'di_key', 'ds_key', 'ebf_key', 'fe_key', 'fp_key', 'gi_key', 'gravidity_key', 'gs_key', 'hd_key', 'he_key', 'ho_key', 'hp_key', 'hw_key', 'hy_key', 'ib_key', 'ja_key', 'kx_key', 'la_key', 'lmp_key', 'lz_key', 'ma_key', 'mc_key', 'md_key', 'mother_height_key', 'mother_phone_key', 'mother_weight_key', 'ms_key', 'mu_key', 'muac_key', 'mw_key', 'na_key', 'nb_key', 'nbc1_key', 'nbc2_key', 'nbc3_key', 'nbc4_key', 'nbc5_key', 'nd_key', 'nh_key', 'nid_key', 'np_key', 'nr_key', 'ns_key', 'nt_key', 'nv_key', 'oe_key', 'oi_key', 'ol_key', 'or_key', 'pa_key', 'parity_key', 'pc_key', 'pm_key', 'pnc1_key', 'pnc2_key', 'pnc3_key', 'pr_key', 'ps_key', 'pt_key', 'rb_key', 'rm_key', 'sa_key', 'sb_key', 'sc_key', 'sl_key', 'to_key', 'tr_key', 'un_key', 'v1_key', 'v2_key', 'v3_key', 'v4_key', 'v5_key', 'v6_key', 'vc_key', 'vi_key', 'vo_key', 'yg_key', 'yj_key',  )                                                    
    actions = (export_model_as_csv, export_model_as_excel)                        

admin.site.register(SMSReportTrack, SMSReportTrackAdmin)
##End of SMSReportTrack
