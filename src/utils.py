

# 异步get请求 请求图片
async def fetch(session, url):
    if url.startswith("http"):
        async with session.get(url) as response:
            return await response.read()
    else:
        return b""