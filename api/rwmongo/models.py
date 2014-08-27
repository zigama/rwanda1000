#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


#Author: UWANTWALI ZIGAMA Didier

from aggregator import Aggregator 

class DailyPregnancy(Aggregator):

    """ The objects list all possible indicators to be tracked in a pregnancy module on daily basis """

    pregnant_women_registered  = None ## Number of Pregnant Women Registered
    high_risk_pregnant_women_registered  = None ## Number of High Risk Pregnant Women Registered
    pregnant_women_registered_with_previous_symptoms = None
    pregnant_women_registered_with_current_symptoms = None
    expected_delivery_notifications = None ## Number of Expected Delivery Notifications
    expected_deliveries = None ## Number of Expected Deliveries
    expected_deliveries_this_week = None
    expected_deliveries_next_week = None
    expected_deliveries_next_two_weeks = None
    high_risk_expected_deliveries = None ## Number of High Risk Expected Deliveries
    high_risk_expected_deliveries_this_week = None
    high_risk_expected_deliveries_next_week = None
    high_risk_expected_deliveries_next_two_weeks = None
    proportion_of_lmp_to_pre_registration_1_month = None
    proportion_of_lmp_to_pre_registration_2_month = None
    proportion_of_lmp_to_pre_registration_3_month = None
    proportion_of_lmp_to_pre_registration_4_month = None
    proportion_of_lmp_to_pre_registration_5_month = None
    proportion_of_lmp_to_pre_registration_6_month = None
    proportion_of_lmp_to_pre_registration_7_month = None
    proportion_of_lmp_to_pre_registration_8_month = None
    proportion_of_lmp_to_pre_registration_9_month = None
    gs = None
    mu = None
    hd = None
    rm = None
    ol = None
    yg = None
    nr = None
    kx = None
    yj = None
    lz = None
    vo = None
    pc = None
    oe = None
    ns = None
    ma = None
    ja = None
    fp = None
    fe = None
    ds = None
    di = None
    sa = None
    rb = None
    hy = None
    ch = None
    np = None

     
class WeeklyPregnancy(object):
    pass

class MonthlyPregnancy(object):
    
    def get_total_per_module_indicators(self):

        """
            The indicators are sometimes grouped and displayed per module, use this to group them
        """
        group = []
        #read module, and find indicators listed there.

        return group



#Report

#ReportDetails



        
        

