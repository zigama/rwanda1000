#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


#Author: UWANTWALI ZIGAMA Didier


import settings
import pymongo

class Config(object):

    '''Default configuration object.'''

    def __init__(self):
        """ We need to initialize the DB for our API, as this is required"""

        self.MONGODB_USER = settings.MONGODB_USER
        self.MONGODB_PASSWORD = settings.MONGODB_PASSWORD
        self.MONGODB_HOST = settings.MONGODB_HOST
        self.MONGODB_PORT = settings.MONGODB_PORT
        self.MONGODB_DB = settings.MONGODB_DB

        self.MASTER_DB_USER = settings.MASTER_DB_USER
        self.MASTER_DB_PASSWORD = settings.MASTER_DB_PASSWORD
        self.MASTER_DB_HOST = settings.MASTER_DB_HOST
        self.MASTER_DB_PORT = settings.MASTER_DB_PORT
        self.MASTER_DB_NAME = settings.MASTER_DB_NAME

    def open_rwmongo_connection(self):
        """ Need to open and return the connection when this app is on"""
        connection = pymongo.Connection(self.MONGODB_HOST, self.MONGODB_PORT)
        return connection

    def get_rwmongo_db(self, connection):
        db = pymongo.database.Database(connection, self.MONGODB_DB)
        db.authenticate(self.MONGODB_USER, self.MONGODB_PASSWORD)
        return db

    def close_rwmongo_connection(self, connection)
        """ Need to close the connection when this app is off """
        connection.close()


    def open_rwmaster_connection(self):
        """ Need to open and return the connection when this app is on"""
        connection = pymongo.Connection(self.MONGODB_HOST, self.MONGODB_PORT)
        return connection

    def get_rwmaster_db(self, connection):
        db = pymongo.database.Database(connection, self.MONGODB_DB)
        db.authenticate(self.MONGODB_USER, self.MONGODB_PASSWORD)
        return db

    def close_rwmaster_connection(self, connection)
        """ Need to close the connection when this app is off """
        connection.close()
