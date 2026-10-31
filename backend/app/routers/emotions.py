"""
情绪相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Emotion, User, UserAchievement, Achievement
from app.schemas import CreateEmotionRequest, EmotionResponse, EmotionStatsResponse, MessageResponse
from app.middleware.auth import get_current_user

router = APIRouter()

@router.get("", response_model=List[EmotionResponse], summary="获取情绪记录列表")
async def get_emotions(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的情绪记录列表
    """
    query = db.query(Emotion).filter(Emotion.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Emotion.date >= start_date)
    if end_date:
        query = query.filter(Emotion.date <= end_date)
    
    emotions = query.order_by(Emotion.date.desc()).all()
    
    return [
        EmotionResponse(
            id=e.id,
            score=e.score,
            capsule_id=e.capsule_id,
            date=e.date,
            created_at=e.created_at
        )
        for e in emotions
    ]

@router.post("", response_model=EmotionResponse, summary="记录情绪")
async def create_emotion(
    request: CreateEmotionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    记录情绪
    """
    emotion = Emotion(
        user_id=current_user.id,
        capsule_id=request.capsule_id,
        score=request.score,
        date=request.date or datetime.now()
    )
    
    db.add(emotion)
    db.commit()
    db.refresh(emotion)
    
    # 检查情绪追踪成就
    check_emotion_tracker_achievement(db, current_user.id)
    
    return EmotionResponse(
        id=emotion.id,
        score=emotion.score,
        capsule_id=emotion.capsule_id,
        date=emotion.date,
        created_at=emotion.created_at
    )

@router.get("/calendar", summary="获取情绪日历数据")
async def get_emotion_calendar(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定月份的情绪日历数据
    """
    # 计算月份的开始和结束日期
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # 查询该月份的情绪记录
    emotions = db.query(Emotion).filter(
        Emotion.user_id == current_user.id,
        Emotion.date >= start_date,
        Emotion.date < end_date
    ).all()
    
    # 按日期分组，取每天最后一条记录的评分
    calendar_data = {}
    for emotion in emotions:
        date_str = emotion.date.strftime("%Y-%m-%d")
        calendar_data[date_str] = emotion.score
    
    return {
        "year": year,
        "month": month,
        "data": calendar_data
    }

@router.get("/stats", response_model=EmotionStatsResponse, summary="获取情绪统计")
async def get_emotion_stats(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取情绪统计数据
    """
    query = db.query(Emotion).filter(Emotion.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Emotion.date >= start_date)
    if end_date:
        query = query.filter(Emotion.date <= end_date)
    
    emotions = query.all()
    
    # 统计各评分数量
    by_score = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for emotion in emotions:
        if 0 <= emotion.score <= 4:
            by_score[emotion.score] += 1
    
    return EmotionStatsResponse(
        total=len(emotions),
        by_score=by_score
    )

def check_emotion_tracker_achievement(db: Session, user_id: int):
    """检查情绪追踪成就：记录7天情绪"""
    # 获取最近7天的日期
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    # 统计有情绪记录的不同日期数
    unique_days = db.query(func.count(func.distinct(cast(Emotion.date, Date)))).filter(
        Emotion.user_id == user_id,
        Emotion.date >= datetime.combine(seven_days_ago, datetime.min.time())
    ).scalar()
    
    if unique_days >= 7:
        # 检查是否已解锁
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == "emotion_tracker"
        ).first()
        
        if not existing:
            # 确保成就定义存在
            achievement = db.query(Achievement).filter(Achievement.id == "emotion_tracker").first()
            if not achievement:
                achievement = Achievement(
                    id="emotion_tracker",
                    title="情绪追踪",
                    description="记录7天情绪",
                    icon="📊"
                )
                db.add(achievement)
            
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id="emotion_tracker"
            )
            db.add(user_achievement)
            db.commit()

