"""
测试注册接口
"""
import requests
import json

url = "http://localhost:8000/api/auth/register"
data = {
    "nickname": "测试用户",
    "account": "19931304555",
    "password": "123456"
}

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")
    
    if response.status_code != 200:
        try:
            error_detail = response.json()
            print(f"错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
        except:
            print(f"无法解析JSON错误")
except Exception as e:
    print(f"请求异常: {e}")

