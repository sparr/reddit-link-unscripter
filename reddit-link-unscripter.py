#!/usr/bin/python

# This script uses reddit_api to fetch posts and comments from reddit.com.
# When it finds a link to a website that requires javascript to view, it
# replies with an alternate link that does not require javascript.
# example link in a comment: http://twitter.com/#!/foobar
# example alternative link:  http://m.twitter.com/foobar

import reddit
import time
import re

r = reddit.Reddit(user_agent='reddit-link-unscripter')
print r
r.login() # credentials are in reddit_api.cfg
print r
    
# this function isn't used yet
# it will handle multiple domains / URL patterns
def process_submission(submission):
    # loop through the list of URL patterns
    if phrase in comment.body:
        True
    # reply with a modified URL if there's a match

place_holder = None

# fetch new submissions, check them, reply
while True:
    submissions = None
    # right now we are just pulling twitter link posts
    if place_holder is None:
        submissions = r.get_content("http://www.reddit.com/domain/twitter.com/new.json",1,[('sort','new')])
    else:
        submissions = r.get_content("http://www.reddit.com/domain/twitter.com/new.json",20,[('sort','new')],place_holder)

    # there is probably a way to use the generator directly, I will investigate that
    submission_list = list(submissions)

    print str(len(submission_list)) + " submissions retrieved at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

    if len(submission_list) > 0:
        for s in submission_list:
            # stop if we get to the first post from the previous list
            if s.name == place_holder:
                break
            new_url = re.sub('(https?://)(?:www.)?(twitter.com/)#!?/(.*)',r'\1m.\2\3',s.url)
            if new_url != s.url:
                s.add_comment('This [mobile twitter link](' + new_url + ') does not require javascript to view.')
                print "commented on " + s.name
                print "original URL: " + s.url
                print "replaced URL: " + new_url

        # remember the newest post we saw in this list
        place_holder = submission_list[0].name

    # sleep for 30 seconds between refreshes of the same page request, per the API rules
    print "sleeping"
    time.sleep(30)
