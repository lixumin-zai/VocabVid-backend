import requests
import time


# 登录获取token
login_url = "http://localhost:20050/token"
login_data = {
    "username": "testuser",
    "password": "testpassword"
}
login_response = requests.post(login_url, data=login_data)
token_data = login_response.json()
access_token = token_data["access_token"]

# 设置请求头，包含JWT token
headers = {
    "Authorization": f"Bearer {access_token}"
}
print(headers)
url = "http://localhost:20050/gen-sentence"
# url = "https://lismin.online:10002/chat"
data = {"words": ["reciprocate, moribund, telegraph, episodic, trespass"]}

response = requests.post(url, json=data, headers=headers, stream=True)

buffer = b''  # 缓存不完整的字节序列
for bytes_text in response.iter_content(chunk_size=1):
    if bytes_text:
        # 将当前字节块追加到缓存中
        buffer += bytes_text
        # print(buffer)
        try:
            # 尝试解码当前的缓存
            decoded_text = buffer.decode('utf-8')
            print(decoded_text)
            # time.sleep(0.2)
            # 如果解码成功，清空缓存
            buffer = b''
        except UnicodeDecodeError: 
            # 如果解码失败，说明我们得到的是不完整的字符，保留在缓存中
            pass