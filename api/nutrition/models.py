#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

##
##
## @author UWANTWALI ZIGAMA Didier
## d.zigama@pivotaccess.com
##

import datetime
from django.db import models
from rapidsmsrw1000.apps.chws.models import Nation, Province, District, Hospital, HealthCentre, Sector, Cell, Village, Reporter
from rapidsmsrw1000.apps.ubuzima.models import Reporter, Report, FieldType, Field, Patient
from pygrowup import helpers, Calculator

BIRTH_LOCATION_PATTERN = "hp|or|ho|cl"
BIRTH_SYMPTOMS_PATTERN = "ci|cm|rb|af|np|sb|ib|db|pm"
BIRTH_GENDER_PATTERN = "bo|gi"
BIRTH_BREASTFEEDING_PATTERN = "nb|bf1"

CHI_SYMPTOMS_PATTERN = "sb|rb|np|af|ci|cm|ib|db|pm"
CHI_VACCINATION_RECEIVED_PATTERN = "v1|v2|v3|v4|v5|v6"
CHI_VACCINATION_STATUS_PATTERN = "vc|vi|nv"
CHI_LOCATION_PATTERN = "hp|ho|cl"

CBN_BREASTFEEDING_PATTERN = "ebf|nb|cbf"

BOY        = 'bo'
GIRL       = 'gi'
GENDER_CHOICES        = ( (BOY, "Boy"),
                    (GIRL, "Girl"))

BIRTH_SYMPTOMS = {'sb': 'Stillborn', 'rb': 'Rapid Breathing', 'np': 'No Problem', 'af': 'Abnormal Fontinel', 'ci': 'Cord Infection',\
                  'cm': 'Congenital Malformation', 'ib': 'Cleft Palate/Lip', 'db': 'Children Living with Disability', 'pm': 'Premature'}


DAYS_ANC3 = 60
DAYS_ANC4 = 14
DAYS_SUP_EDD = 30
DAYS_EDD = 7
DAYS_ON_THE_DOT = 0
DAYS_WEEK_LATER = -7

PREGNANCY_LOCATION_PATTERN = "hp|cl"
PREVIOUS_SYMPTOMS_PATTERN = "gs|mu|hd|rm|ol|yg|nr|kx|yj|lz"
CURRENT_SYMPTOMS_PATTERN = "vo|pc|oe|ns|ma|ja|fp|fe|ds|di|sa|rb|np|hy|ch|af"
TOILET_PATTERN = "to|nt"
HANDWASHING_PATTERN = "hw|nh"

PREGNANCY_LOCATION = {'cl': 'At Clinic', 'hp': 'At Hospital'}

PREVIOUS_SYMPTOMS = {'gs': 'Previous Obstetric Surgery', 'mu': 'Multiples', 'hd': 'Previous Home Delivery', 'rm': 'Repetitive Miscarriage',\
                     'ol': 'Old Age (over 35)', 'yg': 'Young Age (Under 18)', 'nr': 'No Previous Risks', 'kx': 'Previous Convulsion', \
                     'yj': 'Previous Serious Conditions', 'lz': 'Previous Hemorrhaging/Bleeding'}

CURRENT_SYMPTOMS = {'vo': 'Vomiting', 'pc': 'Pneumonia', 'oe': 'Edema', 'ns': 'Neck Stiffness', 'ma': 'Malaria', 'ja': 'Jaundice',\
                     'fp': 'Fraccid Paralysis', 'fe': 'Fever', 'ds': 'Chronic Disease', 'di': 'Diarrhea', 'sa': 'Severe Anemia', \
                     'rb': 'Rapid Breathing', 'np': 'No Problem', 'hy': 'Hypothermia', 'ch': 'Coughing', 'af': 'Abnormal Fontinel'}

TOILET = {'to': 'Has Toilet', 'nt': 'Has no Toilet'}


class Child(models.Model):
    
    """
    This keeps track of all child in the system. Each child registered once, at the receipt of a birth report.
    We need to mention that if the mother has never been reported to be pregnancy so there is no way to allow a child registration.
     
    """
    
    mother = models.ForeignKey(Patient)
    chw = models.ForeignKey(Reporter)    
    
    nation = models.ForeignKey(Nation, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    sector = models.ForeignKey(Sector, null=True, blank=True)
    cell = models.ForeignKey(Cell, null=True, blank=True)
    village    = models.ForeignKey(Village, null=True, blank=True)
    health_centre = models.ForeignKey(HealthCentre, null=True, blank=True)
    referral_hospital = models.ForeignKey(Hospital, null=True, blank=True)
    
    date_of_birth = models.DateField(null=True, blank = True) ## Child date of birth
    child_number = models.CharField(max_length = 2, blank=True, null= True)
    gender = models.CharField(max_length = 2, blank=True, null= True, choices= GENDER_CHOICES, help_text="Select the gender")
    birth_symptoms = models.CharField(max_length = 100, blank=True, null=True)
    birth_location = models.CharField(max_length = 2, blank=True, null= True)
    birth_breastfeeding = models.CharField(max_length = 3, blank=True, null= True)
    birth_weight = models.FloatField(blank=True, null=True)
    
    is_premature = models.BooleanField(default=False)
    is_dead = models.BooleanField(default=False)
    status = models.CharField(max_length = 100, blank=True, null= True)
    
    def __int__(self):
        return self.id

    def __unicode__(self):
        return "Child: %d" % self.id
    
    def _get_details(self):
        ans = []
        try:    bir = self.birth_set.all()
        except: pass
        try:    chi = self.childhealth_set.all()
        except: pass
        try:    cbn = self.childnutrition_set.all()
        except: pass
        for c in bir: ans.append(c)
        for c in chi: ans.append(c)
        for c in cbn: ans.append(c)
        
        return ans
        

    def _get_history(self):
        bir = self.birth_set.all()
        chi = self.childhealth_set.all()
        cbn = self.childnutrition_set.all()
        history = []
        ans = []
        
        for c in bir: ans.append(c)
        for c in chi: ans.append(c)
        for c in cbn: ans.append(c)
        for an in ans: history.append({'age': an.age_in_months, 'weight' : an.weight, 'id': an.child.id })

        return history
    
    def _get_valid_gender(self):
        try:
            sex = ""
            if self.gender.lower() == 'gi' :
                sex = 'Female'
            elif  self.gender.lower() == 'bo':
                sex = "Male"            
            valid_gender = helpers.get_good_sex( sex )
            return valid_gender
        except:
            return None
    
    def _get_status(self):
        
        bir = chi = cbn = None
        status = ""
        cg = Calculator(adjust_height_data=False, adjust_weight_scores=False)
        try:
            bir = self.birth_set.all().latest('age_in_months')
            chi = self.childhealth_set.all().latest('age_in_months')
            cbn = self.childnutrition_set.all().latest('age_in_months')
        except Exception, e: pass
        
        history = bir
                        
        try:
            if chi:
                if history:
                    if chi.age_in_months > history.age_in_months: history = chi
                else:
                    history = chi
        except Exception, e:    pass
        
        try:
            if cbn:
                if history:
                    if cbn.age_in_months > history.age_in_months: history = cbn
                else:
                    history = cbn
        except Exception, e:    pass
        
        try:
            wfa = cg.zscore_for_measurement('wfa', history.weight, history.age_in_months, self.valid_gender)
            if wfa <= -2: status += " UNDERWEIGHT "
        except Exception, e: pass
        try: 
            lhfa = cg.zscore_for_measurement('lhfa', history.height , history.age_in_months, self.valid_gender)
            if lhfa <= -2: status += " STUNTING "
        except Exception, e: pass
        try:
            wfh = cg.zscore_for_measurement('wfh', history.weight, history.age_in_months, self.valid_gender, history.height)
            if wfh <= -2: status += " WASTING "
        except Exception, e: pass        
        
        if status == "":
            self.status = "NORMAL"
        else:
            self.status = status
            
        self.save()
        
        return status
        
    
    class Meta:

        # define a permission for this app to use the @permission_required
        # in the admin's auth section, we have a group called 'manager' whose
        # users have this permission -- and are able to see this section
        permissions = (
            ("can_view", "Can view"),
        )
        unique_together = ('mother', 'child_number', 'date_of_birth')

    history    =   property(_get_history)
    details    =   property(_get_details)
    cstatus    =   property(_get_status)
    valid_gender = property(_get_valid_gender)
    


class Birth(models.Model):
    """
    It has to be clear if someone can report a birth report without previously reported pregnancy.
    
    This model help us to store any new birth coming in the system, this the best way to be able to generate delivery statistics 
    independently of any kind of reports in the system
    
    Refer to Birth Report Structure, and make it reasonable here
    Easily store and easily retrieved
    
    """
    
    mother = models.ForeignKey(Patient)
    chw = models.ForeignKey(Reporter)
    child = models.ForeignKey(Child) 
    
    nation = models.ForeignKey(Nation, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    sector = models.ForeignKey(Sector, null=True, blank=True)
    cell = models.ForeignKey(Cell, null=True, blank=True)
    village    = models.ForeignKey(Village, null=True, blank=True)
    health_centre = models.ForeignKey(HealthCentre, null=True, blank=True)
    referral_hospital = models.ForeignKey(Hospital, null=True, blank=True) 
       
    child_number = models.CharField(max_length = 2, blank=True, null= True)
    date_of_birth = models.DateField(null=True, blank = True)
    gender = models.CharField(max_length = 2, blank=True, null= True, choices = GENDER_CHOICES, help_text="Select the gender") ##child_sex()
    symptoms = models.CharField(max_length = 100, blank=True, null=True)
    located = models.CharField(max_length = 2, blank=True, null= True)
    breastfeeding = models.CharField(max_length = 3, blank=True, null= True)
    weight = models.FloatField(blank=True, null=True)

    age_in_months = models.IntegerField(default = 0)
    
    report = models.ForeignKey(Report)
    
    def __unicode__(self):
        return "Child: %d" % self.child.id
    
    class Meta:

        # define a permission for this app to use the @permission_required
        # in the admin's auth section, we have a group called 'manager' whose
        # users have this permission -- and are able to see this section
        permissions = (
            ("can_view", "Can view"),
        )
        unique_together = ('mother', 'child')
    
    
    def _get_location(self):
        
        try:
            return  BIRTH_LOCATION[self.located.lower().strip()]
        except Exception, e:
            return BIRTH_LOCATION['ho']
    
    def _get_symptoms(self):

        try:
            signs = self.symptom.lower().split(" ")
            symptoms = ""
            for s in signs:
                try:    symptoms.join(", " + BIRTH_SYMPTOMS[s])
                except: continue
            return  symptoms
        except Exception, e:
            return BIRTH_SYMPTOMS['np']
        
    location    =   property(_get_location)
        
class ChildHealth(models.Model):
    """
    Keeps track of child health reports
    
    """
    
    mother = models.ForeignKey(Patient)
    chw = models.ForeignKey(Reporter)
    child = models.ForeignKey(Child) 
    
    nation = models.ForeignKey(Nation, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    sector = models.ForeignKey(Sector, null=True, blank=True)
    cell = models.ForeignKey(Cell, null=True, blank=True)
    village    = models.ForeignKey(Village, null=True, blank=True)
    health_centre = models.ForeignKey(HealthCentre, null=True, blank=True)
    referral_hospital = models.ForeignKey(Hospital, null=True, blank=True)
    
    child_number = models.CharField(max_length = 2, blank=True, null= True)
    date_of_birth = models.DateField(null=True, blank = True)
    current_symptoms = models.CharField(max_length = 100, blank=True, null=True)
    vaccination_received = models.CharField(max_length = 2, blank=True, null= True)
    vaccination_status = models.CharField(max_length = 2, blank=True, null= True)
    located = models.CharField(max_length = 2, blank=True, null= True)
    weight = models.FloatField(blank=True, null=True)
    muac = models.FloatField(blank=True, null=True)

    gender = models.CharField(max_length = 2, blank=True, null= True, choices = GENDER_CHOICES, help_text="Select the gender")
    age_in_months = models.IntegerField(blank=True, null=True)

    weight_for_age = models.FloatField(blank=True, null=True)
    length_height_for_age = models.FloatField(blank=True, null=True)
    weight_for_height = models.FloatField(blank=True, null=True)
    weight_for_length = models.FloatField(blank=True, null=True)
        
    report = models.ForeignKey(Report)

    def __unicode__(self):
        return "Child: %d" % self.child.id
    
    class Meta:

        # define a permission for this app to use the @permission_required
        # in the admin's auth section, we have a group called 'manager' whose
        # users have this permission -- and are able to see this section
        permissions = (
            ("can_view", "Can view"),
        )
        unique_together = ('child', 'report')

class ChildNutrition(models.Model):
    
    """
    This model helps us to store child nutrition report as they are coming
    We have mentioned that it is a good practice to separate them from other kind of reports
    To speed up specific queries from nutrition
    
    """
    
    mother = models.ForeignKey(Patient)
    chw = models.ForeignKey(Reporter)
    child = models.ForeignKey(Child)
    
    nation = models.ForeignKey(Nation, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    sector = models.ForeignKey(Sector, null=True, blank=True)
    cell = models.ForeignKey(Cell, null=True, blank=True)
    village    = models.ForeignKey(Village, null=True, blank=True)
    health_centre = models.ForeignKey(HealthCentre, null=True, blank=True)
    referral_hospital = models.ForeignKey(Hospital, null=True, blank=True)
    
    child_number = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length = 2, blank=True, null= True, choices = GENDER_CHOICES, help_text="Select the gender")
    date_of_birth = models.DateField(null=True, blank = True)
    age_in_days = models.IntegerField(blank=True, null=True)
    age_in_months = models.IntegerField(blank=True, null=True)   
    
    breastfeeding = models.CharField(max_length = 3, blank=True, null= True)   
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    muac = models.FloatField(blank=True, null=True)
    
    weight_for_age = models.FloatField(blank=True, null=True)
    length_height_for_age = models.FloatField(blank=True, null=True)
    weight_for_height = models.FloatField(blank=True, null=True)
    weight_for_length = models.FloatField(blank=True, null=True) 
    
    report = models.ForeignKey(Report)

    def __unicode__(self):
        return "Child: %d" % self.child.id

    class Meta:

        # define a permission for this app to use the @permission_required
        # in the admin's auth section, we have a group called 'manager' whose
        # users have this permission -- and are able to see this section
        permissions = (
            ("can_view", "Can view"),
        )
        unique_together = ('child', 'report', 'age_in_months')

class Pregnancy(models.Model):
    """
    This stores pregnancy reports.    
    """    

    woman = models.ForeignKey(Patient)
    chw = models.ForeignKey(Reporter)
    
    nation = models.ForeignKey(Nation, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    sector = models.ForeignKey(Sector, null=True, blank=True)
    cell = models.ForeignKey(Cell, null=True, blank=True)
    village    = models.ForeignKey(Village, null=True, blank=True)
    health_centre = models.ForeignKey(HealthCentre, null=True, blank=True)
    referral_hospital = models.ForeignKey(Hospital, null=True, blank=True)
       
    weight = models.FloatField(blank=True, null=True) 
    height = models.FloatField(blank=True, null=True) 
    bmi_anc1 = models.FloatField(blank=True, null=True)
    gravidity = models.IntegerField(blank=True, null=True)
    parity = models.IntegerField(blank=True, null=True) 
    
    previous_symptoms = models.CharField(max_length = 100, blank=True, null=True)
    current_symptoms = models.CharField(max_length = 100, blank=True, null=True)
    location = models.CharField(max_length = 2, blank=True, null= True)
    toilet = models.CharField(max_length = 2, blank=True, null= True)
    handwashing = models.CharField(max_length = 2, blank=True, null= True)
    
    last_menstrual_period = models.DateField(blank=True, null=True) 
    expected_delivery_date              =  models.DateField(blank=True, null=True)
    expected_anc2_date         =   models.DateField(blank=True, null=True)
    expected_anc3_date         =   models.DateField(blank=True, null=True) 
    expected_anc4_date         =   models.DateField(blank=True, null=True) 

    is_risky = models.BooleanField(default=False)
    is_high_risky = models.BooleanField(default=False)###Such kind of flags are important to make sure our query are optimized for non required checks/calc
    
    
    report = models.ForeignKey(Report)
    
    class Meta:

        # define a permission for this app to use the @permission_required
        # in the admin's auth section, we have a group called 'manager' whose
        # users have this permission -- and are able to see this section
        permissions = (
            ("can_view", "Can view"),
        )
        unique_together = ('woman', 'last_menstrual_period')
    
    def __unicode__(self):
        return self.woman.national_id
    
    @classmethod
    def calculate_edd(cls, last_menses):
        """
        Given the date of the last menses, figures out the expected delivery date
        """
        # first add seven days
        edd = last_menses + datetime.timedelta(7)
        neufmois = datetime.timedelta(days = 270)
        
        return edd + neufmois

    @classmethod
    def calculate_last_menses(cls, edd):
        """
        Given an EDD, figures out the last menses date.  This is basically the opposite
        function to calculate_edd
        """
        
        return edd - datetime.timedelta(days = 277)


