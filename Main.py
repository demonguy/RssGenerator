import webapp2
import re
import PyRSS2Gen
import datetime
from google.appengine.api import urlfetch
from pubsubhubbub_publish import *


PatternDicts = {'Title':'漫画','url':"http://www.manmankan.com/",'global':'<div class="hotlist">(.*)</div>',"item":'<em class="lab_tit">.*?href="(.+?)".*?title="(.+?)".*?</em>',"itemTitle":2,'itemLink':1}


class MainPage(webapp2.RequestHandler):
	def get(self):
		url = PatternDicts['url']
		result = urlfetch.fetch(url)   #URL fetch
		
		globalPattern  = re.compile(PatternDicts['global'],re.DOTALL)
		itemPattern = re.compile(PatternDicts['item'],re.DOTALL)   #define regular expression
		
		charset = re.findall('(?i)charset=([\w\d-]+)',result.header_msg.getheaders('content-type')[0])
		charset = charset and charset[0] or 'gbk'
		
		content = result.content.decode(charset).encode('utf-8')  #translate page into utf-8
		
		globalPattern  = re.compile(PatternDicts['global'],re.DOTALL)
		itemPattern = re.compile(PatternDicts['item'],re.DOTALL)
		
		self.response.headers['Content-Type'] = 'text/xml;charset=utf-8'
		matches = globalPattern.findall(content)
		
		RssItems = []
		for index in range(len(matches)):
			match = itemPattern.findall(matches[index])
			for num in range(len(match)):
				title = match[num][PatternDicts['itemTitle'] - 1]
				link  = match[num][PatternDicts['itemLink'] - 1]
				description = PatternDicts.has_key('description') and match[num][PatternDicts['description'] - 1] or title
				#self.response.write(title + ":" + link + "\n")
				
				RssItems.append(
					PyRSS2Gen.RSSItem(  
						title = title,  
						link = link,  
						description = description,  
						guid = PyRSS2Gen.Guid(link),
					)
				)
		
		RSS = self.createRss(PatternDicts['Title'],PatternDicts['url'],RssItems,'http://pubsubhubbub.appspot.com')
		self.response.write(RSS.to_xml(encoding = 'utf-8'))
		#publish('http://pubsubhubbub.appspot.com','http://drssgenerator.appspot.com')	
				
				
	def createRss(self,Title,Link,Items,hub):
		return PyRSS2Gen.RSS2(
					title = Title,
					link = Link,
					description = "",
					lastBuildDate = datetime.datetime.now(),
					items = Items,
					hub = hub,
				)
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)