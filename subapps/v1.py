#!/usr/bin/env/python

import web
from apps.api import v1

urls = ("/sandbox/?", "apps.api.v1.Sandbox",
        "/twiml/directions/(.*)/(.*)/?", "apps.api.v1.TwimlDirections",
        "/directions/(.*)/(.*)/?", "apps.api.v1.Directions",
        "/tincan/sms/?", "apps.api.v1.TincanSMS",
        "/tincan/voice/?", "apps.api.v1.TincanVoice",
        "/tincan/?", "apps.api.v1.TincanEntry",        
        "/?", "apps.api.v1.Api",
        "/.*", "Error",)

#===============================================================#
# Error
#===============================================================#
class Error:
    def GET(self, err1=None, err2=None, err3=None):
        """
        """
        raise web.seeother(web.ctx.homedomain + "/404")

subapp = web.application(urls, globals())
