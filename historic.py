import tweepy

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
tweets = api.user_timeline(screen_name='elonmusk',
                           # 200 is the maximum allowed count
                           count=1,
                           include_rts=False,
                           # Necessary to keep full_text
                           # otherwise only the first 140 words are extracted
                           tweet_mode='extended'
                           )

print(tweets[0].full_text)

#for tweet in tweets:
#    print(tweet.created_at, tweet.full_text)
#print(len(tweets))