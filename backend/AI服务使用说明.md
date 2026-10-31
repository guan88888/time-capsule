# AI服务使用说明

## 📁 文件结构

已创建以下文件：

```
backend/
├── .env                           # API配置（包含API Key）
├── app/
│   ├── config.py                  # 配置管理
│   └── services/
│       ├── ai.py                  # AI服务封装
│       └── prompts.py             # 提示词模板
└── test_ai.py                     # AI服务测试脚本
```

---

## 🔧 配置文件

### `.env` 文件
存放火山方舟AI的配置信息：
```env
VOLCANO_ARK_API_KEY=REDACTED_SECRET
VOLCANO_ARK_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
VOLCANO_ARK_MODEL=doubao-seed-1-8-251228
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.7
AI_ENABLE_THINKING=false
```

**⚠️ 注意**: `.env` 文件包含敏感信息，请勿提交到版本控制系统。

---

## 🚀 快速使用

### 1. 基础AI调用

```python
from app.services.ai import generate_text

# 简单文本生成
result = generate_text("你好，请介绍一下你自己。")
print(result)
```

### 2. 完整API调用（获取详细结果）

```python
from app.services.ai import call_ai_api

result = call_ai_api("请说一个励志句子。")
if result["success"]:
    print(result["content"])
    print(result["raw_response"])  # 完整响应
else:
    print(result["error"])
```

### 3. 使用提示词模板

```python
from app.services.prompts import PromptTemplates
from app.services.ai import generate_text

templates = PromptTemplates()

# 生成标题
prompt = templates.generate_title("我今天很开心，和朋友一起去了公园。", count=3)
titles = generate_text(prompt)
print(titles)

# 推荐标签
prompt = templates.recommend_tags("快乐的一天", "今天很开心，和朋友一起去了公园。", count=5)
tags = generate_text(prompt)
print(tags)

# 心理健康建议
prompt = templates.mental_suggestion(
    emotion_score=3,
    review_text="现在感觉比之前好多了",
    original_content="今天心情有点低落"
)
suggestion = generate_text(prompt)
print(suggestion)
```

---

## 📋 可用功能

### AI服务 (`app/services/ai.py`)

- `generate_text(prompt, max_tokens, temperature, system_prompt)` - 生成文本（简化接口）
- `call_ai_api(prompt, max_tokens, temperature, system_prompt)` - 调用API（完整结果）

### 提示词模板 (`app/services/prompts.py`)

1. **标题生成**: `generate_title(content, count=3)`
2. **标签推荐**: `recommend_tags(title, content, count=5)`
3. **心理健康建议**: `mental_suggestion(emotion_score, review_text, original_content)`
4. **内容优化**: `optimize_content(content)`
5. **目标分析**: `analyze_goal(target, progress, review_text)`
6. **情绪趋势分析**: `emotion_trend_analysis(emotion_data)`
7. **反思引导**: `reflection_questions(original_content, review_text, count=3)`
8. **内容检测**: `detect_inappropriate_content(text)`
9. **回复建议**: `suggest_comment_reply(comment, capsule_content)`

---

## 🧪 测试

运行测试脚本验证AI服务：

```bash
cd backend
python3 test_ai.py
```

测试包括：
- ✅ 配置加载
- ✅ 基础AI调用
- ✅ 原始API调用
- ✅ 提示词模板
- ✅ AI集成测试

---

## 📝 使用示例

### 示例1: 在路由中使用AI服务

```python
from fastapi import APIRouter
from app.services.ai import generate_text
from app.services.prompts import PromptTemplates

router = APIRouter()

@router.post("/generate-title")
async def generate_title_api(request: GenerateTitleRequest):
    templates = PromptTemplates()
    prompt = templates.generate_title(request.content, count=3)
    titles = generate_text(prompt)
    return {"titles": titles.split("\n")}
```

### 示例2: 错误处理

```python
from app.services.ai import call_ai_api

result = call_ai_api("你好")
if result["success"]:
    content = result["content"]
else:
    # 降级方案：使用固定模板
    error = result["error"]
    content = "默认内容"  # 或从缓存获取
```

---

## ⚙️ 配置说明

### 修改模型
编辑 `.env` 文件：
```env
VOLCANO_ARK_MODEL=doubao-seed-1-8-251228
```

### 调整参数
```env
AI_MAX_TOKENS=500      # 最大token数
AI_TEMPERATURE=0.7     # 温度参数（0-1，越高越随机）
AI_ENABLE_THINKING=false  # 是否启用深度思考
```

---

## 🔒 安全建议

1. **API Key保护**: 确保 `.env` 文件不被提交到Git
2. **错误处理**: 在生产环境中添加适当的错误处理和降级方案
3. **频率限制**: 考虑添加API调用频率限制，防止滥用
4. **结果缓存**: 相同输入可以缓存结果，减少API调用

---

## 📊 性能优化

- **异步调用**: AI请求可以异步处理，不阻塞主流程
- **结果缓存**: 相同提示词的结果可以缓存24小时
- **批量处理**: 多个请求可以批量发送（如果API支持）

---

## ❓ 故障排查

### 问题1: 配置加载失败
**解决方案**: 检查 `.env` 文件路径和格式是否正确

### 问题2: API调用失败
**解决方案**: 
- 检查API Key是否正确
- 检查网络连接
- 查看错误信息中的状态码和错误详情

### 问题3: 响应格式异常
**解决方案**: 
- 检查模型名称是否正确
- 查看 `raw_response` 了解API实际返回内容

---

**创建时间**: 2024-12-20  
**版本**: v1.0
