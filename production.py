import tweepy
import time
from fs.ftx import FtxClient
from datetime import datetime
import os

def main():
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_token = os.environ['ACCESS_TOKEN']
    access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    last_tweet = 'none'
    client = FtxClient()
    leverage = 5
    stop_trigger = 0.03
    stop_val = 0.035

    while True:
        try:
            tweets = api.user_timeline(screen_name='elonmusk',
                                       # 200 is the maximum allowed count
                                       count=1,
                                       include_rts=False,
                                       # Necessary to keep full_text
                                       # otherwise only the first 140 words are extracted
                                       tweet_mode='extended'
                                       )
        except:
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
        try:
            text = tweets[0].full_text.lower()
            created_at = tweets[0].created_at
            print(created_at, text)
            if ('doge' in text) and (text != last_tweet):
                try:
                    balances = client.get_balances()[0]['availableWithoutBorrow']
                except:
                    client = FtxClient()
                    balances = client.get_balances()[0]['availableWithoutBorrow']
                size = balances * leverage
                #Market in - 5x long
                client.place_order('DOGE-PERP', side='buy', size=size, price=None, post_only=False)
                #Get entry price
                price = client.get_positions()[0]['entryPrice']
                #Stop
                client.place_conditional_order('DOGE-PERP', side='sell', size=size, type='stop', trigger_price=(1-stop_trigger/leverage)*price,
                                                       limit_price=(1 - stop_val/leverage) * price, reduce_only=True)
                now = datetime.now()
                print(f'({now}) Longed doge at {price}')
                last_tweet = text
                #Close after 5 minutes
                time.sleep(5*60)
                positions = client.get_positions()
                position_size = positions[0]['size']
                open_positions = position_size > 0
                if open_positions:
                    #market out
                    client.place_order('DOGE-PERP', side='sell', size=position_size, price=None, post_only=False, reduce_only=True)
                    client.cancel_orders('DOGE-PERP', conditional_orders=True)
            time.sleep(60)
        except:
            print('Tweet not found. Possible API ban')

if __name__ == '__main__':
    main()



