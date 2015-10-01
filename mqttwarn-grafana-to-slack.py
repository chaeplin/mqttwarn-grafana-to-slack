#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = 'CHAEPIL LIM <chaeplin()gmail.com>'
__copyright__ = 'Copyright 2015 CHAEPIL LIM'
__license__   = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""


HAVE_SLACK=True
try:
    from slacker import Slacker
    import os
    import sys
    import time
    import StringIO
    import datetime
    import urllib2
    from PIL import Image

except ImportError:
    HAVE_SLACK=False

"""
[config:grafanatoslack]
token = 'xxxx-1234567890-1234567890-1234567890-1234a1'
targets = {
              #channel_id,  url, header, header_contents, dir_to_save
    'mychannel' : [ 'channel_id',   'http://a/b',  'Authorization',  'Bearer joxfQ==', '/home/nfs/webcam' ],
  }

"""

def plugin(srv, item):

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if HAVE_SLACK == False:
        srv.logging.error("slacker module missing")
        return False

    token = item.config.get('token')
    if token is None:
        srv.logging.error("No token found for slack")
        return False

    try:
        channel_id, url, header, header_contents, dir_to_save = item.addrs

    except:
        srv.logging.error("Incorrect target configuration")
        return False

    # If the incoming payload has been transformed, use that,
    # else the original payload
    text = item.message

    if text != "Nemo: 0" :
        # get png
    
        cur_month = datetime.datetime.now().strftime("%Y%m")
        cur_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
        cur_dir = dir_to_save + "/" + cur_month
        if not os.path.exists(cur_dir):
            os.makedirs(cur_dir)
    
        cur_img = cur_dir + "/" + cur_time + ".png"
    
        try:
            req = urllib2.Request(url)
            req.add_header(header, header_contents)
            response = urllib2.urlopen(req)
            headers = response.info().headers
            data = response.read()
            if data:
               im = Image.open(StringIO.StringIO(data))
               im.save(cur_img, "PNG")
    
    
        except Exception, e:
            srv.logging.warning("Cannot get grafana file: %s" % (str(e)))
            return False
    
        # upload to slack
        try:
            slack = Slacker(token)
            if os.path.isfile(cur_img):
                slack.files.upload(cur_img, channels=channel_id)
    
        except Exception, e:
            srv.logging.warning("Cannot post to slack: %s" % (str(e)))
            return False

    return True