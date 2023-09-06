import requests
import os
import json
from .ftx import FtxClient
import time
from .price_stream import f
from multiprocessing import Process, Pipe

leverage = 5
stop_trigger = 0.045
stop = 0.05

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(headers, delete, bearer_token):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "from:elonmusk"},
        #{"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers, set, bearer_token):
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            text = json_response['data']['text'].lower()
            if 'doge' in text:
                # post order
                client = FtxClient()
                balance = client.get_balances()[0]['availableWithoutBorrow']
                if balance < 50:
                    print('Low balance. Halting execution...')
                    return 0
                price = parent_conn.recv()
                if isinstance(price, float):
                    print('Price: ', price)
                    size = balance*leverage/price
                    print('Size: ', size)
                    # Market buy
                    client.place_order('DOGE-PERP', side='buy', price=None, size=size)
                    # Stop loss
                    client.place_conditional_order('DOGE-PERP', side='sell', size=size, type='stop',
                                                   trigger_price=(1 - stop_trigger / leverage) * price,
                                                   limit_price=(1 - stop / leverage) * price, reduce_only=True)
                    #Wait 4 minutes then close
                    time.sleep(4.8*60)
                    client.place_order('DOGE-PERP', side='sell', price=None, size=size, reduce_only=True)
                else:
                    print('Price received is not a number')
            print('\nText: ', text)