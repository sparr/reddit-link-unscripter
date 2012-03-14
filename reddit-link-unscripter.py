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

# fetch our last 100 comments, so we can try not to double-comment when starting up
my_comments = None
try:
    my_comments = r.get_content("http://www.reddit.com/user/" + r.config.user + "/comments.json",100)
except:
    pass
my_comment_parents = set(comment.parent_id for comment in my_comments)
    
place_holder = None
commented_count = 0

# fetch new submissions, check them, reply
while True:
    submissions = None
    # right now we are just pulling twitter link posts
    try:
        if place_holder is None:
            submissions = r.get_content("http://www.reddit.com/domain/twitter.com/new.json",10,{'sort':'new'})
        else:
            submissions = r.get_content("http://www.reddit.com/domain/twitter.com/new.json",100,{'sort':'new'},place_holder)

        retrieved_count = 0
        
        for s in submissions:
            retrieved_count += 1
            # stop if we get to the first post from the previous list
            # TODO: keep going in case we missed a post in a previous pass
            if s.name == place_holder:
                break
            if retrieved_count == 1:
                place_holder = s.name
            # stop if we already replied to this post
            if place_holder == None and s.name in my_comment_parents:
                #FIXME: some posts are still getting duplicate comments!
                print "Already commented on " + s.name
                continue
            new_url = re.sub('(https?://)(?:www.)?(twitter.com/)#!?/(.*)',r'\1m.\2\3',s.url)
            if new_url != s.url:
                try:
                    #print 'This [mobile twitter link](' + new_url + ') does not require javascript to view.'
                    s.add_comment('This [mobile twitter link](' + new_url + ') does not require javascript to view.')
                    #FIXME: some posts are still getting duplicate comments!
                    my_comment_parents.add(s.name)
                    print "commented on " + s.name
                    print "original URL: " + s.url
                    print "replaced URL: " + new_url
                    commented_count += 1
                except:
                    pass

        print str(retrieved_count) + " submissions considered at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        print str(commented_count) + " submissions replied to so far this run"

    except:
        # if the request failed, try again
        print "Failed to retrieve post list"
        pass

    # sleep for 30 seconds between refreshes of the same page request, per the API rules
    print "sleeping"
    time.sleep(30)
