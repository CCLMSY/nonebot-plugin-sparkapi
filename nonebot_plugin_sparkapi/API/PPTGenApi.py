# type: ignore
import hashlib
import hmac
import base64
import json
import time
import httpx

class AIPPT():
    def __init__(self, APPId, APISecret, Text):
        self.APPid = APPId
        self.APISecret = APISecret
        self.text = Text
        self.header = {}

    def get_signature(self, ts):
        try:
            auth = self.md5(self.APPid + str(ts))
            return self.hmac_sha1_encrypt(auth, self.APISecret)
        except Exception as e:
            print(e)
            return None

    def hmac_sha1_encrypt(self, encrypt_text, encrypt_key):
        return base64.b64encode(hmac.new(encrypt_key.encode('utf-8'), encrypt_text.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')

    def md5(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    async def create_task(self):
        url = 'https://zwapi.xfyun.cn/api/aippt/create'
        timestamp = int(time.time())
        signature = self.get_signature(timestamp)
        body = self.getbody(self.text)

        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": "application/json; charset=utf-8"
        }
        self.header = headers
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=json.dumps(body), headers=headers)
            resp = response.json()
            if resp['code'] == 0:
                print('创建PPT任务成功')
                return resp['data']['sid']
            else:
                print('创建PPT任务失败')
                return None

    def getbody(self, text):
        body = {"query": text}
        return body

    async def get_process(self, sid):
        if sid is not None:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://zwapi.xfyun.cn/api/aippt/progress?sid={sid}", headers=self.header)
                print(f"res:{response.text}")
                return response.text
        else:
            return None

    async def get_result(self):
        task_id = await self.create_task()
        while True:
            response = await self.get_process(task_id)
            resp = json.loads(response)
            process = resp['data']['process']
            if process == 100:
                PPTurl = resp['data']['pptUrl']
                break
        return PPTurl

async def main(appid, api_secret, content):
    demo = AIPPT(appid, api_secret, content)
    result = await demo.get_result()
    return result

# ---------------------------API Request---------------------------
from ..config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)

appid = conf.sparkapi_app_id
api_secret = conf.sparkapi_api_secret
api_key = conf.sparkapi_api_key


async def request_IP(content):
    res = await main(appid, api_secret, content)
    return res
