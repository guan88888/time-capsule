"""
Pydantic 数据模型（请求/响应）
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# 注册请求
class RegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    account: str = Field(..., description="邮箱或手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    sms_code: Optional[str] = Field(None, min_length=6, max_length=6, description="短信验证码（手机号注册时必需）")

# 登录请求
class LoginRequest(BaseModel):
    account: str = Field(..., description="邮箱或手机号")
    password: str = Field(..., description="密码")

# 忘记密码请求
class ForgotPasswordRequest(BaseModel):
    account: str = Field(..., description="邮箱或手机号")

# 重置密码请求
class ResetPasswordRequest(BaseModel):
    account: str = Field(..., description="邮箱或手机号")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    sms_code: str = Field(..., min_length=6, max_length=6, description="短信验证码（手机号重置密码时必需）")

# 发送验证码请求
class SendCodeRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    scene: str = Field(default="register", description="场景类型: register/login/reset_password/change_phone/bind_phone/verify_bind_phone")

# 验证码登录请求
class CodeLoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=4, max_length=10, description="验证码")

# 用户信息响应
class UserInfo(BaseModel):
    id: int
    nickname: str
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 登录/注册响应
class AuthResponse(BaseModel):
    token: str
    user: UserInfo

# 通用响应
class MessageResponse(BaseModel):
    message: str
    success: bool = True

# 更新用户资料请求
class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    email: Optional[str] = Field(None, description="邮箱")

# ========== 胶囊相关 ==========

# 创建胶囊请求
class CreateCapsuleRequest(BaseModel):
    type: str = Field(..., description="胶囊类型: target/emotion/gratitude/share")
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., description="内容")
    target: Optional[str] = Field(None, description="目标描述（目标胶囊）")
    unlock_date: datetime = Field(..., description="解锁时间")
    tags: Optional[List[str]] = Field(default=[], description="标签列表")
    allow_share: Optional[bool] = Field(default=False, description="是否允许共享")

# 更新胶囊请求
class UpdateCapsuleRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="标题")
    content: Optional[str] = Field(None, description="内容")
    target: Optional[str] = Field(None, description="目标描述")

# 保存回顾请求
class SaveReviewRequest(BaseModel):
    review: Optional[str] = Field(None, description="回顾内容")
    progress: Optional[int] = Field(None, ge=0, le=100, description="完成进度（0-100，目标胶囊）")
    emotion_score: Optional[int] = Field(None, ge=0, le=4, description="情绪评分（0-4，心境胶囊）")

# 胶囊响应
class CapsuleResponse(BaseModel):
    id: int
    type: str
    title: str
    content: str
    target: Optional[str] = None
    unlock_date: datetime
    is_unlocked: bool
    is_shared: bool
    share_code: Optional[str] = None
    tags: Optional[List[str]] = None
    progress: int
    emotion_score: Optional[int] = None
    review: Optional[str] = None
    like_count: int
    is_liked: Optional[bool] = False  # 当前用户是否已点赞
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========== 情绪相关 ==========

# 记录情绪请求
class CreateEmotionRequest(BaseModel):
    score: int = Field(..., ge=0, le=4, description="情绪评分（0-4）")
    capsule_id: Optional[int] = Field(None, description="关联胶囊ID")
    date: Optional[datetime] = Field(None, description="记录日期（默认今天）")

# 情绪响应
class EmotionResponse(BaseModel):
    id: int
    score: int
    capsule_id: Optional[int] = None
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# 情绪统计响应
class EmotionStatsResponse(BaseModel):
    total: int
    by_score: Dict[int, int]  # {score: count}

# ========== 成就相关 ==========

# 成就响应
class AchievementResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    
    class Config:
        from_attributes = True

# 用户成就响应
class UserAchievementResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    unlocked_at: Optional[datetime] = None
    is_unlocked: bool
    
    class Config:
        from_attributes = True

# ========== 评论相关 ==========

# 添加评论请求
class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")

# 评论响应
class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    user_nickname: str
    user_avatar: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

