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

def valid_month(month):
    months = ['January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December']
    if month.capitalize() in months:
        return month.capitalize()
    else:
        return None

# This function I wrote. I tend to be more pedantic in my code but wanted
# to see if I could do it in one line.

def valid_day(day):
    return  int(day) if (day.isdigit() and int(day) in range(1,32)) else None

def valid_year(year):
    return  int(year) if (year.isdigit() and int(year) in range(1900,2021)) else None

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # response represents the response that we will send back to the
        # client
        self.response.write(form)

    def post(self):
        user_month = valid_month(self.request.get('month'));
        user_day = valid_day(self.request.get('day'));
        user_year = valid_year(self.request.get('year'));

        if not (user_month and user_day and user_year):
            self.response.out.write(form)
        else:
           self.response.out.write("Thanks! That is a valid day!")




app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
