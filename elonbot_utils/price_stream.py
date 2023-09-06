from multiprocessing import Process, Pipe
from client import FtxWebsocketClient
import time
import pandas as pd
pd.options.display.max_columns = None

def f(child_conn):
    client = FtxWebsocketClient()
    while True:
        # response = client.get_orderbook('DOGE-PERP')
        try:
            response = client.get_ticker('DOGE-PERP')
            last = response['last']
            time.sleep(0.5)
            child_conn.send(last)
        except:
            pass