#!/usr/bin/env/python

import web
import urllib, urllib2
import httplib
import json
from HTMLParser import HTMLParser
from config import SERVER
from config import private_conf as pc
import pywapi
from twilio import twiml
from twilio.rest import TwilioRestClient
import re

SMS_MAX_LEN = 150 

class Api:
    def GET(self):
        """
        Root resource served when a GET request is made to /v1/api/
        """
        #render = web.ctx.shared['render']
        #slender = web.ctx.shared['slender']
        i = web.input()
        #service = getattr(i, 'service', None)
        #url =  getattr(i, 'url', None)
        #if service and url:
        #    return REST(url).GET()
        return "<p>This is be the root of our API</p>"

class Sandbox:
    def GET(self):
        pass

class Directions:
    def GET(self, src=None, dest=None):
        i = web.input()
        prettyprint = getattr(i, 'pretty', False)
        slender = web.ctx.shared['slender']
        if src and dest:
            src = src.replace(" ", "+")
            dest = dest.replace(" ", "+")
            url = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=walking&sensor=false" % (src, dest)
            data = urllib2.urlopen(url).read()
            jdata = json.loads(data)
            jdata = jdata['routes'][0]['legs'][0]['steps']
            if prettyprint:
                return slender.directions(jdata)
            #web.header('Content-Type', 'application/json')
            return json.dumps(jdata)
        
        return "i gets get and post, fo real!"

class TincanEntry:
    def GET(self):
        """ Evan, do yo thang! """
        i = web.input()
        return TincanSMS().GET() # you may be able to pass 'i' into TincanSMS + Voice - GET(i)
    
class TincanSMS:
    def GET(self):
        account = pc.webapis['twilio']['account_sid']
        token = pc.webapis['twilio']['auth_token']
        client = TwilioRestClient(account, token)

        # Create our twilio xml object (initialize it as a response)
        resp = twiml.Response()

        # Get our SMS msg from user
        i = web.input()
        body = getattr(i, 'Body', None)

        # bag of words is a list of words
        bow = body.split(" ")
        msg_zipcode = getattr(i, 'FromZip', None)

        if len(bow) and bow[0] == "W":
            result = self.exec_weather(bow, msg_zipcode)
            print result
            resp.sms(result)

        elif len(bow) and bow[0] == "E":
            result = self.exec_hydrant(bow)
            url = 'https://www.google.com/fusiontables/api/query?sql=SELECT * FROM '
            headers= {'Content-Type': 'application/x-www-form-urlencoded'}
            data = urllib2.urlopen(url).read()
            results = json.loads(data)
            return results

        elif len(bow) and bow[0] == "M":
            body = body[2:] # remove the "M " in the request            
            src, dest = body.split(" to ")
            path = urllib.quote("/api/v1/twiml/directions/%s/%s" % (src, dest))
            print TwimlDirections().GET(src, dest)
            call = client.calls.create(to="16033056953",
                                       from_="14155992671",
                                       url="http://www.codesf.org:8080" + path)
            return call.sid
            #directions = self.exec_directions(body)
            #resp.say(directions)
            #resp.sms(directions[:SMS_MAX_LEN - 5])
            #for result in chunk(directions, SMS_MAX_LEN):
            #    print result
            #    resp.sms(result)

        return str(resp)
                    
    def exec_weather(self, bow, msg_zipcode):
        """
        """
        zipcode = bow[1] if len(bow)>=2 and bow[1] else msg_zipcode
        forecast = pywapi.get_weather_from_google(zipcode)['current_conditions']
        f_tmp = forecast['temp_f']
        condition = forecast['condition']
        weather = "The weather at %s is %sf and %s" % (zipcode, f_tmp, condition)
        return weather
    
    def exec_hydrant(self, bow):
        """ Hyndrant port """
        url = 'https://www.google.com/fusiontables/api/query?sql=SELECT * FROM S332004hUlz'
        headers= {'Content-Type': 'application/x-www-form-urlencoded'}
        data = urllib2.urlopen(url).read()
        results = json.loads(data)
        return results

def chunk(lst, n):
    """
    Yield successive n-sized chunks from l.
    """
    if len(lst) < n:
        return [lst]
    chunks = []
    for i in xrange(0, len(lst), n):
        chunks.append(lst[i:i+n])
    return chunks

class TwimlDirections:
    def GET(self, src=None, dest=None):
        path = urllib.quote("/api/v1/directions/%s/%s" % (src, dest))
        url = SERVER + path
        data = urllib2.urlopen(url).read()
        directions = json.loads(data)
        
        unsent = ''
            
        for direction in directions:
            instruction = strip_tags(direction['html_instructions'])
            dist = direction['duration']['value']
            duration = direction['duration']['text']
            unsent += '%s ' % instruction#, dist, duration

        resp = twiml.Response()
        resp.say(unsent)
        web.header('Content-Type', 'text/xml')
        return str(resp)

    def POST(self, src=None, dest=None):
        path = urllib.quote("/api/v1/directions/%s/%s" % (src, dest))
        url = SERVER + path
        data = urllib2.urlopen(url).read()
        directions = json.loads(data)
        
        unsent = ''
            
        for direction in directions:
            instruction = strip_tags(direction['html_instructions'])
            dist = direction['duration']['value']
            duration = direction['duration']['text']
            unsent += '%s ' % instruction#, dist, duration

        resp = twiml.Response()
        resp.say(unsent)
        web.header('Content-Type', 'text/xml')
        return str(resp)

class TincanVoice:
    def GET(self):
        account = pc.webapis['twilio']['account_sid']
        token = pc.webapis['twilio']['auth_token']
        client = TwilioRestClient(account, token)
        call = client.calls.create(to="16033056953",
                                   from_="14155992671",
                                   url="http://demo.twilio.com/welcome/voice")
        return call.sid

class Responder:
    def GET(self):
        resp = twiml.Response()
        resp.sms("Please enter your current location:")

class REST:
    def GET(self, url):
        """
        Call any REST Api over the web and return the JSON representation
        """
        data = urllib2.urlopen(url).read()
        json.dumps(data)
        return ""

    def POST(self, url, path):
        i = web.input()
        dest = getattr(i, 'dest', None)
        if dest:
            del i['dest']

        params = urllib.urlencode(i)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(url)
        response = conn.request("POST", path, params, headers)
        data = response.read()
        #print(data)
        conn.close()
        return data
    
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
