"""
测试后端服务是否正常运行
"""
import requests

BASE_URL = "http://localhost:8000"

def test_connection():
    """测试后端连接"""
    try:
        # 测试根路径
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✓ 后端服务正常: {response.status_code}")
        print(f"  响应: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务")
        print(f"  请确认后端服务运行在 {BASE_URL}")
        print("  启动命令: cd backend && python main.py")
        return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def test_send_code():
    """测试发送验证码接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/send-code",
            json={"phone": "19994729367"},
            timeout=10
        )
        print(f"\n✓ 发送验证码接口测试: {response.status_code}")
        print(f"  响应: {response.json()}")
        return True
    except Exception as e:
        print(f"\n✗ 发送验证码接口测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("后端服务连接测试")
    print("=" * 50)
    
    if test_connection():
        test_send_code()
    
    print("\n" + "=" * 50)

