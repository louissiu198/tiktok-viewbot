from time import time
from httpx import Client, post
from random import choice, choices, randint, randbytes
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, wait
import string

domain_server   = "api-va.tiktokv.com" # replace with any domain you want
script_setting  = {
    "retryCount": 6,
    "threadCount": 100
}

class Utils:
    @staticmethod
    def generate_header():
        return {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sdk-version': '2',
            'User-Agent': ''.join(choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=randint(13, 27))),
        }

    @staticmethod
    def services_payload(choice: str, videoid: str = None):
        if choice == "views":
            return f"item_id={videoid}&play_delta=1&request_id=0&aweme_type=0&order=0&pre_item_id=" 

class TikTok:
    def __init__(self, choice, amount, videoid):
        self.sent, self.fail, self.error, self.thread, self.videoid = 0, 0, 0, [], videoid
        self.endpoints = {
            "views": {"endpoints": "/aweme/v1/aweme/stats/?", "method": "POST"},
        }
        startTime = time()
        with ThreadPoolExecutor(max_workers = script_setting["threadCount"]) as executor:
            for _ in range(amount):
                self.thread.append(executor.submit(self.send_services, choice))
            wait(self.thread)
        endTime = round(time() - startTime)
        print(f"{self.sent, self.fail, self.error, endTime}")

    def send_services(self, types: str):
        client = Client(http2 = True, verify = False)
        for _ in range(script_setting['retryCount']):
            try:
                payload = Utils.services_payload(types, self.videoid)
                headers = Utils.generate_header() 

                resp = client.request(
                    self.endpoints[types]["method"],
                    f"https://{domain_server}" + self.endpoints[types]["endpoints"], 
                    data = payload,
                    headers = headers
                )
                # print(resp.text.strip())

                if types == "views" or types == "shares":
                    if "charset=utf-8" in str(resp.headers):
                        print("success")
                        self.sent += 1; break
                    else:
                        print("error")
                        self.fail += 1
            except Exception as e:
                print(e)
                self.error += 1
                continue

TikTok(choice = "views", amount = 1000, videoid = "7344621227987701025")
