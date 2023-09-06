import requests
import os
import json
from elonbot_utils.stream import *


def main():
    bearer_token = os.environ.get("BEARER_TOKEN")
    #print(bearer_token)
    headers = create_headers(bearer_token)
    rules = get_rules(headers, bearer_token)
    delete = delete_all_rules(headers, bearer_token, rules)
    set = set_rules(headers, delete, bearer_token)
    get_stream(headers, set, bearer_token)


if __name__ == "__main__":
    main()

