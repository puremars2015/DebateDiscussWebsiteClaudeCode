import requests

# 測試需要認證的 OPTIONS 請求
headers = {
    'Origin': 'http://localhost:8080',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'authorization'
}

print("測試 OPTIONS 請求到 /api/users/me（需要認證）")
response = requests.options('http://localhost:5000/api/users/me', headers=headers)
print(f"狀態碼: {response.status_code}")
print(f"響應文本: {response.text}")
print(f"Headers: {dict(response.headers)}")
print()

if response.status_code == 204:
    print("✅ OPTIONS 請求成功！不需要認證即可通過 preflight")
else:
    print(f"❌ OPTIONS 請求失敗，狀態碼: {response.status_code}")
