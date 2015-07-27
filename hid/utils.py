# encoding=utf-8
# maintainer: katembu

import os
from urlparse import urlparse
import httplib
import math
import random
import codecs
from datetime import datetime
from django.template import Context, Template
import uuid
from bs4 import BeautifulSoup as Soup

from hid.models import *


ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

VALID_CHARS = "0123456789ACDEFGHJKLMNPRTUVWXY"
LEN = 3


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

        # Remove leading or trailing whitespace, convert to uppercase
        identifier = identifier.strip().upper()

        # This will be a running total
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
                # raise Exception('InvalidIDException')
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
    xml_form = form['data']
    headers = {"Content-type": "text/xml", "Accept": "text/plain"}
    url = form['COMMCARE_URL']
    SUBMIT_CASEXML = form['SUBMIT_TO_COMMCARE']

    if SUBMIT_CASEXML:
        print url
        up = urlparse(url)
        conn = httplib.HTTPSConnection(up.netloc) if url.startswith("https") \
            else httplib.HTTPConnection(up.netloc)
        conn.request('POST', up.path, xml_form, headers)
        resp = conn.getresponse()
        responsetext = resp.read()
        if resp.status == 201:
            print "Thanks for submitting  %s " % responsetext
            return True
        else:
            print "Bad response text: %s " % responsetext
            return False


def xml_template_upload(form, domain_url):
    ''' Submit data to commcare server '''

    xml_form = form.render()
    headers = {"Content-type": "text/xml", "Accept": "text/plain"}

    xml_form = xml_form.encode('utf-8')
    url = domain_url
    up = urlparse(url)
    conn = httplib.HTTPSConnection(up.netloc) if url.startswith("https") \
        else httplib.HTTPConnection(up.netloc)
    conn.request('POST', up.path, xml_form, headers)
    resp = conn.getresponse()
    responsetext = resp.read()
    if resp.status == 502:
        print "Retrying ..."
        transmit_form(form, domain_url)
    elif resp.status == 201:
        print "Thanks for submitting %s " % responsetext
        return True
    else:
        print "Bad HTTP Response: [%s] %s " % (resp.status, responsetext)
        return False


def valid_hid(hid):
    ''' Check if HID is Valid '''
    try:
        Identifier.objects.get(identifier=hid)
    except Identifier.DoesNotExist:
        return False
    return True


def oldvalid_hid(hid, site):
    ''' Check if HID exists in previous CHILDCOUNT IDs '''
    try:
        p = IssuedIdentifier.objects.get(identifier__identifier=hid,
                                         site__slug=site)
    except IssuedIdentifier.DoesNotExist:
        return False

    p.status = IssuedIdentifier.STATUS_ISSUED
    p.save()
    return True


def checkhid(hid, site):
    # Check if HID exist in childcount hid pool.
    if oldvalid_hid(hid, site):
        return True
    elif valid_hid(hid):
        hid = Identifier.objects.get(identifier=hid)
        site = Site.objects.get(slug=site)
        new = IssuedIdentifier()
        new.identifier = hid
        new.status = IssuedIdentifier.STATUS_ISSUED
        new.site = site
        new.save()
        return True
    else:
        return False


def get_caseid(data):
    soup = Soup(data)
    # check if case type exist
    try:
        m = str(soup.case['case_id'])
        return m
    except:
        return False


def sanitise_case(site, data):
    # check if case type exist
    soup = Soup(data)
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
                household = True
            except:
                return False
        else:
            try:
                m = soup.find('health_id')
                old_hid = m.text.upper()
                tag = 'health_id'
                household = False
            except:
                return False
        try:
            hid_status = checkhid(old_hid, site)
        except:
            hid_status = False

        return {'status': hid_status, 'form_type': s, 'household': household}
    else:
        '''
        update form to indicate that it was not processed because it did
        not specify have case_type
        '''
        return {'status': True}


class CaseXMLInterface(object):
    template_name = ""
    data = {}

    def __init__(self, data, template):

        # load template
        self.data = data
        self.data['uuid'] = uuid.uuid4().hex
        self.data['timeend'] = self._format_datetime(datetime.utcnow())
        self.template_name = template
        self.load_template()

    def _format_datetime(self, time):
        return time.strftime(ISO_FORMAT)

    def set_template(self, set_temp):
        return set_temp

    def load_template(self):
        fp = codecs.open('%(template)s' % {'template': self.template_name})
        self.template = Template(fp.read())
        fp.close()

    def render(self):
        ''' returns the CaseXML formatted Form to Submit to Commcare '''
        rendered = self.template.render(Context(self.data))
        return rendered


def check_file(file_name, ftype):
    exist = True
    if not os.path.exists(file_name):
        exist = False
    if file_name.split(".")[-1] != ftype:
        exist = False

    return exist


def generate_caselist(site):
    from logger_ng.models import LoggedMessage
    data = {}
    try:
        site = Site.objects.get(slug=site)
    except Site.DoesNotExist:
        return {'Site': False}

    messages = LoggedMessage.objects.filter(direction=self.DIRECTION_OUTGOING,
                                            site=site)[0]
    if(messages.count() > 0):
        for m in messages:
            m = Soup(m.text)
            try:
                p = [tag.attrs for tag in m.findAll('case')]
                z = p[0]['case_id']
            except:
                return {'Site': "Error"}
            if(z):
                data.update({z: z})
                print ">>>> "  z
        f = open('cases_to/' + site.name + '.txt', 'w+')
        for d in data:
            k = str(data[d]) + ' \n'
            f.write(k)
        f.close()
