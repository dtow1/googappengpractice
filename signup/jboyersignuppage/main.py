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
import os
import jinja2
import re
import time
import hashlib

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def hash_str(s):
    return hashlib.md5(s + "secretword").hexdigest()

def check_secure_val(h):
    test=h.split('|')
    if test[1] == make_secure_val(test[0]).split('|')[1]:
        return test[0]


class Entry(db.Model):
    user_name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.EmailProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("signup.html", response = "")

    def post(self):
        response = ""
        redirect = False;

        username = self.request.get('username')
        if self.check_name(username) is None:
           response += "Please enter a valid username. "
           redirect = False;

        password = self.request.get('password')
        if self.check_password(password) is None:
            response += "Please enter a valid password. "
            redirect = False;

        verify = self.request.get('verify')
        if self.check_password(verify) is None:
            response += "Please verify your password. "
            redirect = False;

        if self.check_match(password, verify) is None:
            response += "Passwords do not match. "
            redirect = False;

        email = self.request.get('email')
        if self.check_email(email) is None:
            response += "Please enter a valid email. "
            redirect = False;

        if response == "":
            title = self.request.get("subject")
            article = self.request.get("content")

            # Check Database for existing user

            uid = self.request.get('username')
            email = self.request.get('email')
            pwd = self.request.get('password')
            data=db.GqlQuery("SELECT * FROM Entry WHERE user_name = '" + uid + "'")
            data2=db.GqlQuery("SELECT * FROM Entry WHERE email = '" + email + "'")



            if data.get():
                response += "User ID already exists" + str(data.get().user_name)

            if data2.get():
                response += "Email already registered" + str(data2.get().email)

            # Add new user

            else:
                hash_id = hash_str(uid)
                a = Entry(user_name=hash_id, password = hash_str(pwd), email = email)
                a.put()
                self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % str(make_secure_val(uid)))

        if response == "":
            self.redirect('/welcome')
        else:
            self.render("signup.html", response = response)


    def check_name(self, name):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return USER_RE.match(name)

    def check_password(self, password):
        PWD_RE = re.compile(r"^.{3,20}$")
        return PWD_RE.match(password)

    def check_match(self, password, confirm):
        return password == confirm

    def check_email(self, email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        return email == "" or EMAIL_RE.match(email)

class WelcomeHandler(Handler):
    def get(self):
        username = check_secure_val(self.request.cookies.get('name'))
        if username:
            self.render("welcome.html", username = username)
        else:
            self.redirect('/signup')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/welcome', WelcomeHandler,),
    ('/signup', MainHandler)
], debug=True)
