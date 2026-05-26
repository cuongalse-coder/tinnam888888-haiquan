import requests

urls = [
    'https://luatvietnam.vn/tin-phap-luat.rss',
    'https://haiquanonline.com.vn/rss/hai-quan-c4.rss',
    'https://haiquanonline.com.vn/rss/xuat-nhap-khau-c5.rss',
    'https://baophapluat.vn/rss/kinh-te-c3.rss',
    'https://tapchitaichinh.vn/rss/ke-toan-kiem-toan.rss'
]

for url in urls:
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"{url} -> {resp.status_code}")
    except Exception as e:
        print(f"{url} -> Error: {e}")
