"""
测试AI API接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# 测试用的token（需要先登录获取）
# 这里我们先测试接口是否可访问，然后再测试需要认证的接口

def test_ai_routes_accessible():
    """测试AI路由是否已注册"""
    print("=" * 60)
    print("测试1: 检查AI路由是否已注册")
    print("=" * 60)
    
    try:
        # 访问API文档，检查是否有AI路由
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
            # 检查是否有 /api/ai 路由（通过openapi.json）
            openapi_response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
            if openapi_response.status_code == 200:
                openapi = openapi_response.json()
                paths = openapi.get("paths", {})
                ai_paths = [path for path in paths.keys() if "/api/ai" in path]
                if ai_paths:
                    print(f"✅ AI路由已注册: {len(ai_paths)} 个接口")
                    for path in ai_paths:
                        print(f"   - {path}")
                    return True
                else:
                    print("❌ 未找到AI路由")
                    return False
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_generate_title_without_auth():
    """测试未认证时调用生成标题接口"""
    print("\n" + "=" * 60)
    print("测试2: 测试未认证时的响应（应返回401）")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-title",
            json={"content": "测试内容", "count": 3},
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ 正确返回401未授权错误（需要登录）")
            return True
        else:
            print(f"⚠️  返回状态码: {response.status_code} (预期: 401)")
            print(f"响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("\n🚀 开始测试AI API接口\n")
    
    results = []
    
    # 测试路由是否已注册
    results.append(("路由注册", test_ai_routes_accessible()))
    
    # 测试认证要求
    results.append(("认证检查", test_generate_title_without_auth()))
    
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
        print("\n🎉 所有基础测试通过！")
        print("\n⚠️  注意: 完整功能测试需要登录token")
        print("   可以在前端页面登录后测试完整功能")
    else:
        print("\n⚠️  部分测试失败，请检查后端服务")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
