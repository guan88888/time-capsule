"""
成就相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Achievement, UserAchievement, User
from app.schemas import UserAchievementResponse, MessageResponse
from app.middleware.auth import get_current_user

router = APIRouter()

# 所有成就定义
ALL_ACHIEVEMENTS = [
    {"id": "first_capsule", "title": "初次体验", "description": "创建第一个胶囊", "icon": "📦"},
    {"id": "happy_mood", "title": "心情愉悦", "description": "情绪评分达到非常开心", "icon": "😊"},
    {"id": "target_achiever", "title": "目标达成", "description": "完成一个目标胶囊", "icon": "🎯"},
    {"id": "emotion_tracker", "title": "情绪追踪", "description": "记录7天情绪", "icon": "📊"},
    {"id": "gratitude_master", "title": "感恩大师", "description": "创建10个感恩胶囊", "icon": "🙏"},
    {"id": "sharing_love", "title": "分享爱心", "description": "分享5个胶囊", "icon": "🔗"},
    {"id": "time_traveler", "title": "时空旅行者", "description": "解锁10个胶囊", "icon": "⏰"},
    {"id": "reflection_master", "title": "反思大师", "description": "完成10次回顾", "icon": "💭"},
]

def ensure_achievements_exist(db: Session):
    """确保成就定义存在于数据库中"""
    for ach_data in ALL_ACHIEVEMENTS:
        existing = db.query(Achievement).filter(Achievement.id == ach_data["id"]).first()
        if not existing:
            achievement = Achievement(
                id=ach_data["id"],
                title=ach_data["title"],
                description=ach_data["description"],
                icon=ach_data["icon"]
            )
            db.add(achievement)
    db.commit()

@router.get("", response_model=List[UserAchievementResponse], summary="获取成就列表")
async def get_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的成就列表（包含已解锁和未解锁）
    """
    # 确保成就定义存在
    ensure_achievements_exist(db)
    
    # 获取用户已解锁的成就
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id
    ).all()
    
    unlocked_map = {ua.achievement_id: ua.unlocked_at for ua in user_achievements}
    
    # 构建响应
    result = []
    for ach_data in ALL_ACHIEVEMENTS:
        is_unlocked = ach_data["id"] in unlocked_map
        result.append(UserAchievementResponse(
            id=ach_data["id"],
            title=ach_data["title"],
            description=ach_data["description"],
            icon=ach_data["icon"],
            unlocked_at=unlocked_map.get(ach_data["id"]),
            is_unlocked=is_unlocked
        ))
    
    # 已解锁的排在前面
    result.sort(key=lambda x: (not x.is_unlocked, x.id))
    
    return result

@router.post("/{achievement_id}/unlock", response_model=MessageResponse, summary="解锁成就")
async def unlock_achievement(
    achievement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    手动解锁成就（通常由系统自动调用）
    """
    # 确保成就定义存在
    ensure_achievements_exist(db)
    
    # 检查成就是否存在
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成就不存在"
        )
    
    # 检查是否已解锁
    existing = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.achievement_id == achievement_id
    ).first()
    
    if existing:
        return MessageResponse(message="成就已解锁", success=True)
    
    # 解锁成就
    user_achievement = UserAchievement(
        user_id=current_user.id,
        achievement_id=achievement_id
    )
    db.add(user_achievement)
    db.commit()
    
    return MessageResponse(message=f"恭喜解锁成就：{achievement.title}！", success=True)

