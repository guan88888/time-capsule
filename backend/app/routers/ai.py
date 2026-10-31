"""
AI功能相关路由
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
import re

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import User
from app.services.ai import generate_text
from app.services.prompts import PromptTemplates

router = APIRouter()


# 请求模型
class GenerateTitleRequest(BaseModel):
    """生成标题请求"""
    content: str = Field(..., description="胶囊内容", min_length=1, max_length=2000)
    count: int = Field(default=3, description="生成标题数量", ge=1, le=10)


class RecommendTagsRequest(BaseModel):
    """推荐标签请求"""
    title: str = Field(..., description="胶囊标题", max_length=100)
    content: str = Field(..., description="胶囊内容", max_length=2000)
    count: int = Field(default=5, description="推荐标签数量", ge=1, le=10)


class MentalSuggestionRequest(BaseModel):
    """心理健康建议请求"""
    emotion_score: int = Field(..., description="情绪评分（0-4）", ge=0, le=4)
    review_text: str = Field(..., description="回顾文本", max_length=1000)
    original_content: str = Field(..., description="原始胶囊内容", max_length=2000)


# 响应模型
class GenerateTitleResponse(BaseModel):
    """生成标题响应"""
    titles: List[str] = Field(..., description="生成的标题列表")
    success: bool = Field(default=True, description="是否成功")


class RecommendTagsResponse(BaseModel):
    """推荐标签响应"""
    tags: List[str] = Field(..., description="推荐的标签列表")
    success: bool = Field(default=True, description="是否成功")


class MentalSuggestionResponse(BaseModel):
    """心理健康建议响应"""
    suggestion: str = Field(..., description="心理健康建议")
    success: bool = Field(default=True, description="是否成功")


@router.post("/generate-title", response_model=GenerateTitleResponse, summary="AI生成标题")
async def generate_title(
    request: GenerateTitleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    根据胶囊内容生成标题
    
    - **content**: 胶囊内容
    - **count**: 生成标题数量（1-10，默认3）
    
    返回生成的标题列表
    """
    try:
        templates = PromptTemplates()
        prompt = templates.generate_title(request.content, count=request.count)
        
        # 调用AI生成标题
        result = generate_text(prompt, max_tokens=150)
        
        # 解析结果：按换行符分割，过滤空行，去除编号
        titles = []
        for line in result.split('\n'):
            line = line.strip()
            # 移除可能的编号（如 "1. "、"1、"等）
            if line and not line.startswith(tuple('0REDACTED_SECRET9.- ')):
                titles.append(line)
            elif line:
                # 如果有编号，移除编号部分
                cleaned = re.sub(r'^[\d\.\-\s]+\s*', '', line)
                if cleaned:
                    titles.append(cleaned)
        
        # 如果解析失败或数量不足，使用原始结果作为单个标题
        if not titles:
            titles = [result.strip()] if result.strip() else ["未生成标题"]
        
        # 限制返回数量
        titles = titles[:request.count]
        
        return GenerateTitleResponse(titles=titles, success=True)
        
    except ValueError as e:
        # AI调用失败，返回友好错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成标题失败: {str(e)}"
        )


@router.post("/recommend-tags", response_model=RecommendTagsResponse, summary="AI推荐标签")
async def recommend_tags(
    request: RecommendTagsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    根据胶囊标题和内容推荐标签
    
    - **title**: 胶囊标题
    - **content**: 胶囊内容
    - **count**: 推荐标签数量（1-10，默认5）
    
    返回推荐的标签列表
    """
    try:
        templates = PromptTemplates()
        prompt = templates.recommend_tags(request.title, request.content, count=request.count)
        
        # 调用AI生成标签
        result = generate_text(prompt, max_tokens=100)
        
        # 解析结果：按逗号分割，过滤空字符串，去除空格
        tags = []
        for tag in result.split(','):
            tag = tag.strip()
            # 移除可能的编号
            if tag and not tag.startswith(tuple('0REDACTED_SECRET9.- ')):
                tags.append(tag)
        
        # 如果解析失败，尝试按其他分隔符分割
        if not tags:
            for separator in ['，', '\n', '、']:
                tags = [t.strip() for t in result.split(separator) if t.strip()]
                if tags:
                    break
        
        # 如果还是没有，使用原始结果
        if not tags:
            tags = [result.strip()] if result.strip() else []
        
        # 限制返回数量
        tags = tags[:request.count]
        
        return RecommendTagsResponse(tags=tags, success=True)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推荐标签失败: {str(e)}"
        )


@router.post("/mental-suggestion", response_model=MentalSuggestionResponse, summary="AI心理健康建议")
async def mental_suggestion(
    request: MentalSuggestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    根据情绪评分和回顾内容生成个性化心理健康建议
    
    - **emotion_score**: 情绪评分（0-4）
    - **review_text**: 回顾文本
    - **original_content**: 原始胶囊内容
    
    返回个性化心理健康建议
    """
    try:
        templates = PromptTemplates()
        prompt = templates.mental_suggestion(
            emotion_score=request.emotion_score,
            review_text=request.review_text,
            original_content=request.original_content
        )
        
        # 调用AI生成建议
        result = generate_text(prompt, max_tokens=300, temperature=0.8)
        
        return MentalSuggestionResponse(suggestion=result.strip(), success=True)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成心理健康建议失败: {str(e)}"
        )
