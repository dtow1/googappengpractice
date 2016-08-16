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
import webapp2
import jinja2
import os
import time

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Entry(db.Model):
    title = db.StringProperty(required = True)
    article = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))

class MainHandler(Handler):
    def render_front(self, title="", article="", error=""):
        articles = db.GqlQuery("SELECT * FROM Entry "
                            "ORDER BY created DESC")
        self.render("main.html",title=title, article=article, error=error, articles = articles)

    def get(self):
        self.render_front()

class NewHandler(Handler):
    def render_front(self, title="", article="", error=""):
        articles = db.GqlQuery("SELECT * FROM Entry "
                            "ORDER BY created DESC")
        self.render("newpost.html",title=title, article=article, error=error, articles = articles)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("subject")
        article = self.request.get("content")

        if title and article:
            a = Entry(title=title, article=article)
            a.put()
            key=a.key().id();
            self.redirect("/post/" + str(key))
        else:
            error = "You need to include both a title and an article"
            self.render_front(title,article,error)

class PostHandler(Handler):
    def get(self):
        baseurl=self.request.url[:27]
        title=self.request.url[27:]
        article=self.request.query_string
        self.render("postpermalink.html", title=title,article=article)
    def post(self):
        self.render("postpermalink.html")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewHandler),
    (r'/post/[0-9]+', PostHandler)
], debug=True)
