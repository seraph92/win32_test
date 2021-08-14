import requests
import json

with open(r"C:\work\python\win32_test-1\talk_test\kakao_code.json","r") as fp:
    tokens = json.load(fp)

url="https://kapi.kakao.com/v2/api/talk/memo/default/send"

print(f"url = [{url}]")
# kapi.kakao.com/v2/api/talk/memo/default/send 

headers={
    "Authorization" : "Bearer " + tokens["access_token"]
}

print(f"headers = [{headers}]")

data={
    "template_object": json.dumps({
        "object_type":"text",
        "text":"Hello, world!",
        "link":{
            "web_url":"www.naver.com"
        }
    })
}

print(f"data = [{data}]")

response = requests.post(url, headers=headers, data=data)
response.status_code

print(f"response = [{response}]")