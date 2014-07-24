#!/usr/bin/env python

"""HIDProcessor.py: This class processes cases and assigns health_id to cases that dont have """

__author__ = "Josiah Njuki <jnjuki@cgcafrica.org>"
__copyright__ = "Copyright 2014, Modi Labs"


import mysql.connector
import csv
import logging

class HIDProcessor: 
    ############## CONFIGS ##################################
    username = 'root'
    password = 'r00t'
    server = 'localhost'
    db_name = 'hid_final'
    logPath = 'logs.log'    
    site_id = 'mvp-ruhiira'
    cnx = ""    
    def __init__(self):
        try:            
            self.cnx = mysql.connector.Connect(user=self.username, password=self.password, database=self.db_name, host=self.server)
            logging.basicConfig(filename=self.logPath, level=logging.DEBUG, format='%(levelname)s: %(asctime)s%(message)s on line %(lineno)d')
        except Exception as e:
            print str(e)  
    
    def read_csv(self):
        try:                        
            csv_data = csv.reader(open('data/child_household_pregnancy_Cases.csv', 'rb')) 
                          
            rowcount = len(list(csv_data))
            # print "rows count %i" %rowcount  
            afile = open('data/child_household_pregnancy_Cases.csv', 'r+')
            csvReader1 = csv.reader(afile)
            
            validIDs = 0
            invalidIDs = 0
            fullCount = 0
            tobeAssignedNew = 0
            casesToFulfilInternally = 0
            identifiersToGenerate = 0
            validButNotMarkedAsIssued = 0
            validAndIssued = 0
            
            # Invalid list holders
            childInvalidList = []
            pregnancyInvalidList = []
            householdInvalidList = []
            
            # csv format
            # case_id, site_id, case_type, child_hid, household_hid, pregnancy_hid 
            for i in range(rowcount):
                fullCount += 1 
                thisRow = csvReader1.next()
                case_id = thisRow[0];
                case_type = thisRow[1]   
                site_id = thisRow[2]
                             
                # switch case type:
                if case_type == "child":
                    case_type = 'C'
                    health_id = thisRow[3]
                elif case_type == "household":
                    case_type = 'H'
                    health_id = thisRow[4]
                elif case_type == "pregnancy":
                    case_type = 'P'
                    health_id = thisRow[3]
                    
                query_hid = "select id from hid_identifier where identifier='%s';" % health_id    
                # logging.info("query hid SQL=> %s" %query_hid)  
                cursor = self.cnx.cursor()
                cursor.execute(query_hid)
                rows = cursor.fetchall()
                resultsCount = len(rows)
                if resultsCount > 0:
                    validIDs += 1
                    id = rows[0][0]
                    # check if id has been issued for the site
                    query_issued = "select id from hid_issuedidentifier where identifier_id='%d' and site_id='%s';" % (id, self.site_id)    
                    # slogging.info("query issued SQL=> %s" %query_issued)  
                    cursor.execute(query_issued)
                    rows = cursor.fetchall()
                    resultsCount = len(rows)
                    if resultsCount > 0:
                        issuedID = rows[0][0]
                        validAndIssued += 1
                    else:
                        # For the valid but un-issued, insert into issuedidentifier
                        validButNotMarkedAsIssued += 1
                        insert_not_issued = """insert into hid_issuedidentifier (identifier_id, site_id, issued_on, status)      
 values('%d', '%s', now(), 'I');""" % (id, self.site_id)    
                        logging.info("health_id--- %s query insert issued  SQL=> %s" % (health_id, insert_not_issued))
                        cursor.execute(insert_not_issued)
                        issuedID = cursor.lastrowid
                    
                
                    # insert into cases
                    insert_case = """insert into hid_cases_playground(`case`, issued_id_id, case_type) values 
                    ('%s', '%d', '%s')""" % (case_id, issuedID, case_type)  
                    logging.info("case--- %s query insert case  SQL=> %s" % (case_id, insert_case))
                    cursor.execute(insert_case)     
                             
                else:  # invalid health_ids case list
                    # save empty/
                    invalidIDs += 1
                    if case_type == "C":                        
                        childInvalidList.append(case_id)
                    elif case_type == "H":
                        pregnancyInvalidList.append(case_id)           
                        
                    elif case_type == "P":
                        householdInvalidList.append(case_id)    
            
            
            # process invalid child list
            if len(childInvalidList) > 0:
                 for the_case_id in childInvalidList:
                     tobeAssignedNew += 1                
                     query_new_identifier = """select id, identifier from hid_identifier where id not in 
                     (select identifier_id from hid_issuedidentifier where site_id='%s') limit 1;""" % self.site_id    
                     logging.info("query new hid SQL=> %s" % query_new_identifier)  
                     cursor = self.cnx.cursor()
                     cursor.execute(query_new_identifier)
                     rows = cursor.fetchall()
                     resultsCount = len(rows)
                     if resultsCount > 0:  # a valid free identifier exists                          
                         casesToFulfilInternally += 1
                   # insert into issued
                         id = rows[0][0]
                         insert_new_issued = """insert into hid_issuedidentifier (identifier_id, site_id, issued_on, status)      
values('%d', '%s', now(), 'I');""" % (id, self.site_id)    
                         logging.info("health_id--- %s query insert issued  SQL=> %s" % (health_id, insert_new_issued))
                         cursor.execute(insert_new_issued)
                         issuedID = cursor.lastrowid
                          # insert into cases
                         insert_case = """insert into hid_cases_playground( `case`, issued_id_id, case_type) values 
                    ('%s', '%d', 'C')""" % (the_case_id, issuedID)  
                         logging.info("case--- %s query insert case  SQL=> %s" % (case_id, insert_case))
                         cursor.execute(insert_case) 
                   
                     else:                         
                        identifiersToGenerate += 1  # generate
                        # insert into issued
                        
            # process pregnancyList
            if len(pregnancyInvalidList) > 0:
                 for the_case_id in pregnancyInvalidList:
                     tobeAssignedNew += 1                
                     query_new_identifier = """select id, identifier from hid_identifier where id not in 
                     (select identifier_id from hid_issuedidentifier where site_id='%s') limit 1;""" % self.site_id    
                     logging.info("query new hid SQL=> %s" % query_new_identifier)  
                     cursor = self.cnx.cursor()
                     cursor.execute(query_new_identifier)
                     rows = cursor.fetchall()
                     resultsCount = len(rows)
                     if resultsCount > 0:  # a valid free identifier exists                          
                         casesToFulfilInternally += 1
                   # insert into issued
                         id = rows[0][0]
                         insert_new_issued = """insert into hid_issuedidentifier (identifier_id, site_id, issued_on, status)      
values('%d', '%s', now(), 'I');""" % (id, self.site_id)    
                         logging.info("health_id--- %s query insert issued  SQL=> %s" % (health_id, insert_new_issued))
                         cursor.execute(insert_new_issued)
                         issuedID = cursor.lastrowid
                          # insert into cases
                         insert_case = """insert into hid_cases_playground( `case`, issued_id_id, case_type) values 
                    ('%s', '%d', 'P')""" % (the_case_id, issuedID)    
                         logging.info("case--- %s query insert case  SQL=> %s" % (case_id, insert_case))
                         cursor.execute(insert_case) 
                   
                     else:                         
                        identifiersToGenerate += 1
                        
            # process ivalid householdList
            if len(householdInvalidList) > 0:
                 for the_case_id in householdInvalidList:
                     tobeAssignedNew += 1                
                     query_new_identifier = """select id, identifier from hid_identifier where id not in 
                     (select identifier_id from hid_issuedidentifier where site_id='%s') limit 1;""" % self.site_id    
                     logging.info("query new hid SQL=> %s" % query_new_identifier)  
                     cursor = self.cnx.cursor()
                     cursor.execute(query_new_identifier)
                     rows = cursor.fetchall()
                     resultsCount = len(rows)
                     if resultsCount > 0:  # a valid free identifier exists                          
                         casesToFulfilInternally += 1
                   # insert into issued
                         id = rows[0][0]
                         insert_new_issued = """insert into hid_issuedidentifier (identifier_id, site_id, issued_on, status)      
values('%d', '%s', now(), 'I');""" % (id, self.site_id)    
                         logging.info("health_id--- %s query insert issued  SQL=> %s" % (health_id, insert_new_issued))
                         cursor.execute(insert_new_issued)
                         issuedID = cursor.lastrowid
                          # insert into cases
                         insert_case = """insert into hid_cases_playground(`case`, issued_id_id, case_type) values 
                    ('%s', '%d', 'H')""" % (the_case_id, issuedID)     
                         logging.info("case--- %s query insert case  SQL=> %s" % (case_id, insert_case))
                         cursor.execute(insert_case) 
                   
                     else:                         
                        identifiersToGenerate += 1
            
            
            
            
            
            
             
                        
                # Replicate of pregnancy and household case types      
                     
            print 'valid: %d' % validIDs
            print 'invalid: %d' % invalidIDs
            print 'valid and issued: %d' % validAndIssued
            print 'validButNotMarkedAsIssued: %d' % validButNotMarkedAsIssued
            print 'child invalid: %d' % len(childInvalidList)
            print 'pregnancy invalid: %d' % len(pregnancyInvalidList)
            print 'household invalid: %d' % len(householdInvalidList)
            print 'tobeAssignedNew: %d' % tobeAssignedNew
            print 'cases fulfilled internally: %d' % casesToFulfilInternally
            print 'cases to generate new identifiers: %d' % identifiersToGenerate
            print 'Full count: %d' % fullCount
            totalCount = validAndIssued + validButNotMarkedAsIssued + casesToFulfilInternally + identifiersToGenerate
            
            # total count should be equal to the count in the csv            
            if totalCount == rowcount:
                print "totalCount=noOfRecords i.e %d = %d" % (totalCount, rowcount)
                logging.info("totalCount=noOfRecords i.e %d = %d" % (totalCount, rowcount))
                # identifiersToGenerate = 0
                if identifiersToGenerate == 0:
                    logging.info("identifiersToGenerate is Zero!! Commit to DB.....")
                    print "identifiersToGenerate is Zero!! Commit to DB....."
                    self.cnx.commit()
                    
                else:
                     logging.info("identifiersToGenerate is greater than Zero!! DONT Commit to DB.....")
                     print "identifiersToGenerate is greater than Zero!! DONT Commit to DB....."
                
            else:
                logging.info("totalCount != noOfRecords i.e %d != %d . Dont Commit" % (totalCount, rowcount))
                print "totalCount != noOfRecords i.e %d != %d . Dont Commit" % (totalCount, rowcount)
        except Exception as e:
            print 'Exception: %s' % str(e)
        self.cnx.close()    

processor = HIDProcessor()
processor.read_csv()
        
