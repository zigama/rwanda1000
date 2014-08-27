#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


#Author: UWANTWALI ZIGAMA Didier

class Aggregator(object):

    """ This class is an abstraction of data aggregator, as for every indicator we are collecting 
        we need o aggregate on daily basis and by location, it was good the base location to be a village, but no one is using this, 
        so our aggregator base on health centre.
    """

    def __init__(self):

        """ Need to initialize the day and location ... why not the indicator .... 
            They are required , please remember to update it for every indicator.
        """
        self.date = None
        self.week = None
        self.month = None
        self.quarter = None
        self.location = None
        self.location_type = None
        self.indicator = None
        self.table = None
        self.field = None
        self.total = None

    def get_total_per_indicator(self):

        """
           You need to get the total per indicator, date, location and precise db details             
        """

        return {'indicator': self.indicator, 'location': self.location, 'location_type': self.location_type,
                 'date': self.date, 'week': self.week, 'month': self.month, 'quarter': self.quarter, 'table': self.table, 'field': self.field, 'total': self.total }




