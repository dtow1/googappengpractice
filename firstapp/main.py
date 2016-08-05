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

#
#   IMPORTANT - THIS CODE SHOULD NOT BE USED TO EVALUATE MY WORK
#
#   This code is from following allong the examples used in the
#   udacity full stack developer nano degree Intro to Backend course
#   I will likely add to it with my own ideas and exploration but it
#   will be 90+% follow along code.
#

import webapp2

form = """
<form method="post">
    What is your birthday?
    <br>
    <label> Month
        <input type="text" name="month">
    </label>
    <label> Day
        <input type="text" name="day">
    </label>
    <label> Year
        <input type="text" name="year"
    </label>

    <br>
    <br>
    <input type="submit">
</form>
"""

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # response represents the response that we will send back to the
        # client
        self.response.write(form)

    def post(self):
        self.response.out.write("Thanks! That is a valid day!")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
