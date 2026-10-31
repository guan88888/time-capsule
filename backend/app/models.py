"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nickname = Column(String(50), nullable=False, comment="昵称")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    password_hash = Column(String(255), nullable=True, comment="密码哈希（验证码登录可为空）")
    avatar = Column(String(255), nullable=True, default="", comment="头像URL")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    capsules = relationship("Capsule", back_populates="owner", cascade="all, delete-orphan")
    emotions = relationship("Emotion", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

class VerificationCode(Base):
    """验证码模型"""
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), nullable=False, index=True, comment="手机号")
    code = Column(String(10), nullable=False, comment="验证码")
    is_used = Column(Boolean, default=False, comment="是否已使用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")

class Capsule(Base):
    """胶囊模型"""
    __tablename__ = "capsules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    type = Column(String(20), nullable=False, index=True, comment="胶囊类型: target/emotion/gratitude/share")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容（加密存储）")
    target = Column(Text, nullable=True, comment="目标描述（目标胶囊，加密存储）")
    unlock_date = Column(DateTime, nullable=False, index=True, comment="解锁时间")
    is_unlocked = Column(Boolean, default=False, index=True, comment="是否已解锁")
    is_shared = Column(Boolean, default=False, comment="是否共享")
    share_code = Column(String(20), nullable=True, unique=True, index=True, comment="共享码")
    tags = Column(String(500), nullable=True, comment="标签（JSON数组字符串）")
    progress = Column(Integer, default=0, comment="完成进度（0-100，目标胶囊）")
    emotion_score = Column(Integer, nullable=True, comment="情绪评分（0-4，心境胶囊）")
    review = Column(Text, nullable=True, comment="回顾内容")
    like_count = Column(Integer, default=0, comment="点赞数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    owner = relationship("User", back_populates="capsules")
    comments = relationship("Comment", back_populates="capsule", cascade="all, delete-orphan")
    likes = relationship("CapsuleLike", back_populates="capsule", cascade="all, delete-orphan")

class Emotion(Base):
    """情绪记录模型"""
    __tablename__ = "emotions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=True, comment="关联胶囊ID")
    score = Column(Integer, nullable=False, comment="情绪评分（0-4）")
    date = Column(DateTime, nullable=False, index=True, comment="记录日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="emotions")
    capsule = relationship("Capsule")

class Achievement(Base):
    """成就定义模型"""
    __tablename__ = "achievements"
    
    id = Column(String(50), primary_key=True, comment="成就ID")
    title = Column(String(100), nullable=False, comment="成就标题")
    description = Column(String(500), nullable=True, comment="成就描述")
    icon = Column(String(10), nullable=True, comment="成就图标")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

class UserAchievement(Base):
    """用户成就模型"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    achievement_id = Column(String(50), ForeignKey("achievements.id"), nullable=False, index=True, comment="成就ID")
    unlocked_at = Column(DateTime, server_default=func.now(), comment="解锁时间")
    
    # 关系
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    content = Column(Text, nullable=False, comment="评论内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    capsule = relationship("Capsule", back_populates="comments")
    user = relationship("User", back_populates="comments")

class CapsuleLike(Base):
    """胶囊点赞模型"""
    __tablename__ = "capsule_likes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    capsule = relationship("Capsule", back_populates="likes")
    
    # 唯一约束：一个用户只能对一个胶囊点赞一次
    from sqlalchemy import UniqueConstraint
    __table_args__ = (
        UniqueConstraint('capsule_id', 'user_id', name='uq_capsule_user_like'),
    )

