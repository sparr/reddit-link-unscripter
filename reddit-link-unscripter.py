#!/usr/bin/python

# This script uses reddit_api to fetch posts and comments from reddit.com.
# When it finds a link to a website that requires javascript to view, it
# replies with an alternate link that does not require javascript.
# example link in a comment: http://twitter.com/#!/foobar
# example alternative link:  http://m.twitter.com/foobar

import reddit
import time
import re
import urllib2
import socket

from exception_handler import ExpHandler

import pprint

r = reddit.Reddit(user_agent='reddit-link-unscripter')
print r
r.login() # credentials are in reddit_api.cfg
print r

banned_subreddits = set()
    
# this function isn't used yet
# it will handle multiple domains / URL patterns
def process_submission(submission):
    # loop through the list of URL patterns
    if phrase in comment.body:
        True
    # reply with a modified URL if there's a match

#TODO: handle network failures here
def post_comment(parent,comment):
    result = parent.add_comment(comment)
    return result

def persistent_post_comment(parent,comment,retries=5,debug=False):
    result = None
    while retries >= 0:
        try:
            if debug:
                print "debug: comment: " + comment
            else:
                print "comment: " + comment
                result = post_comment(parent,comment)
        except reddit.errors.RateLimitExceeded as e:
            pprint.pprint(vars(e))
            print "Rate limited for " + str(e.sleep_time) + " seconds at " + time.strftime("%H:%M:%S", time.gmtime()) + ", sleeping"
            time_left = e.sleep_time
            if time_left < 60:
                time_left += 1
            while time_left > 0:
                if time_left >= 60:
                    time.sleep(60)
                    time_left -= 60
                else:
                    time.sleep(time_left)
                    time_left = 0
                if time_left > 0:
                    print str(time_left) + " seconds left to sleep"
            retries -= 1
            continue
        except urllib2.HTTPError as e:
            print e.__module__,'.',e.__class__.__name__,':',e
            pprint.pprint(vars(e))
            print e.headers
            print "code: " + str(e.code)
            if e.code == 403:
                print "HTTP 403, aborting this attempt, marking " + str(parent.subreddit) + " as a banned subreddit"
                banned_subreddits.add(str(parent.subreddit))
                return None
            else:
                print e.readlines()
                print "retrying " + str(retries) + " more times, after 5 seconds"
                time.sleep(5)
                retries -= 1
            continue
        except reddit.errors.NotLoggedIn as e:
            print e.__module__,'.',e.__class__.__name__,':',e
            pprint.pprint(vars(e))
            if e.error_type == "USER_REQUIRED":
                print "We've been logged out, logging back in!"
                r.login()
                time.sleep(5)
                retries -= 1
            continue
        except reddit.errors.APIException as e:
            print e.__module__,'.',e.__class__.__name__,':',e
            pprint.pprint(vars(e))
            if e.error_type == "DELETED_LINK":
                print "Deleted link, aborting this attempt"
                return None
            else:
                print "retrying " + str(retries) + " more times, after 5 seconds"
                time.sleep(5)
                retries -= 1
            continue
        except Exception as e:
            print e.__module__,'.',e.__class__.__name__,':',e
            pprint.pprint(dir(e))
            pprint.pprint(vars(e))
            print "retrying " + str(retries) + " more times, after 5 seconds"
            time.sleep(5)
            retries -= 1
            continue
        break
    return result


# this is the main function, it loops forever
def link_unscripter():
    commented_count = 0
    post_time_mark = 0
    
    # fetch our inbox, find subreddits we are banned from in advance
    my_inbox = None
    try:
        my_inbox = r.user.get_inbox()
    except:
        #TODO: handle some exceptions here!
        raise
    if (my_inbox):
        for m in my_inbox:
            s = re.match("you have been banned from posting to \[.*\]\(/r/(.*)/\)\.",m.body)
            if (s != None):
                banned_subreddits.add(s.group(1))
    

    # fetch our last comment, which will dictate how far back we go on the first pass
    my_comments = None
    try:
        my_comments = r.get_content("http://www.reddit.com/user/link-unscripter/comments.json",25,{'sort':'new'})
    except:
        #TODO: handle some exceptions here!
        raise

        #TODO: handle comments on comments
    for c in my_comments:
        if c.submission.created_utc > post_time_mark:
            print "new mark, " + str(time.time() - c.submission.created_utc) + " seconds in the past, for " + str(c.submission)
            post_time_mark = c.submission.created_utc

    print "banned subreddits: "
    for s in banned_subreddits:
        print s
    
    # fetch new submissions, check them, reply
    while True:
        
        
        submissions = None
        # right now we are just pulling twitter link posts
        submissions = r.get_content("http://www.reddit.com/domain/twitter.com/new.json",25,{'sort':'new'})

        retrieved_count = 0
        new_time_mark = post_time_mark
        print "Starting loop at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + " with post_time_mark of " + str(time.time() - post_time_mark) + " seconds in the past"
        try:
            for s in submissions:
                retrieved_count += 1
                if str(s.subreddit) in banned_subreddits:
                    continue
                # skip posts older than our previous "newest post" timestamp
                if s.created_utc <= post_time_mark:
                    continue
                print "We are currently considering a post that is " + str(time.time() - s.created_utc) + " seconds old, from " + str(s.subreddit)
                new_url = re.sub('(https?://)(?:www.)?(twitter.com/)(?:#!/)?(.*)',r'\1m.\2\3',s.url)
                if new_url == s.url:
                    continue
                comment = new_url + "  \nThis mobile twitter link will work without requiring javascript.  \nThis comment generated by an [automated bot](/r/link_unscripter)."
                result = persistent_post_comment(s,comment)
                if result == None:
                    print "failed to comment on " + s.name
                    if s.created_utc > new_time_mark:
                        print "New time mark, " + str(s.created_utc)
                        new_time_mark = s.created_utc
                    continue
                else:
                    #TODO: handle failures like being banned here
                    print "commented on " + s.name
                    #pprint.pprint(vars(result))
                    print "original URL: " + s.url
                    print "replaced URL: " + new_url
                    commented_count += 1
                    if s.created_utc > new_time_mark:
                        print "New time mark, " + str(s.created_utc)
                        new_time_mark = s.created_utc
                print "sleeping for 5 seconds, interrupt if you must"
                time.sleep(5) 
        except (NameError, TypeError) as e:
            print e.__class__.__name__,':',e
            pprint.pprint(dir(e))
            pprint.pprint(vars(e))
            break
        except socket.timeout as e:
            print e.__module__,'.',e.__class__.__name__,':',e
            pprint.pprint(dir(e))
            pprint.pprint(vars(e))
            print "Timeout"
        except Exception as e:
            print e.__module__,'.',e.__class__.__name__,':',e
            pprint.pprint(dir(e))
            pprint.pprint(vars(e))
            print "Main loop failed with an exception, delaying 5 minutes before retrying"
            time.sleep(300)

        print str(retrieved_count) + " submissions considered at " + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        print str(commented_count) + " submissions replied to so far this run"

        post_time_mark = new_time_mark
        
        # sleep for 30 seconds between refreshes of the same page request, per the API rules
        print "sleeping"
        time.sleep(30)

if __name__=="__main__":
    link_unscripter()