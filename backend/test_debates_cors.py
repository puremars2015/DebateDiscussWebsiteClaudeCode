import requests

# 測試 OPTIONS 請求到 /api/debates
headers = {
    'Origin': 'http://localhost:8080',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'authorization'
}

print("=" * 60)
print("測試 OPTIONS 請求到 /api/debates")
print("=" * 60)

try:
    response = requests.options('http://localhost:5000/api/debates', headers=headers, allow_redirects=False)
    print(f"狀態碼: {response.status_code}")
    print(f"響應文本: '{response.text}'")
    print(f"\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    if response.status_code in [301, 302, 307, 308]:
        print(f"\n❌ 錯誤：收到重定向狀態碼 {response.status_code}")
        if 'Location' in response.headers:
            print(f"   重定向到: {response.headers['Location']}")
    elif response.status_code == 204:
        print("\n✅ OPTIONS 請求成功！")
    else:
        print(f"\n⚠️ 非預期的狀態碼: {response.status_code}")
        
except Exception as e:
    print(f"❌ 請求失敗: {e}")

print("\n" + "=" * 60)
print("測試 GET 請求到 /api/debates")
print("=" * 60)

try:
    response = requests.get('http://localhost:5000/api/debates?status=ONGOING')
    print(f"狀態碼: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET 請求成功，返回 {len(data.get('debates', []))} 個辯論")
    else:
        print(f"響應: {response.text}")
except Exception as e:
    print(f"❌ 請求失敗: {e}")
