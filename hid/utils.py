# encoding=utf-8
# maintainer: katembu

import os

from urlparse import urlparse
import httplib
import math
import random

from bs4 import BeautifulSoup as Soup
from datetime import datetime

from hid.models import *

VALID_CHARS = "0123456789ACDEFGHJKLMNPRTUVWXY"
LEN = 4


def getBaseCharacters():
    '''Return base characters'''
    return VALID_CHARS


def getIdentifierLength():
    '''Return Identifier Length'''
    return LEN


def generate(id_without_check):
    '''Append Check digit '''
    checkdigit = computeCheckDigit(id_without_check)
    return id_without_check + checkdigit


def computeCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)
        print identifier

        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        #this will be a running total
        sum = 0

        # loop through digits from right to left
        for n, char in enumerate(reversed(identifier)):
            if not valid_chars.count(char):
                raise Exception('InvalidIDException')

            # Point
            code_point = valid_chars.index(char)

            # weight will be the current digit's contribution to
            # the running total
            weight = None
            if (n % 2 == 0):
                weight = (2 * code_point)
            else:
                weight = code_point

            weight = (weight / mod) + (weight % mod)
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod
        checkCodePoint = mod - remainder
        print remainder
        print checkCodePoint
        try:
            checkdigit = valid_chars[checkCodePoint]
        except:
            checkdigit = valid_chars[0]

        return checkdigit


def validateCheckDigit(identifier):
        '''Compute CheckDigit for a passed identifier'''
        valid_chars = getBaseCharacters()
        mod = len(valid_chars)

        # remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        # this will be a running total
        sum = 0
        # loop through digits from right to left
        for n, char in enumerate(reversed(identifier)):
            if not valid_chars.count(char):
                #raise Exception('InvalidIDException')
                return False

            # Point
            code_point = valid_chars.index(char)
            # weight will be the current digit's contribution to
            # the running total
            weight = None
            if (n % 2 == 0):
                weight = code_point
            else:
                weight = (2 * code_point)

            weight = (weight / mod) + (weight % mod)
            # keep a running total of weights
            sum += weight

        # return check digit
        remainder = sum % mod
        return (remainder == 0)


def generateIdentifier():
    char = getBaseCharacters()
    slen = getIdentifierLength()
    identifier = ''.join([random.choice(char) for i in range(0, slen - 1)])
    return generate(identifier)

 
def transmit_form(form):
    ''' Submit data to commcare server '''
    xml_form = form.data
    headers = {"Content-type": "text/xml", "Accept": "text/plain"}
    url = form.COMMCARE_URL
    SUBMIT_CASEXML = form.SUBMIT_TO_COMMCARE

    if SUBMIT_CASEXML:
        print url
        up = urlparse(url)
        conn = httplib.HTTPSConnection(up.netloc) if url.startswith("https") \
                                        else httplib.HTTPConnection(up.netloc)
        conn.request('POST', up.path, xml_form, headers)
        resp = conn.getresponse()
        responsetext = resp.read()
        if resp.status == 201:
            print "Bad HTTP Response: %s " % responsetext
        else:
            print "Thanks for submitting %s Bad response text" % responsetext


def valid_hid(hid):
    ''' Check if HID is Valid '''
    try:
        Identifier.objects.get(identifier=hid)
        return True
    except Identifier.DoesNotExist:
        return False


def oldvalid_hid(hid, site):
    ''' Check if HID exists in previous CHILDCOUNT IDs '''
    try:
        IssuedIdentifier.objects.get(identifier=hid, site__slug=site)
        return True
    except IssuedIdentifier.DoesNotExist:
        return False


def checkhid(hid, site):
    if oldvalid_hid(hid, site):
        #Check if HID exist in childcount hid pool.
        response = {'status': True, 'hid': hid}
    elif valid_hid(hid):
        new = valid_hid(hid)
        if new.status == Identifier.STATUS_GENERATED:
            new.status = STATUS_ISSUED
            new.save()
        response = {'status': True, 'hid': hid}
        #check if HID exist in new generated IDs
    else:
        #z = Identifier.objects.filter(status=Identifier.STATUS_GENERATED)[0]
        response = {'status': True, 'hid': hid}

    return response


def sanitise_case(site, data):
    soup = Soup(data)
    #check if case type exist
    try:
        m = soup.find('case_type')
        s = m.text.lower()
        valid = True
    except:
        valid = False

    '''
    If case_type exist check case type.
    Household Registration Form has different name tag for variable storing
    '''
    if valid:
        old_hid = False
        if s == 'household':
            try:
                m = soup.find('household_head_health_id')
                old_hid = m.text.upper()
                tag = 'household_head_health_id'
            except:
                return False
        else:
            try:
                m = soup.find('health_id')
                old_hid = m.text.upper()
                tag = 'health_id'
            except:
                return False

        z = checkhid(old_hid, site)
        print z
        
        print "===== "
        print tag
        print old_hid
        print site
        print "===== "

        z = checkhid(old_hid, site)
        print z
        '''
        if z['status'] == True:
            print z['hid']
        else:
            print ">>>> Error >>"
        '''   
    else:
        '''
        update form to indicate that it was not processed because it did
        not specify have case_type
        '''
        return False
