# Copyright (c) 2014 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from random import random
import requests
import pymongo
import blogPostDAO
import mClassDAO
import pointsDAO
import sessionDAO
import pictureDAO
import dataDAO
import putsDAO
import modelDAO
import userDAO
import bottle
import cgi
import re
import json
#from gevent import monkey; monkey.patch_all()
from time import time
from time import sleep;
import time
import threading
import thread
import logInfo
from logInfo import logInfo
from mClassDAO import mClasses, currMClass
import computerValueDAO

#betting_variables = {}
#for mClass in mClasses:
#    betting_variables[mClass] = mClasses[mClass]['bettingVar']

#Periods should be determined by the following:
#int(120-round(time()%120))

#the following will allow me to build graphs from the json strings that are
#sent back when the model is build.

from bayesian.bbn import build_bbn_from_conditionals as build_graph
from bayesian.bbn import *
#here is the true model, which is a constant (the simulated truth)
'''TRUTH = {
        "prize_door": [
            # For nodes that have no parents
            # use the empty list to specify
            # the conditioned upon variables
            # ie conditioned on the empty set
            [[], {"A": float(1)/3, "B": float(1)/3, "C": float(1)/3}]],
        "contestant_door": [
            [[], {"A": float(1)/3, "B": float(1)/3, "C": float(1)/3}]],
        "monty_door": [
            [[["prize_door", "A"], ["contestant_door", "A"]], {"A": 0, "B": 0.5, "C": 0.5}],
            [[["prize_door", "A"], ["contestant_door", "B"]], {"A": 0, "B": 0, "C": 1}],
            [[["prize_door", "A"], ["contestant_door", "C"]], {"A": 0, "B": 1, "C": 0}],
            [[["prize_door", "B"], ["contestant_door", "A"]], {"A": 0, "B": 0, "C": 1}],
            [[["prize_door", "B"], ["contestant_door", "B"]], {"A": 0.5, "B": 0, "C": 0.5}],
            [[["prize_door", "B"], ["contestant_door", "C"]], {"A": 1, "B": 0, "C": 0}],
            [[["prize_door", "C"], ["contestant_door", "A"]], {"A": 0, "B": 1, "C": 0}],
            [[["prize_door", "C"], ["contestant_door", "B"]], {"A": 1, "B": 0, "C": 0}],
            [[["prize_door", "C"], ["contestant_door", "C"]], {"A": 0.5, "B": 0.5, "C": 0}],
        ]
    }

g = build_bbn_from_conditionals(TRUTH);

results=g.query();

#samples = g.draw_samples(results, 1000);
'''

__author__ = 'johannes castner'

#because the above does nt yet work, for now, I'm using the below code to generate data:

# make treatments; (data generation and budget constraints)

# Now we leave out the "prize_door" value for the last member in the sequence. This is the one players bet on. This value comes in, when the timer runs out.

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.blog
mClass = mClassDAO.mClassDAO(database)
pictures=pictureDAO.PictureDAO(database)
posts = blogPostDAO.BlogPostDAO(database)
puts  = putsDAO.PutsDAO(database)
users = userDAO.UserDAO(database)
models=modelDAO.ModelDAO(database)
sessions = sessionDAO.SessionDAO(database)
data = dataDAO.DataDAO(database)
points=pointsDAO.PointsDAO(database)
cvd = computerValueDAO.ComputerValueDAO(database)
# General Discussion on structure. This program implements a blog. This file is the best place to start to get
# to know the code. In this file, which is the controller, we define a bunch of HTTP routes that are handled
# by functions. The basic way that this magic occurs is through the decorator design pattern. Decorators
# allow you to modify a function, adding code to be executed before and after the function. As a side effect
# the bottle.py decorators also put each callback into a route table.

# These are the routes that the blog must handle. They are decorated using bottle.py
# This route is the main page of the blog

@bottle.route("/clock")
def get_time():
    return data.getTimeUntilTwoMinuteMark()

free_period = True
@bottle.route("/beginFreePeriod")
def beginFreePeriod():
    global free_period
    free_period = True
    cookie = bottle.request.get_cookie("session")
    user_id = sessions.get_username(cookie)
    admin_users = []
    return user_id

@bottle.route("/endFreePeriod")
def endFreePeriod():
    global free_period
    free_period = False
    cookie = bottle.request.get_cookie("session")
    user_id = sessions.get_username(cookie)
    admin_users = []
    return user_id

@bottle.route("/hasNewData/<model_class>/<period>")
def hasNewData(model_class, period):
    latest_period = data.get_latest_period(model_class)
    if latest_period > int(period):
        return '1'
    else:
        return '0'

@bottle.route("/isFreePeriod")
def isFreePeriod():
    return {"free_period": free_period}

demo_mode = True
@bottle.route("/endDemo")
def end_demo():
    global demo_mode
    demo_mode = False
    cookie = bottle.request.get_cookie("session")
    user_id = sessions.get_username(cookie)
    admin_users = []
    return user_id

@bottle.route("/emptyData")
def empty_mclasses():
    mClass.empty_data()
    return

@bottle.route("/beginDemo")
def reset_demo():
    global demo_mode
    demo_mode = True
    cookie = bottle.request.get_cookie("session")
    user_id = sessions.get_username(cookie)
    admin_users = []
    return user_id

@bottle.route("/pointsRefresh/<user>")
def points_refresh(user):
    point_object=points.get_points(user)
    return json.dumps({"points": point_object["points"], "shares":point_object["shares"]})

@bottle.route("/calls/<treatmentNum>/<period>")
def blog_index(treatmentNum, period):

    cookie = bottle.request.get_cookie("session")

    username = sessions.get_username(cookie)

    # even if there is no logged in user, we can show the blog
    l = posts.get_posts(int(treatmentNum), int(period), demo_mode)

    #print "printing myposts: " +str(l);
    return json.dumps(dict(myposts=l, username=username))

# adding user_id
@bottle.route("/puts/<treatmentNum>/<period>")
def blog_index(treatmentNum, period):

    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)

    # even if there is no logged in user, we can show the blog
    l = puts.get_puts(int(treatmentNum), int(period), demo_mode)
    #print "printing myposts: " +str(l);
    return json.dumps(dict(myputs=l, username=username))

@bottle.route("/query/<i>/<path:path>")
def query(i, path):
    query_dict=dict(tuple(elem.split(':')) for elem in path.split("/"))
    return models.query(_id=i, conditions=query_dict)

@bottle.route("/hello/<user_id>")
def blog_index(user_id):
    return "hello world"

@bottle.route("/truth/<user_id>")
def blog_index(user_id):
    # if mClass.user_needs_updating(user_id):
    #     mClass.assign_mClass(user_id)
    # model_name = mClass.get_user_mClass(user_id)

    #group_id = mClass.assign_group_if_not_already(user_id)
    #model_name, points_assigned = mClass.get_group_treatment(group_id)

    treatmentNum, model_name, points_assigned = mClass.assign_treatment_if_not_already(user_id)
    points.insert_entry(user_id, points_assigned, 1)
    #model_name = currMClass

    if demo_mode:
        model_name = "simple"

    model_class = {
        'model_name': model_name,
        'betting_variable': mClasses[model_name]["bettingVar"],
        'vars': mClasses[model_name]["vars"],
        'domain': mClasses[model_name]["domain"]
    }
    if user_id in set(["121211", "100006471334363"]):
        isAdmin=True
    else:
        isAdmin=False

    samples = data.get_first_twenty(model_class)
    retData = {'model_class': model_class,
               'isAdmin': isAdmin,
               'samples': samples,
               'points': points_assigned,
               'treatmentNum': treatmentNum,
               }
    return json.dumps(retData)

'''@bottle.post('/newData')
def post_new_data():
    data.add_data([random_monty()])
    return'''

@bottle.route("/newData/<treatmentNum>" )
def index(treatmentNum):
    #newMClassAssigned = False
    #if mClass.user_needs_updating(user_id):
    #    mClass.assign_mClass(user_id)
    #    newMClassAssigned = True
    #model_name = mClass.get_user_mClass(user_id)
    #model_name = currMClass

    model_name, _ = mClass.get_treatment_from_num(int(treatmentNum))
    if demo_mode:
        model_name = "simple"

    model_class = {
        'model_name': model_name,
        'betting_variable': mClasses[model_name]["bettingVar"],
        'vars': mClasses[model_name]["vars"],
    }
    samples = data.get_newest(model_class)
    retData = samples
    #retData = {'samples': samples}
    #if newMClassAssigned:
    #    retData['newModelClass'] = model_class;
    #else:
    #    retData['newModelClass'] = None

    return json.dumps(retData)

@bottle.post("/accept_put/<put_id>/<accepter_id>/<poster_id>")
def accept_put(put_id, accepter_id,poster_id):
    postAll= bottle.request.json

    point_count = postAll["points"]
    puts.accept_put(put_id, accepter_id)
    points.accept_put(poster_id, accepter_id, point_count)
# used to insert a person's facebook picture in the mongodb database. 
    return json.dumps({})

@bottle.post("/accept_call/<call_id>/<accepter_id>/<poster_id>")
def accept_call(call_id, accepter_id,poster_id):
    postAll= bottle.request.json
    point_count = postAll["points"]
    posts.accept_call(call_id, accepter_id)
    points.accept_call(poster_id, accepter_id, point_count)
    return json.dumps({})

#@bottle.post("/new_user_points/<user_id>")
#def enter_new_user_points(user_id):
#    points.insert_entry(user_id, 1000, 10)

@bottle.post('/picture')
def post_new_picture():
    postAll= bottle.request.json
    name = postAll["id"]
    url = postAll["url"]
    width=postAll['width']
    height=postAll['height']
    pictures.add_picture(name, url, width, height)
    return json.dumps({})

@bottle.route("/picture/<id>/<width>/<height>")
def index(id, width, height):
    path=pictures.get_newest(id, width, height)
    bottle.response.content_type = 'image/jpeg'
    return requests.get(path).content

# used to process a comment on a blog post
@bottle.post('/newcomment')
def post_new_comment():
    postAll= bottle.request.json
    commentId=postAll["commentId"]
    name = postAll["commentName"]
    email = postAll["commentEmail"]
    body = postAll["commentBody"]
    id = postAll["id"]
    permalink = postAll["permalink"]
    post = posts.get_post_by_id(id)
    cookie = bottle.request.get_cookie("session")
    username = sessions.get_username(cookie)
    # it all looks good, insert the comment into the blog post and redirect back to the post viewer
    posts.add_comment(id, name, email, body, commentId)
    return json.dumps({})

#
# Post handler for setting up a new post.
# Only works for logged in user.
@bottle.post('/newpost')
def post_newpost():
    postAll= bottle.request.json
    title= postAll['subject'];
    post=postAll['price'];
    comments=postAll['comments']
    username=postAll['username']
    userid=postAll['userid']
    #variable=postAll["variable"]
    treatmentNum = postAll['treatmentNum']
    period=postAll["period"]
    # extract tags
    #tags = cgi.escape(tags)
    tags_array = [] #extract_tags(tags)
    opend=postAll['open']
    # looks like a good entry, insert it escaped
    escaped_post = cgi.escape(post, quote=True)

    # substitute some <p> for the paragraph breaks
    newline = re.compile('\r?\n')
    formatted_post = newline.sub("<p>", escaped_post)
    #formatted_post

    permalink = posts.insert_entry(title, formatted_post, comments, tags_array, username, userid, treatmentNum, period, opend)

    #computerShareValue = cvd.getComputerValue()
    #print "formatted_post: ", formatted_post
    #print "formatted isinstance ", isinstance(formatted_post, int)
    #pointVal = int(formatted_post)
    #if pointVal > computerShare:
    #    points.computer_accept_call(userid, pointVal)
    #    posts.computer_accept()

    return json.dumps({})

@bottle.post('/newput')
def post_newpost():
    postAll= bottle.request.json
    title= postAll['subject'];
    post=postAll['price'];
    comments=postAll['comments']
    username=postAll['username']
    userid=postAll['userid']
    # variable=postAll["variable"]
    treatmentNum = postAll['treatmentNum']
    period=postAll["period"]
    # extract tags
    #tags = cgi.escape(tags)
    tags_array = [] #extract_tags(tags)
    opend=postAll['open']
    # looks like a good entry, insert it escaped
    escaped_post = cgi.escape(post, quote=True)

    # substitute some <p> for the paragraph breaks
    newline = re.compile('\r?\n')
    formatted_post = newline.sub("<p>", escaped_post)

    permalink = puts.insert_entry(title, formatted_post, comments, tags_array, username, userid, treatmentNum, period, opend)

    #computerShareValue = cvd.getComputerValue()
    #print "formatted_post: ", formatted_post
    #print "formatted isinstance ", isinstance(formatted_post, int)
    #pointVal = int(formatted_post)
    #if pointVal > computerShare:
    #    computer_accept_put(userid, pointVal)

    return json.dumps({})

# handles a login and places the time stamped data in the database. 
@bottle.post('/login')
def process_login():
    user= bottle.request.json
    username= user['id'];
    users.add_user(user);
        # username is stored in the user collection in the _id key
    session_id = sessions.start_session(username)

    if session_id is None:
        print "Error: there is no session id!!" 

    cookie = session_id
        # Warning, if you are running into a problem whereby the cookie being set here is
        # not getting set on the redirect, you are probably using the experimental version of bottle (.12).
        # revert to .11 to solve the problem.
    #print bottle.response.set_cookie;
    bottle.response.set_cookie("session", cookie)
    return json.dumps({})

@bottle.post('/model')
def building_model():
    model = bottle.request.json
    user = model['id'];
    models.add_model(model)
    return json.dumps({})

@bottle.route("/has_query/<_id>")
def blog_index(_id):

    # even if there is no logged in user, we can show the blog

    return json.dumps(models.has_query(_id))


@bottle.get('/user/:id/photo')
def get_photo():
    return requests.get(db.getUser(id).photo_url)


@bottle.get('/internal_error')
@bottle.view('error_template')
def present_internal_error():
    return {'error':"System has encountered a DB error"}

#######################

# Helper Functions

#extracts the tag from the tags form element. an experience python programmer could do this in  fewer lines, no doubt
def extract_tags(tags):

    whitespace = re.compile('\s')

    nowhite = whitespace.sub("",tags)
    tags_array = nowhite.split(',')

    # let's clean it up
    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)

    return cleaned

# validates that the user information is valid for new signup, return True of False
# and fills in the error string if there is an issue
def validate_signup(username, verify, email, errors):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

    errors['username_error'] = ""
    errors['verify_error'] = ""
    errors['email_error'] = ""

    if not USER_RE.match(username):
        errors['username_error'] = "invalid username. try just letters and numbers"
        return False

    if email != "":
        if not EMAIL_RE.match(email):
            errors['email_error'] = "invalid email address"
            return False
    return True

def json_convert(query):
    """
    function used to convert queries into useful json files
    that can be served by bottle and imported into the game
    using ajax.
    """
    d={k[0]:{} for k in query.keys()}
    [d[k[0]].update({k[1]:r}) for k, r in query.items()]
    return json.dumps(d)

bottle.debug(True)
bottle.run(host='localhost', port=8080)         # Start the webserver running and wait for requests

