import tweepy
import csv
import tweets as pre_tweets
from urllib import request

# gets media from tweets that have media
def get_media(tweets_to_save):

    # check for tweets that have media and save them urls to tweets_media_urls
    tweets_media_urls = {}
    for tweet in tweets_to_save:
        if hasattr(tweet, 'extended_entities'):
            if 'media' in tweet.extended_entities:
                tweets_media_urls[tweet.id_str] = []
                for media_item in tweet.extended_entities['media']:
                    if media_item['type'] == 'animated_gif' or media_item['type'] == 'video':
                        tweets_media_urls[tweet.id_str].append(media_item['video_info']['variants'][0]['url'])
                    else:
                        tweets_media_urls[tweet.id_str].append(media_item['media_url_https'])

    # save media to media folder
    for tweet_media_urls in tweets_media_urls:
        if len(tweets_media_urls[tweet_media_urls]) > 1:
            media_count = 1
            for media_in_tweet in tweets_media_urls[tweet_media_urls]:
                # file name is tweet number + index of the media + file_extension (right now you can't upload more
                # than 1 gif in a tweet, so it's a bit redundant, but might save me some time in the future
                f = open('media/' + tweet_media_urls+ '-' + str(media_count) + '.' + media_in_tweet[-3:], 'wb')
                f.write(request.urlopen(media_in_tweet).read())
                f.close()
                media_count += 1
        else:
            f = open('media/' + tweet_media_urls + '.' + tweets_media_urls[tweet_media_urls][0][-3:], 'wb')
            f.write(request.urlopen(tweets_media_urls[tweet_media_urls][0]).read())
            f.close()

def main():

    # twitter auth info
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # get already saved tweets into a list
    with open('saved_tweets.csv', 'r', encoding='utf-8') as f:
        csv_tweets = csv.reader(f)
        csv_tweets_list = []
        for row in csv_tweets:
            csv_tweets_list.append(row)
        if csv_tweets_list:
            del csv_tweets_list[0]

    # get ids of already saved tweets
    saved_tweets = [int(tweet[0]) for tweet in csv_tweets_list]
    # get a list of tweets
    all_tweets = pre_tweets.tweets
    # get ids of tweets (stored not as ids to allow easier embedding on site)
    tweets_ids = [int(tweet[tweet.find('/status/')+8:]) for tweet in all_tweets]
    # get ids of tweets to save
    tweets_ids_to_save = [tweet_id for tweet_id in tweets_ids if tweet_id not in saved_tweets]
    # get tweets that have not been deleted
    tweets_to_save = []
    for tweet in tweets_ids_to_save:
        try:
            tweets_to_save.append(api.get_status(tweet))
        except:
            print(tweet, 'was deleted!')

    # extract needed data from all_tweets. This is the data we need from new tweets
    tweets_info_to_save = [[tweet.id_str, tweet.author.screen_name, tweet.author.name, str(tweet.created_at), tweet.text] for tweet in tweets_to_save ]

    get_media(tweets_to_save)

    # write tweets to a file
    with open('saved_tweets.csv', 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f, lineterminator='\n')
        header = ['id', 'created_at', 'screen_name', 'name', 'text']
        csv_writer.writerow(header)
        csv_writer.writerows(sorted(csv_tweets_list + tweets_info_to_save, key=lambda x: int(x[0])))

if __name__ == "__main__":
    main()