#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import logging
import re
from models import Rank
from BeautifulSoup import BeautifulSoup
from abstract import BaseHandler
from google.appengine.api.taskqueue import Task,Queue

class MainHandler(BaseHandler):
    def get(self):
        apps = Rank.all().filter('category','apps_topselling_free').order("rank").fetch(500)
        self.render_template("index.html",{"apps":apps})

class CronHandler(webapp.RequestHandler):
    def get(self):
        num_pages_to_fetch=50
        q = Queue('scrape')
        for i in range(0,num_pages_to_fetch):
            q.add(Task(url='/tasks/scrape?page=%d' % i, method='GET'))
        self.response.out.write("done")
        
class ScrapeHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-type']="text/plain"
        npp = 12
        category = 'apps_topselling_free'
        page = int(self.request.get("page"))
        url = 'http://market.android.com/details?id=%s&cat=GAME&start=%d&num=%d' % (category,page*npp,npp)
        html = urlfetch.fetch(url,deadline=10).content
        soup = BeautifulSoup(html)
        
        applist = soup.findAll('a',{"class":re.compile("title")})
        formatted = [(unicode(app.contents[0]),unicode(app['href']).replace('/details?id=','')) for app in applist]
        n = page*npp
        for item in formatted:
            n+=1
            name,uniqueid = item
            r = Rank(key_name=str(n), name=name, uniqueid=uniqueid, rank=n, category=category)
            r.put()
        self.response.out.write("done")


def main():
    application = webapp.WSGIApplication([('/', MainHandler),('/tasks/scrape', ScrapeHandler),('/cron/scrape', CronHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
