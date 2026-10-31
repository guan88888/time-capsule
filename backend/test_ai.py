"""
测试AI服务
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai import generate_text, call_ai_api
from app.services.prompts import PromptTemplates
from app.config import settings

def test_basic_ai_call():
    """测试基础AI调用"""
    print("=" * 60)
    print("测试1: 基础AI调用")
    print("=" * 60)
    
    try:
        result = generate_text("你好，请用一句话介绍你自己。")
        print(f"✅ AI响应成功:")
        print(f"内容: {result}")
        print()
        return True
    except Exception as e:
        print(f"❌ AI调用失败: {e}")
        print()
        return False

def test_raw_api_call():
    """测试原始API调用（返回完整结果）"""
    print("=" * 60)
    print("测试2: 原始API调用（返回完整结果）")
    print("=" * 60)
    
    try:
        result = call_ai_api("请说一个简短的励志句子。")
        if result["success"]:
            print(f"✅ API调用成功:")
            print(f"内容: {result['content']}")
            print(f"原始响应keys: {list(result.get('raw_response', {}).keys())}")
        else:
            print(f"❌ API调用失败: {result.get('error')}")
            print(f"状态码: {result.get('status_code')}")
        print()
        return result["success"]
    except Exception as e:
        print(f"❌ 调用异常: {e}")
        print()
        return False

def test_prompt_templates():
    """测试提示词模板"""
    print("=" * 60)
    print("测试3: 提示词模板")
    print("=" * 60)
    
    try:
        templates = PromptTemplates()
        
        # 测试标题生成
        title_prompt = templates.generate_title("我今天很开心，和朋友一起去了公园，天气很好。", count=3)
        print("✅ 标题生成提示词:")
        print(title_prompt[:100] + "...")
        print()
        
        # 测试标签推荐
        tag_prompt = templates.recommend_tags("快乐的一天", "今天很开心，和朋友一起去了公园。", count=5)
        print("✅ 标签推荐提示词:")
        print(tag_prompt[:100] + "...")
        print()
        
        # 测试心理健康建议
        suggestion_prompt = templates.mental_suggestion(
            emotion_score=3,
            review_text="现在感觉比之前好多了",
            original_content="今天心情有点低落"
        )
        print("✅ 心理健康建议提示词:")
        print(suggestion_prompt[:150] + "...")
        print()
        
        return True
    except Exception as e:
        print(f"❌ 提示词模板测试失败: {e}")
        print()
        return False

def test_ai_integration():
    """测试AI集成（使用提示词模板）"""
    print("=" * 60)
    print("测试4: AI集成测试（标题生成）")
    print("=" * 60)
    
    try:
        templates = PromptTemplates()
        prompt = templates.generate_title(
            "我今天很开心，和朋友一起去了公园，天气很好，还拍了很多照片。",
            count=3
        )
        
        result = generate_text(prompt, max_tokens=100)
        print(f"✅ AI标题生成成功:")
        print(f"提示词长度: {len(prompt)} 字符")
        print(f"生成的标题:")
        print(result)
        print()
        return True
    except Exception as e:
        print(f"❌ AI集成测试失败: {e}")
        print()
        return False

def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("测试0: 配置加载")
    print("=" * 60)
    
    try:
        print(f"API URL: {settings.volcano_ark_api_url}")
        print(f"Model: {settings.volcano_ark_model}")
        print(f"API Key: {settings.volcano_ark_api_key[:20]}..." if settings.volcano_ark_api_key else "未配置")
        print(f"Max Tokens: {settings.ai_max_tokens}")
        print(f"Temperature: {settings.ai_temperature}")
        print(f"Enable Thinking: {settings.ai_enable_thinking}")
        print()
        
        if not settings.volcano_ark_api_key:
            print("⚠️  警告: API Key 未配置")
            return False
        
        print("✅ 配置加载成功")
        print()
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        print()
        return False

def main():
    """主测试函数"""
    print("\n🚀 开始测试AI服务\n")
    
    results = []
    
    # 测试配置
    results.append(("配置加载", test_config()))
    
    # 测试基础AI调用
    if results[-1][1]:  # 只有配置加载成功才继续
        results.append(("基础AI调用", test_basic_ai_call()))
        results.append(("原始API调用", test_raw_api_call()))
        results.append(("提示词模板", test_prompt_templates()))
        
        # 只有在基础调用成功时才测试集成
        if results[1][1]:  # 基础调用成功
            results.append(("AI集成测试", test_ai_integration()))
    
    # 输出总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！AI服务配置成功。")
    else:
        print("\n⚠️  部分测试失败，请检查配置和网络连接。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
