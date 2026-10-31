# 时空胶囊APP - AI功能接入分析文档

## 📋 概述
本文档梳理了时空胶囊APP中可以接入火山方舟AI（豆包模型）的功能点，按优先级和使用场景进行分类。

---

## 🎯 一、核心功能（高优先级）

### 1.1 智能标题生成
**位置**: 创建胶囊页面 (`pages/create/create.vue`)
**功能描述**: 用户输入胶囊内容后，AI自动生成合适的标题
**实现方式**:
- 用户输入内容时，提供"AI生成标题"按钮
- 调用豆包API，传入内容文本，生成3-5个候选标题
- 用户可选择其中一个或手动编辑

**AI提示词示例**:
```
根据以下胶囊内容，生成3个简洁有吸引力的标题（每个不超过15字）：
{content}
```

**预期效果**: 提升用户体验，减少起标题的困难

---

### 1.2 智能标签推荐
**位置**: 创建胶囊页面 (`pages/create/create.vue`)
**功能描述**: 根据胶囊内容和标题，自动推荐相关标签
**实现方式**:
- 用户创建胶囊后，点击"AI推荐标签"按钮
- 分析内容提取关键词和主题
- 返回5-8个标签供用户选择

**AI提示词示例**:
```
分析以下胶囊内容，推荐5个标签（单个标签2-4字，用逗号分隔）：
标题：{title}
内容：{content}
```

**预期效果**: 方便用户添加标签，提升内容分类准确性

---

### 1.3 个性化心理健康建议
**位置**: 回顾胶囊页面 (`pages/review/review.vue`)
**功能描述**: 根据用户选择的情绪评分和回顾内容，生成个性化心理建议
**当前状态**: 使用固定模板（`getSuggestion`方法，5个固定建议）
**改进方案**:
- 分析用户的历史情绪数据
- 结合当前回顾文本内容
- 生成个性化、有针对性的建议

**AI提示词示例**:
```
用户情绪评分：{emotion_score}（0=非常难过，4=非常开心）
回顾内容：{review_text}
原始胶囊内容：{original_content}

请生成一段温暖、鼓励的心理健康建议（100-150字），帮助用户理解情绪，提供实用的改善建议。
```

**预期效果**: 从固定模板升级为个性化AI建议，更贴合用户实际情况

---

## 🔍 二、增强功能（中优先级）

### 2.1 AI内容优化建议
**位置**: 创建胶囊页面 (`pages/create/create.vue`)
**功能描述**: 检查内容语法、润色文字、提供表达建议
**实现方式**:
- 创建胶囊时，提供"AI优化"按钮
- 分析内容提供优化建议（语法、措辞、结构）
- 用户可选择接受建议或忽略

**AI提示词示例**:
```
请优化以下胶囊内容，提供：
1. 语法检查
2. 措辞润色建议
3. 表达优化（如适用）

内容：{content}
```

**预期效果**: 帮助用户提升内容质量

---

### 2.2 智能目标分析
**位置**: 回顾胶囊页面 - 目标胶囊类型 (`pages/review/review.vue`)
**功能描述**: 分析目标完成情况，提供改进建议
**实现方式**:
- 对比原始目标和当前进度
- 分析完成情况，识别阻碍因素
- 提供下一步行动建议

**AI提示词示例**:
```
原始目标：{target}
当前进度：{progress}%
回顾内容：{review_text}

请分析目标完成情况，提供：
1. 完成情况评估
2. 可能的原因分析
3. 下一步行动建议（50-100字）
```

**预期效果**: 帮助用户更好地达成目标

---

### 2.3 AI情感分析报告
**位置**: 情绪日历页面 (`pages/emotion-calendar/emotion-calendar.vue`)
**功能描述**: 分析一段时间内的情绪趋势，生成月度/年度情绪报告
**实现方式**:
- 收集用户的历史情绪数据（评分+回顾文本）
- AI分析情绪变化趋势、主要影响因素
- 生成可视化报告和建议

**AI提示词示例**:
```
用户近30天的情绪数据：
{emotion_data}  // 格式：[{date, score, review_text}, ...]

请生成月度情绪分析报告：
1. 情绪趋势总结
2. 主要情绪影响因素
3. 改善建议（100-200字）
```

**预期效果**: 帮助用户了解情绪模式，提升自我认知

---

### 2.4 AI反思引导
**位置**: 回顾胶囊页面 (`pages/review/review.vue`)
**功能描述**: 根据胶囊内容和当前回顾，生成引导性问题，帮助用户深度思考
**实现方式**:
- 分析胶囊内容和当前回顾文本
- 生成3-5个开放性问题
- 帮助用户更深入地反思

**AI提示词示例**:
```
原始胶囊内容：{original_content}
当前回顾：{review_text}

请生成3个引导性反思问题，帮助用户深度思考（每个问题20-30字）。
```

**预期效果**: 促进用户深度思考，提升回顾质量

---

## 🛡️ 三、辅助功能（低优先级）

### 3.1 AI评论内容检测
**位置**: 共享胶囊评论功能
**功能描述**: 检测评论内容是否包含不当言论（辱骂、广告等）
**实现方式**:
- 提交评论前进行内容检测
- 识别不当内容并提示用户修改
- 保护社区环境

**AI提示词示例**:
```
检测以下评论内容是否包含不当言论（辱骂、广告、色情等）：
{comment_text}

返回：{"is_appropriate": true/false, "reason": "原因"}
```

**预期效果**: 维护社区环境，减少不当内容

---

### 3.2 AI评论回复建议
**位置**: 共享胶囊评论回复
**功能描述**: 帮助用户生成友好的回复
**实现方式**:
- 用户点击"AI帮助回复"
- 分析原评论内容和上下文
- 生成2-3个回复建议

**AI提示词示例**:
```
原始胶囊：{capsule_content}
用户评论：{comment}
请生成2个友好、合适的回复建议（每个30-50字）。
```

**预期效果**: 提升互动质量

---

## 📊 四、功能优先级总结

| 功能 | 优先级 | 难度 | 用户体验提升 | 实现建议 |
|------|--------|------|--------------|----------|
| 智能标题生成 | ⭐⭐⭐⭐⭐ | 低 | 高 | 先实现 |
| 智能标签推荐 | ⭐⭐⭐⭐⭐ | 低 | 高 | 先实现 |
| 个性化心理健康建议 | ⭐⭐⭐⭐⭐ | 中 | 高 | 先实现 |
| AI内容优化 | ⭐⭐⭐⭐ | 中 | 中 | 第二阶段 |
| 智能目标分析 | ⭐⭐⭐⭐ | 中 | 中 | 第二阶段 |
| AI情感分析报告 | ⭐⭐⭐ | 高 | 中 | 第三阶段 |
| AI反思引导 | ⭐⭐⭐ | 中 | 中 | 第三阶段 |
| 评论内容检测 | ⭐⭐ | 低 | 低 | 第四阶段 |
| 评论回复建议 | ⭐⭐ | 低 | 低 | 第四阶段 |

---

## 🔧 五、技术实现建议

### 5.1 后端API设计

#### 创建AI服务模块
```
backend/app/services/ai_service.py
- send_ai_request(prompt, model="doubao")  # 统一AI请求封装
- generate_title(content)  # 生成标题
- recommend_tags(title, content)  # 推荐标签
- generate_mental_suggestion(emotion_score, review_text, original_content)  # 心理健康建议
- optimize_content(content)  # 内容优化
- analyze_goal(target, progress, review_text)  # 目标分析
- analyze_emotion_trend(emotion_data)  # 情绪趋势分析
- generate_reflection_questions(original_content, review_text)  # 反思引导
- detect_inappropriate_content(text)  # 内容检测
- suggest_comment_reply(comment, capsule_content)  # 回复建议
```

#### 创建AI路由
```
backend/app/routers/ai.py
- POST /api/ai/generate-title  # 生成标题
- POST /api/ai/recommend-tags  # 推荐标签
- POST /api/ai/mental-suggestion  # 心理健康建议
- POST /api/ai/optimize-content  # 内容优化
- POST /api/ai/analyze-goal  # 目标分析
- POST /api/ai/emotion-report  # 情绪报告
- POST /api/ai/reflection-questions  # 反思引导
- POST /api/ai/detect-content  # 内容检测
- POST /api/ai/suggest-reply  # 回复建议
```

### 5.2 前端调用示例

```javascript
// utils/api.js 添加AI相关API
const ai = {
  // 生成标题
  generateTitle(content) {
    return request('/api/ai/generate-title', 'POST', { content })
  },
  
  // 推荐标签
  recommendTags(title, content) {
    return request('/api/ai/recommend-tags', 'POST', { title, content })
  },
  
  // 获取心理健康建议
  getMentalSuggestion(emotionScore, reviewText, originalContent) {
    return request('/api/ai/mental-suggestion', 'POST', {
      emotion_score: emotionScore,
      review_text: reviewText,
      original_content: originalContent
    })
  },
  
  // 其他AI功能...
}
```

### 5.3 火山方舟API集成

**配置信息**:
- API密钥: 需要在火山方舟平台申请
- 模型名称: doubao-pro-32k 或 doubao-lite-32k
- API端点: https://ark.cn-beijing.volces.com/api/v3/chat/completions

**请求示例**:
```python
import requests
import json

def call_doubao_api(prompt, max_tokens=500):
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "doubao-pro-32k",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

---

## 📝 六、注意事项

### 6.1 成本控制
- **缓存策略**: 相同输入缓存结果，避免重复调用
- **频率限制**: 限制用户调用频率，防止滥用
- **模型选择**: 根据场景选择合适模型（lite版成本更低）

### 6.2 用户体验
- **加载状态**: 显示"AI思考中..."等友好提示
- **错误处理**: AI调用失败时提供降级方案（使用固定模板）
- **可选功能**: AI功能作为增强功能，不影响基础使用

### 6.3 数据隐私
- **内容保护**: 确保用户内容不被用于模型训练
- **敏感信息**: 检测并过滤敏感内容
- **用户授权**: 明确告知用户AI功能的使用

### 6.4 性能优化
- **异步调用**: AI请求异步处理，不阻塞主流程
- **批量处理**: 情绪报告等可批量分析
- **结果缓存**: 相同内容的AI结果缓存24小时

---

## 🚀 七、实施路线图

### Phase 1: MVP（最小可行产品）
- ✅ 智能标题生成
- ✅ 智能标签推荐
- ✅ 个性化心理健康建议

### Phase 2: 功能增强
- ✅ AI内容优化
- ✅ 智能目标分析

### Phase 3: 深度分析
- ✅ AI情感分析报告
- ✅ AI反思引导

### Phase 4: 社区功能
- ✅ 评论内容检测
- ✅ 评论回复建议

---

## 📞 八、后续优化方向

1. **个性化模型**: 根据用户历史数据训练个性化模型
2. **多模态支持**: 支持图片、语音胶囊的AI分析
3. **智能推荐**: 基于AI推荐相关胶囊、用户
4. **情感陪伴**: AI虚拟助手陪伴用户回顾胶囊

---

**文档版本**: v1.0  
**更新时间**: 2024-12-20  
**维护者**: 开发团队
