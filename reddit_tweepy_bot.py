import praw
import tweepy
import time
import requests
import os
from os import environ

text_file_name = 'last_seen_id.txt'

auth = tweepy.OAuthHandler(environ['CONSUMER_KEY'], environ['CONSUMER_SECRET'])
auth.set_access_token(environ['ACCESS_KEY'], environ['ACCESS_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


reddit = praw.Reddit(client_id=environ['CLIENT_ID'],
                     client_secret=environ['CLIENT_SECRET'], user_agent=environ['USER_AGENT'])


def retrieve_text(file_name):
    file = open(file_name, 'r')
    text = str(file.read().strip())
    file.close()
    return text


def store_text(text, file_name):
    file = open(file_name, 'w')
    file.write(str(text))
    file.close()
    return


def download_img(url):
    print('Downloading image...')
    reddit_tweepy_bot_directory = os.path.dirname(__file__)
    short_directory = "image\imgdownload.jpg"
    abs_file_path = os.path.join(reddit_tweepy_bot_directory, short_directory)
    with open(abs_file_path, 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)
    print('Image downloaded.')
    return abs_file_path


def post_tweet(tweepy_api, author, link, img):
    img_path = download_img(img)
    tweepy_api.update_with_media(img_path, status=str(link) + ' - ' + str(author))
    os.remove(img_path)


def check_reddit(post, file_name, tweepy_api):
    last_id = retrieve_text(file_name)
    current_id = int(post.id, 36)
    id_link = post.id
    if  current_id > int(last_id):
        over_18 = post.over_18
        if not over_18:
            hint = post.__dict__.get('post_hint', None)
            if hint == 'image':
                author = post.author
                link = 'http://redd.it/' + id_link
                img = post.url
                print("It's a legit post, trying to tweet...")
                try:
                    post_tweet(tweepy_api, author, link, img)
                    print('Post tweeted.')
                except tweepy.TweepError as e:
                    print("Couldn't post image, something went wrong")
                    print(e.reason)
                print('Sleeping for 300 seconds...')
                time.sleep(300)
            else:
                print('Not an image, skipping...')
        else:
            print('+18 post, skipping...')
    else:
        print('Old post, sikkping')
    store_text(current_id, file_name)
    print('Post id updated, last seen id: ' + current_id)


def search_posts(file_name, tweepy_api):
    print('Searching for posts...')
    new_posts = reddit.subreddit('memes').new(limit=10)
    for post in new_posts:
        print('Found post id - ' + post.id)
        check_reddit(post, file_name, tweepy_api)


while 1:
    print('Running bot...')
    search_posts(text_file_name, api)
    time.sleep(300)