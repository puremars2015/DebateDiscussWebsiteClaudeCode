import requests
import time

time.sleep(1)  # 確保服務器已啟動

print("測試 OPTIONS 到 /api/debates (沒有尾斜線)")
r = requests.options('http://localhost:5000/api/debates', 
                     headers={'Origin': 'http://localhost:8080'}, 
                     allow_redirects=False)
print(f"狀態碼: {r.status_code}")
if r.status_code in [301, 302, 307, 308]:
    print(f"❌ 重定向到: {r.headers.get('Location')}")
elif r.status_code == 204:
    print("✅ 成功！")
print()

print("測試 GET 到 /api/debates")
r = requests.get('http://localhost:5000/api/debates?status=ONGOING')
print(f"狀態碼: {r.status_code}")
if r.status_code == 200:
    print(f"✅ 成功！返回 {len(r.json()['debates'])} 個辯論")
