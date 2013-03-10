import webapp2
import re
from pubsubhubbub_publish import *


class Cron(webapp2.RequestHandler):
    def get(self):
        publish('http://pubsubhubbub.appspot.com','http://drssgenerator.appspot.com')	
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Send Publish To Hub Successfully!')

app = webapp2.WSGIApplication([('/frequenthub', Cron)],
                              debug=True)