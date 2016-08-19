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
import datetime

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


# Create a hash value that includes the original value along with its
# hash. Used to verify that cookies have not been tampered with.
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

# Simple hash method that creates an md5 hash from a string and a salt value
def hash_str(s):
    return hashlib.md5(s + "secretword").hexdigest()

# Method to test if a secure value and its hash are correct
def check_secure_val(h):
    test=h.split('|')
    if test[1] == make_secure_val(test[0]).split('|')[1]:
        return test[0]



# Database setup for the registration data.
class Users(db.Model):
    user_name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)



# Database setup for the article data.
class Entry(db.Model):
    title = db.StringProperty(required = True)
    article = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

# Base handler class to simplify write and render operations for other methods.
# This class is from the Udacity Full Stack Developer Nanodegree.
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))



# Class to validate form data
class ValidateForm():
    def validate(self, username,password,verify,email):
        response=""

        # Check each form item and create an error if it does not meet the
        # requirements.
        if self.check_name(username) is None:
            response += "Please enter a valid username. "

        if self.check_password(password) is None:
            response += "Please enter a valid password. "

        if self.check_password(verify) is None:
            response += "Please verify your password. "

        if self.check_match(password, verify) is None:
            response += "Passwords do not match. "

        if self.check_email(email) is None:
            response += "Please enter a valid email. "

        return response

    #Method to check the username against the requirements regex.
    def check_name(self, name):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return USER_RE.match(name)

    # Method to check if a password against the requirements regex.
    def check_password(self, password):
        PWD_RE = re.compile(r"^.{3,20}$")
        return PWD_RE.match(password)

    # Method to verify that password and confirmation passord match.
    def check_match(self, password, confirm):
        return password == confirm

    # Method to validate an email address against an email regex.
    def check_email(self, email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        return email == "" or EMAIL_RE.match(email)



# Class to verify user and email have not been registered. If they are new,
# create a new user in the database.
class CreateUser():
    def create(self, uid="",email="",pwd=""):
        # Check Database for existing user

        # Gql does not support OR statements in the WHERE clause, need two
        # separate queries to make sure both UID and email are not yet
        # registered.
        response = ""
        if uid !="" and pwd!="":
            data=db.GqlQuery("SELECT * FROM Users WHERE user_name = '" + uid + "'")
            data2=db.GqlQuery("SELECT * FROM Users WHERE email = '" + email + "'" + "and email != ''")

            # Check if UID has been registered
            if data.get():
                response += "User ID already exists" + str(data.get().user_name)

            # Check if email has been registered
            if data2.get():
                response += "Email already registered" + str(data2.get().email)

            # Add new user if no errors have been identified
            if response=="":
                # Hash and store the UID and password
                a = Users(user_name=hash_str(uid), password = hash_str(pwd), email = email)
                key = a.put()
                if not key:
                    response += "Error adding to database"
        else:
            response += "Error adding to database"

        return response



# This is the handler for the registration page. It is responsible for form
# validation, rejecting duplicate IDs or emails, and registering the user if
# all requirements are satisfied.
class SignUpHandler(Handler):
    def get(self):
        self.render("signup.html", response = "")

    def post(self):
        response = ""

        # Get each form value
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        # Test each form value for validity, update error message if any errors
        # exist.
        response = ValidateForm().validate(username = username,
                                        password = password,
                                        verify = verify,
                                        email = email)

        # If no error message, ok to proceed with validating and creating a
        # user account.
        if response == "":
            response = CreateUser().create(uid=username,
                                        email=email,
                                        pwd=password)
            self.render("signup.html", response = response)
        if response=="":
            # Set a cookie with the new user ID and its hash
            self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % str(make_secure_val(username)))

        # If no errors, redirect to the welcome page. Otherwise show signup
        # page and any errors.
        if response == "":
            self.redirect('/welcome')
        else:
            self.render("signup.html", response = response)



# Class for validating user id
class LoginHandler(Handler):
    def get(self):
        # If user is already logged in, redirect them to welcome page
        username = self.request.cookies.get('name')
        if username and username!="":
            self.redirect("/welcome")
        else:
            self.render("login.html", response = "")

    def post(self):
        # Check Database for existing user

        # Gql does not support OR statements in the WHERE clause, need two
        # separate queries to make sure both UID and email are not yet
        # registered.

        response = ""
        uid=self.request.get('username')
        pwd=self.request.get('password')

        if uid !="" and pwd!="":

            # UID must be hashed because it is stored as a hash value in the
            # database.
            data=db.GqlQuery("SELECT * FROM Users WHERE user_name = '" + hash_str(uid) + "'")

            # If there was an entry for the UID attempt to log in
            if data.get():
                if hash_str(uid) == data.get().user_name:
                    if hash_str(pwd) == data.get().password:
                        self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % str(make_secure_val(uid)))
                        self.redirect('/welcome')
                    else:
                        response += "Incorrect password"
            else:
                self.redirect('/signup')
        else:
            response += "Please enter a username and passowrd"

        self.render("login.html",response=response)



# Class for validating user id
class LogoutHandler(Handler):
    def get(self):
        # If user is already logged in, redirect them to welcome page
        username = self.request.cookies.get('name')
        if username and username != "":
            # expiration = "Thu, 01-Jan-1970 00:00:10 GMT"
            # self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/; Expires=%s' % (str(make_secure_val(username)), expiration))
            self.response.headers.add_header('Set-Cookie', 'name=; Path=/;')
        self.redirect("/signup")



# Class for rendering the welcome page, checks for a valid cookie and if one
# does not exist, redirects to the signup page.
class WelcomeHandler(Handler):
    def get(self):
        username = self.request.cookies.get('name')
        if username and username!="":
            self.render("welcome.html", username = check_secure_val(username))
        else:
            self.redirect('/signup')



class MainHandler(Handler):
    def render_front(self, title="", article="", error=""):
        articles = db.GqlQuery("SELECT * FROM Entry "
                            "ORDER BY created DESC LIMIT 10")
        self.render("main.html",title=title, article=article, error=error, articles = articles)

    def get(self):
        self.render_front()



class NewPostHandler(Handler):
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
            a = Entry(title=title, article=article, parent=blog_key())
            a.put()
            url = "/post/" + str(a.key().id())
            self.redirect(url)
        else:
            error = "You need to include both a title and an article"
            self.render_front(title,article,error)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Entry', int(post_id),parent=blog_key())
        data = db.get(key)

        title= data.title
        article= data.article
        date=data.created.date().strftime('%A, %B %d, %Y')
        self.render("postpermalink.html", title=title,article=article, date="")



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/welcome', WelcomeHandler),
    ('/signup', SignUpHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/newpost', NewPostHandler),
    (r'/post/([0-9]+)', PostHandler)
], debug=True)
