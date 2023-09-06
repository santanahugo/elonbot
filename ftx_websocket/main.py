from client import FtxWebsocketClient
import time
import pandas as pd
pd.options.display.max_columns = None

def main():
    client = FtxWebsocketClient()
    while True:
        #response = client.get_orderbook('DOGE-PERP')
        try:
            response = client.get_ticker('BTC-PERP')
            bid = response['bid']
            ask = response['ask']
            spread = response['ask'] - response['bid']
            last = response['last']
            print(bid, ask, spread, last, last - bid, last - ask)
            #print(type)
            #print(response)
            time.sleep(0.5)
        except:
            pass

if __name__=='__main__':
    main()