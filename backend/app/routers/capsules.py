"""
胶囊相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from app.models import User
from datetime import datetime
import json
import random
import string

from app.database import get_db
from app.models import Capsule, Emotion, UserAchievement, Achievement, Comment, CapsuleLike, User
from app.schemas import (
    CreateCapsuleRequest, UpdateCapsuleRequest, SaveReviewRequest,
    CapsuleResponse, MessageResponse, CreateCommentRequest, CommentResponse
)
from app.middleware.auth import get_current_user, get_optional_user

router = APIRouter()

def generate_share_code(db: Session = None):
    """生成8位随机共享码，确保唯一性"""
    max_attempts = 10
    for _ in range(max_attempts):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if db:
            # 检查是否已存在
            existing = db.query(Capsule).filter(Capsule.share_code == code).first()
            if not existing:
                return code
        else:
            return code
    # 如果10次都重复（极小概率），返回带时间戳的码
    import time
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + str(int(time.time()))[-2:]

def capsule_to_response(capsule: Capsule, current_user_id: int = None, db: Session = None) -> CapsuleResponse:
    """将胶囊模型转换为响应"""
    tags = []
    if capsule.tags:
        try:
            tags = json.loads(capsule.tags)
        except:
            tags = []
    
    # 检查当前用户是否已点赞
    is_liked = False
    if current_user_id and db:
        existing_like = db.query(CapsuleLike).filter(
            CapsuleLike.capsule_id == capsule.id,
            CapsuleLike.user_id == current_user_id
        ).first()
        is_liked = existing_like is not None
    
    # 判断解锁状态：后端标记为已解锁 OR 时间已到
    now = datetime.now()
    effective_is_unlocked = capsule.is_unlocked or capsule.unlock_date <= now
    
    return CapsuleResponse(
        id=capsule.id,
        type=capsule.type,
        title=capsule.title,
        content=capsule.content,
        target=capsule.target,
        unlock_date=capsule.unlock_date,
        is_unlocked=effective_is_unlocked,  # 返回实际解锁状态
        is_shared=capsule.is_shared,
        share_code=capsule.share_code,
        tags=tags,
        progress=capsule.progress or 0,
        emotion_score=capsule.emotion_score,
        review=capsule.review,
        like_count=capsule.like_count or 0,
        is_liked=is_liked,
        created_at=capsule.created_at,
        updated_at=capsule.updated_at
    )

@router.get("", response_model=List[CapsuleResponse], summary="获取胶囊列表")
async def get_capsules(
    filter: Optional[str] = Query(None, description="筛选: all/locked/unlocked"),
    type: Optional[str] = Query(None, description="胶囊类型: target/emotion/gratitude/share"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的胶囊列表
    """
    query = db.query(Capsule).filter(Capsule.user_id == current_user.id)
    
    # 按类型筛选
    if type:
        query = query.filter(Capsule.type == type)
    
    # 按状态筛选
    now = datetime.now()
    if filter == "locked":
        # 未解锁：后端标记为未解锁 AND 时间未到
        query = query.filter(
            Capsule.is_unlocked == False,
            Capsule.unlock_date > now
        )
    elif filter == "unlocked":
        # 已解锁：后端标记为已解锁 OR 时间已到（即使未点击解锁，时间到了也算可解锁）
        query = query.filter(
            or_(
                Capsule.is_unlocked == True,
                Capsule.unlock_date <= now
            )
        )
    
    # 按创建时间倒序排列
    capsules = query.order_by(Capsule.created_at.desc()).all()
    
    return [capsule_to_response(c, current_user.id, db) for c in capsules]

@router.get("/{capsule_id}", response_model=CapsuleResponse, summary="获取胶囊详情")
async def get_capsule(
    capsule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取胶囊详情
    """
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.user_id == current_user.id
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    return capsule_to_response(capsule, current_user.id, db)

@router.post("", response_model=CapsuleResponse, summary="创建胶囊")
async def create_capsule(
    request: CreateCapsuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新胶囊
    """
    # 验证胶囊类型
    valid_types = ["target", "emotion", "gratitude", "share"]
    if request.type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的胶囊类型，有效类型: {', '.join(valid_types)}"
        )
    
    # 验证解锁时间
    if request.unlock_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="解锁时间必须晚于当前时间"
        )
    
    # 过滤标签中的空字符串
    filtered_tags = [tag.strip() for tag in request.tags if tag and tag.strip()] if request.tags else []
    
    # 创建胶囊
    capsule = Capsule(
        user_id=current_user.id,
        type=request.type,
        title=request.title.strip(),
        content=request.content.strip(),
        target=request.target.strip() if request.target else None,
        unlock_date=request.unlock_date,
        tags=json.dumps(filtered_tags) if filtered_tags else None,
        is_shared=request.allow_share and request.type == "share",
        share_code=generate_share_code(db) if request.allow_share and request.type == "share" else None
    )
    
    db.add(capsule)
    db.commit()
    db.refresh(capsule)
    
    # 检查是否解锁"初次体验"成就
    check_first_capsule_achievement(db, current_user.id)
    
    return capsule_to_response(capsule, current_user.id, db)

@router.put("/{capsule_id}", response_model=CapsuleResponse, summary="更新胶囊")
async def update_capsule(
    capsule_id: int,
    request: UpdateCapsuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新胶囊信息
    """
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.user_id == current_user.id
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    # 已解锁的胶囊不能修改内容（检查实际解锁状态：时间到了也算解锁）
    now = datetime.now()
    if capsule.is_unlocked or capsule.unlock_date <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已解锁的胶囊不能修改"
        )
    
    if request.title is not None:
        title = request.title.strip()
        if len(title) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标题不能为空"
            )
        if len(title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标题长度不能超过200个字符"
            )
        capsule.title = title
    
    if request.content is not None:
        content = request.content.strip()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="内容不能为空"
            )
        capsule.content = content
    
    if request.target is not None:
        capsule.target = request.target.strip() if request.target else None
    
    db.commit()
    db.refresh(capsule)
    
    return capsule_to_response(capsule, current_user.id, db)

@router.put("/{capsule_id}/unlock", response_model=CapsuleResponse, summary="解锁胶囊")
async def unlock_capsule(
    capsule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    解锁胶囊
    """
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.user_id == current_user.id
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    # 检查胶囊是否已解锁（检查实际解锁状态：时间到了也算解锁）
    now = datetime.now()
    if capsule.is_unlocked or capsule.unlock_date <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="胶囊已解锁" if capsule.is_unlocked else "胶囊已到达解锁时间，请直接查看"
        )
    
    # 检查是否到达解锁时间（这个检查实际上已经被上面的条件覆盖，但保留以提供更明确的错误信息）
    if capsule.unlock_date > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="还未到达解锁时间"
        )
    
    capsule.is_unlocked = True
    db.commit()
    db.refresh(capsule)
    
    # 检查解锁相关成就
    check_unlock_achievements(db, current_user.id)
    
    return capsule_to_response(capsule, current_user.id, db)

@router.put("/{capsule_id}/review", response_model=CapsuleResponse, summary="保存回顾")
async def save_review(
    capsule_id: int,
    request: SaveReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    保存胶囊回顾
    """
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.user_id == current_user.id
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    # 检查胶囊是否已解锁（时间到了或已点击解锁）
    now = datetime.now()
    if not capsule.is_unlocked and capsule.unlock_date > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="胶囊尚未解锁，无法保存回顾"
        )
    
    if request.review is not None:
        capsule.review = request.review
    
    if request.progress is not None:
        if capsule.type != "target":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有目标胶囊才能设置完成进度"
            )
        capsule.progress = request.progress
        # 检查目标达成成就
        if request.progress >= 100:
            check_target_achievement(db, current_user.id)
    
    if request.emotion_score is not None:
        if capsule.type != "emotion":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有心境胶囊才能设置情绪评分"
            )
        capsule.emotion_score = request.emotion_score
        # 保存情绪记录
        emotion = Emotion(
            user_id=current_user.id,
            capsule_id=capsule.id,
            score=request.emotion_score,
            date=datetime.now()
        )
        db.add(emotion)
        # 检查情绪相关成就
        if request.emotion_score >= 4:
            check_happy_mood_achievement(db, current_user.id)
    
    db.commit()
    db.refresh(capsule)
    
    # 检查回顾成就
    check_review_achievement(db, current_user.id)
    
    return capsule_to_response(capsule, current_user.id, db)

@router.delete("/{capsule_id}", response_model=MessageResponse, summary="删除胶囊")
async def delete_capsule(
    capsule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除胶囊
    """
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.user_id == current_user.id
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    db.delete(capsule)
    db.commit()
    
    return MessageResponse(message="胶囊删除成功")

# ========== 共享胶囊相关 ==========

@router.get("/share/{code}", response_model=CapsuleResponse, summary="通过共享码获取胶囊")
async def get_shared_capsule(
    code: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    通过共享码获取共享胶囊（允许匿名访问）
    """
    # 共享码统一转换为大写进行比较（确保大小写不敏感）
    capsule = db.query(Capsule).filter(
        func.upper(Capsule.share_code) == code.upper(),
        Capsule.is_shared == True
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到共享胶囊"
        )
    
    # 如果用户已登录，传递用户ID以检查是否已点赞
    current_user_id = current_user.id if current_user else None
    return capsule_to_response(capsule, current_user_id, db)

@router.post("/{capsule_id}/share", summary="生成共享码")
async def generate_share(
    capsule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为胶囊生成共享码
    """
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.user_id == current_user.id
    ).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    if not capsule.share_code:
        capsule.share_code = generate_share_code(db)
    capsule.is_shared = True
    
    db.commit()
    db.refresh(capsule)
    
    # 检查分享成就
    check_sharing_achievement(db, current_user.id)
    
    # 返回胶囊数据，包含更新后的共享码
    capsule_response = capsule_to_response(capsule, current_user.id, db)
    return {
        "message": f"共享码已生成: {capsule.share_code}",
        "success": True,
        "capsule": capsule_response  # 返回更新后的胶囊数据
    }

@router.post("/{capsule_id}/like", response_model=MessageResponse, summary="点赞/取消点赞胶囊")
async def toggle_like(
    capsule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    点赞或取消点赞胶囊
    """
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    # 只有共享胶囊才能被点赞
    if not capsule.is_shared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有共享胶囊才能被点赞"
        )
    
    # 检查是否已点赞
    existing_like = db.query(CapsuleLike).filter(
        CapsuleLike.capsule_id == capsule_id,
        CapsuleLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        # 取消点赞
        db.delete(existing_like)
        capsule.like_count = max(0, (capsule.like_count or 0) - 1)
        message = "已取消点赞"
    else:
        # 添加点赞
        like = CapsuleLike(capsule_id=capsule_id, user_id=current_user.id)
        db.add(like)
        capsule.like_count = (capsule.like_count or 0) + 1
        message = "点赞成功"
    
    db.commit()
    
    return MessageResponse(message=message)

@router.get("/{capsule_id}/comments", response_model=List[CommentResponse], summary="获取评论列表")
async def get_comments(
    capsule_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    获取胶囊评论列表（允许匿名访问，用于共享胶囊）
    """
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    # 检查胶囊是否是共享胶囊（共享胶囊的评论可以公开查看）
    if not capsule.is_shared:
        # 非共享胶囊，需要登录且必须是胶囊所有者
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要登录才能查看此胶囊的评论"
            )
        if capsule.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此胶囊的评论"
            )
    
    comments = db.query(Comment).filter(
        Comment.capsule_id == capsule_id
    ).order_by(Comment.created_at.desc()).all()
    
    result = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        result.append(CommentResponse(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            user_nickname=user.nickname if user else "未知用户",
            user_avatar=user.avatar if user else None,
            created_at=comment.created_at
        ))
    
    return result

@router.post("/{capsule_id}/comments", response_model=CommentResponse, summary="添加评论")
async def add_comment(
    capsule_id: int,
    request: CreateCommentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    添加评论
    """
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
    
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="胶囊不存在"
        )
    
    # 只有共享胶囊才能被评论
    if not capsule.is_shared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有共享胶囊才能被评论"
        )
    
    comment = Comment(
        capsule_id=capsule_id,
        user_id=current_user.id,
        content=request.content
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        user_nickname=current_user.nickname,
        user_avatar=current_user.avatar,
        created_at=comment.created_at
    )

# ========== 成就检查函数 ==========

def ensure_achievements_exist(db: Session):
    """确保成就定义存在"""
    achievements_data = [
        ("first_capsule", "初次体验", "创建第一个胶囊", "📦"),
        ("happy_mood", "心情愉悦", "情绪评分达到非常开心", "😊"),
        ("target_achiever", "目标达成", "完成一个目标胶囊", "🎯"),
        ("emotion_tracker", "情绪追踪", "记录7天情绪", "📊"),
        ("gratitude_master", "感恩大师", "创建10个感恩胶囊", "🙏"),
        ("sharing_love", "分享爱心", "分享5个胶囊", "🔗"),
        ("time_traveler", "时空旅行者", "解锁10个胶囊", "⏰"),
        ("reflection_master", "反思大师", "完成10次回顾", "💭"),
    ]
    
    for aid, title, desc, icon in achievements_data:
        existing = db.query(Achievement).filter(Achievement.id == aid).first()
        if not existing:
            achievement = Achievement(id=aid, title=title, description=desc, icon=icon)
            db.add(achievement)
    
    db.commit()

def unlock_achievement(db: Session, user_id: int, achievement_id: str):
    """解锁成就"""
    # 确保成就定义存在
    ensure_achievements_exist(db)
    
    # 检查是否已解锁
    existing = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.achievement_id == achievement_id
    ).first()
    
    if not existing:
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id
        )
        db.add(user_achievement)
        db.commit()

def check_first_capsule_achievement(db: Session, user_id: int):
    """检查是否解锁'初次体验'成就"""
    count = db.query(Capsule).filter(Capsule.user_id == user_id).count()
    if count == 1:
        unlock_achievement(db, user_id, "first_capsule")

def check_happy_mood_achievement(db: Session, user_id: int):
    """检查是否解锁'心情愉悦'成就"""
    unlock_achievement(db, user_id, "happy_mood")

def check_target_achievement(db: Session, user_id: int):
    """检查是否解锁'目标达成'成就"""
    unlock_achievement(db, user_id, "target_achiever")

def check_unlock_achievements(db: Session, user_id: int):
    """检查解锁相关成就"""
    count = db.query(Capsule).filter(
        Capsule.user_id == user_id,
        Capsule.is_unlocked == True
    ).count()
    if count >= 10:
        unlock_achievement(db, user_id, "time_traveler")

def check_review_achievement(db: Session, user_id: int):
    """检查回顾相关成就"""
    count = db.query(Capsule).filter(
        Capsule.user_id == user_id,
        Capsule.review != None,
        Capsule.review != ""
    ).count()
    if count >= 10:
        unlock_achievement(db, user_id, "reflection_master")

def check_sharing_achievement(db: Session, user_id: int):
    """检查分享相关成就"""
    count = db.query(Capsule).filter(
        Capsule.user_id == user_id,
        Capsule.is_shared == True
    ).count()
    if count >= 5:
        unlock_achievement(db, user_id, "sharing_love")

