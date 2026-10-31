"""
完整AI功能测试（需要登录）
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def login_and_get_token():
    """登录并获取token"""
    print("=" * 60)
    print("步骤1: 登录获取token")
    print("=" * 60)
    
    # 尝试使用测试账号登录
    # 注意：如果账号不存在，需要先注册
    login_data = {
        "account": "contact@example.invalid",
        "password": "123456"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("token")
            if token:
                print(f"✅ 登录成功，token: {token[:20]}...")
                return token
            else:
                print("❌ 登录响应中未找到token")
                return None
        elif response.status_code == 400:
            # 可能账号不存在，尝试注册
            print("⚠️  登录失败，尝试注册账号...")
            register_data = {
                "nickname": "测试用户",
                "account": login_data["account"],
                "password": login_data["password"]
            }
            register_response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=register_data,
                timeout=5
            )
            if register_response.status_code == 200:
                result = register_response.json()
                token = result.get("token")
                if token:
                    print(f"✅ 注册成功，token: {token[:20]}...")
                    return token
                else:
                    print("❌ 注册响应中未找到token")
                    return None
            else:
                print(f"❌ 注册失败: {register_response.status_code}")
                print(f"响应: {register_response.text[:200]}")
                return None
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_generate_title(token):
    """测试生成标题功能"""
    print("\n" + "=" * 60)
    print("步骤2: 测试AI生成标题")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_content = "我今天很开心，和朋友一起去了公园，天气很好，还拍了很多照片。"
    
    data = {
        "content": test_content,
        "count": 3
    }
    
    try:
        print(f"测试内容: {test_content}")
        print("发送请求...")
        
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-title",
            headers=headers,
            json=data,
            timeout=30  # AI请求可能需要较长时间
        )
        
        if response.status_code == 200:
            result = response.json()
            titles = result.get("titles", [])
            success = result.get("success", False)
            
            if success and titles:
                print(f"✅ 生成标题成功！共生成 {len(titles)} 个标题:")
                for i, title in enumerate(titles, 1):
                    print(f"   {i}. {title}")
                return True
            else:
                print(f"❌ 响应格式异常: {result}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（AI服务响应慢）")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommend_tags(token):
    """测试推荐标签功能"""
    print("\n" + "=" * 60)
    print("步骤3: 测试AI推荐标签")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": "快乐的一天",
        "content": "今天很开心，和朋友一起去了公园，天气很好。",
        "count": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/recommend-tags",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            tags = result.get("tags", [])
            success = result.get("success", False)
            
            if success and tags:
                print(f"✅ 推荐标签成功！共推荐 {len(tags)} 个标签:")
                for i, tag in enumerate(tags, 1):
                    print(f"   {i}. {tag}")
                return True
            else:
                print(f"❌ 响应格式异常: {result}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("\n🚀 开始完整AI功能测试\n")
    
    # 步骤1: 登录
    token = login_and_get_token()
    if not token:
        print("\n❌ 无法获取token，跳过需要认证的测试")
        print("   请先在前端页面登录后再测试完整功能")
        return False
    
    results = []
    
    # 步骤2: 测试生成标题
    results.append(("生成标题", test_generate_title(token)))
    
    # 步骤3: 测试推荐标签
    results.append(("推荐标签", test_recommend_tags(token)))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有功能测试通过！AI功能正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查:")
        print("   1. 后端服务是否正常运行")
        print("   2. AI API Key是否正确配置")
        print("   3. 网络连接是否正常")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
