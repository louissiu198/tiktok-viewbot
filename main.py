from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore
import urllib.parse
import threading
import requests
import binascii
import hashlib
import random
import time
import json
import ssl
import os 

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

Option = False
devices = open("devices.txt").read().splitlines()
domains = open("domains.txt").read().splitlines()

seconds = 0
success = 0
failed = 0
errors = 0
counts = 0
proxy = 0

class signature:
    def __init__(self, params: str, data: str, cookies: str) -> None:
        self.params = params
        self.data = data
        self.cookies = cookies
    def hash(self, data: str) -> str:
        return str(hashlib.md5(data.encode()).hexdigest())
    def get_base_string(self) -> str:
        base_str = self.hash(self.params)
        base_str = (base_str + self.hash(self.data) if self.data else base_str + str("0" * 32))
        base_str = (base_str + self.hash(self.cookies) if self.cookies else base_str + str("0" * 32))
        return base_str
    def get_value(self) -> json:
        return self.encrypt(self.get_base_string())
    def encrypt(self, data: str) -> json:
        unix = time.time()
        len = 0x14
        key = [0xDF,0x77,0xB9,0x40,0xB9,0x9B,0x84,0x83,0xD1,0xB9,0xCB,0xD1,0xF7,0xC2,0xB9,0x85,0xC3,0xD0,0xFB,0xC3,]
        param_list = []
        for i in range(0, 12, 4):
            temp = data[8 * i : 8 * (i + 1)]
            for j in range(4):
                H = int(temp[j * 2 : (j + 1) * 2], 16)
                param_list.append(H)
        param_list.extend([0x0, 0x6, 0xB, 0x1C])
        H = int(hex(int(unix)), 16)
        param_list.append((H & 0xFF000000) >> 24)
        param_list.append((H & 0x00FF0000) >> 16)
        param_list.append((H & 0x0000FF00) >> 8)
        param_list.append((H & 0x000000FF) >> 0)
        eor_result_list = []
        for A, B in zip(param_list, key):
            eor_result_list.append(A ^ B)
        for i in range(len):
            C = self.reverse(eor_result_list[i])
            D = eor_result_list[(i + 1) % len]
            E = C ^ D
            F = self.rbit_algorithm(E)
            H = ((F ^ 0xFFFFFFFF) ^ len) & 0xFF
            eor_result_list[i] = H
        result = ""
        for param in eor_result_list:
            result += self.hex_string(param)
        return {
            "x-ss-req-ticket": str(int(unix * 1000)),
            "x-khronos": str(int(unix)),
            "x-gorgon": ("840480e90000" + result),  
        }
    def rbit_algorithm(self, num):
        result = ""
        tmp_string = bin(num)[2:]
        while len(tmp_string) < 8:
            tmp_string = "0" + tmp_string
        for i in range(0, 8):
            result = result + tmp_string[7 - i]
        return int(result, 2)

    def hex_string(self, num):
        tmp_string = hex(num)[2:]

        if len(tmp_string) < 2:
            tmp_string = "0" + tmp_string
        return tmp_string

    def reverse(self, num):
        tmp_string = self.hex_string(num)
        return int(tmp_string[1:] + tmp_string[:1], 16)

class TikTok:                       
    @staticmethod
    def GenerateBanner():
        print(""" _____ _ _    ____        _
|_   _(_) | _| __ )  ___ | |_
  | | | | |/ /  _ \ / _ \| __|
  | | | |   <| |_) | (_) | |_
  |_| |_|_|\_\____/ \___/ \__|
        """)
        print(Fore.LIGHTRED_EX + "                  Tiktok Viewbot")
        print(Fore.LIGHTRED_EX + "                  v9 Beta")
        print(f"{Fore.RESET}")
        print("")

    @staticmethod
    def GenerateChecks():
        global counts, success, seconds 
        while True:
            counts += 1
            seconds = round(success/counts)
            time.sleep(1)

    @staticmethod
    def GenerateScreen(choiceId):
        if choiceId == "1":
            TikTok.GenerateBanner()
        elif choiceId == "2":
            while True:
                os.system(f"title TikBot - Devices: {str(len(devices))}  Seconds:{seconds}  Success: {success}  Failed: {failed}  Script Errors: {errors}  Proxy Errors: {proxy}")

    @staticmethod
    def GenerateParams(deviceInfo, deviceType):
        return {
            "iid":deviceInfo["install_id"],
            "device_id":deviceInfo["device_id"],
            "ac":"wifi",
            "channel":"googleplay",
            "aid":1233,
            "app_name":"musical_ly",
            "version_code":290304,
            "version_name":"29.3.4",
            "device_platform":"android",
            "os":"android",
            "ab_version":"29.3.4",
            "ssmix":"a",
            "device_type":deviceType["device_type"],
            "device_brand":"samsung",
            "language":"en",
            "os_api":28,
            "os_version":9,
            "openudid":deviceType["openudid"],
            "manifest_version_code":2022903040,
            "resolution":deviceType["resolution"],
            "dpi":deviceType["dpi"],
            "update_version_code":2022903040,
            "app_type":"normal",
            "sys_region":deviceType["sys_region"],
            "mcc_mnc":50501,
            "timezone_name":"Asia\/Yakutsk",
            "carrier_region_v2":505,
            "app_language":"en",
            "carrier_region":deviceType["carrier_region"],
            "ac2":"wifi5g",
            "uoo":0,
            "op_region":deviceType["op_region"],
            "timezone_offset":deviceType["timezone_offset"],
            "build_number":"29.3.4",
            "host_abi":"arm64-v8a",
            "locale":deviceType["locale"],
            "region":deviceType["region"],
            "cdid":deviceType["cdid"]
        }

    @staticmethod
    def GenerateHeaders(basePayload, baseCookies, domainRotate, signature):
        return {
            "content-length":str(len(basePayload)),
            "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
            "cookie":baseCookies,
            "host":domainRotate,
            "passport-sdk-version":"19",
            "sdk-version":"2",
            "user-agent":"com.zhiliaoapp.musically/2022903040 (Linux; U; Android 9; en_US; SM-G977N; Build/LMY48Z;tt-ok/3.12.13.1)",
            "x-argus":"iXezAlBdeoONxmYFYN7vi4wBB39kLVrgUvzvJWzOaRrSr8/Bbj777qHcPUQeKfgfKH7v94B6Cx3b8V6HpCzVKOSobKtOAIYccG+cQ4oVRgcvKo5oLqAD/0P2/VWs2yv5qXgF1sLxEqMg5i2CyDmFEcSUS8D7R08oG0z3RdMv6z5y0UXdYqKMyomJuqCc3xyLQr+RWaaWh7/kN1VfQQd67fJKUDqkfV6lwmssjOhvov1MLJu6q8K/pcfZwwRha9Z/xkSRSD8UYn9uRlQIy+fFUtxu",
            "x-gorgon":signature["x-gorgon"],
            "x-khronos":signature["x-khronos"],
            "x-ladon":"G2GCCV7qqfoOGszXlN4/yP1EViOEmP6wez1kTcy+5ArrTVi1",
            "x-ss-req-ticket":"1682927953076",
            "x-ss-stub":hashlib.md5(str(basePayload).encode()).hexdigest().upper(),
            "x-tt-dm-status":"login=0;ct=1;rt=6",
            "x-tt-store-region":"au",
            "x-tt-store-region-src":"did",
            "x-vc-bdturing-sdk-version":"2.3.0.i18n"
        }

    @staticmethod
    def GeneratePayload(videoId, choiceId):
        return {
            "item_id": videoId,
            f"{choiceId}_delta": 1
        }

def GenerateService():
    global success, failed, errors, proxy, Option, proxies
    while True:
        try:
            global videoId
            domainRotate = random.choice(domains)
            if Option == True:
                proxyRotate = random.choice(proxies)
                proxyRequests = {"http": f"http://{proxyRotate}", "https": f"http://{proxyRotate}"}
            else:
                proxyRequests = None
            while True:
                try:
                    device = random.choice(devices)
                    deviceInfo = json.loads(device.replace("'", '"').replace("True",'"True"'))
                    break
                except:
                    continue
            choiceId = "play"
            deviceType = deviceInfo["device_info"]
            baseParams = TikTok.GenerateParams(deviceInfo, deviceType)
            basePayload = TikTok.GeneratePayload(videoId, choiceId)
            baseSignature = signature(params=urllib.parse.urlencode(baseParams), cookies=None, data=None).get_value()
            baseHeaders = TikTok.GenerateHeaders(basePayload, deviceInfo["cookie"], domainRotate, baseSignature)
            try:
                response = requests.post(
                    url = f"https://{domainRotate}/aweme/v1/aweme/stats/?",
                    headers = baseHeaders,
                    data = basePayload,
                    params = urllib.parse.urlencode(baseParams),
                    proxies = proxyRequests,
                    verify = False
                )
                if "status_code" in response.text:
                    success += 1
                else:
                    failed += 1
            except requests.exceptions.ProxyError:
                proxy += 1
            except Exception as e:
                errors += 1
        except Exception:
            errors += 1 

os.system("mode 100,25")
TikTok.GenerateScreen("1")
videoId = input(Fore.LIGHTRED_EX + f"[>] {Fore.LIGHTGREEN_EX}VideoID  {Fore.RESET}")
threadChoice = input(Fore.LIGHTRED_EX + f"[>] {Fore.LIGHTGREEN_EX}Threads  {Fore.RESET}")
proxyChoice = input(Fore.LIGHTRED_EX + f"[>] {Fore.LIGHTGREEN_EX}If you dont have proxies (ENTER 1) if u have proxies and u put it in proxies.txt (ENTER 2){Fore.RESET}     ")
if proxyChoice == "1":
    Option = False
else:
    Option = True
    proxies = open("proxies.txt").read().splitlines()
os.system('cls' if os.name == 'nt' else 'clear')
TikTok.GenerateScreen(1)
print(Fore.LIGHTGREEN_EX + f'Sending Views ...')
threading.Thread(target=TikTok.GenerateChecks).start()
threading.Thread(target=TikTok.GenerateScreen, args=("2")).start()

for i in range(int(threadChoice)):
    threading.Thread(target=GenerateService).start()
