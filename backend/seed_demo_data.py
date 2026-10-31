#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时空胶囊 - 测试数据生成脚本

运行方式：
    python3 seed_demo_data.py

或者：
    cd backend
    python3 seed_demo_data.py

功能：
    1. 清空所有表的数据（可选）
    2. 生成演示数据，包括：
       - 用户数据
       - 成就定义
       - 胶囊数据（各种类型）
       - 情绪记录
       - 用户成就
       - 评论和点赞
    3. 显示插入统计信息

注意：
    - 确保MySQL服务已启动
    - 确保数据库 my_app 已创建
    - 确保已安装所有依赖：pip install -r requirements.txt
"""

import sys
import json
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

# 导入数据库相关
from app.database import SessionLocal, engine
from app.models import (
    User, VerificationCode, Capsule, Emotion, Achievement, 
    UserAchievement, Comment, CapsuleLike
)
from app.utils import get_password_hash

# 成就定义（与 achievements.py 保持一致）
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

def generate_share_code():
    """生成8位随机共享码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def clear_all_data(db: Session):
    """清空所有表的数据"""
    print("正在清空所有表的数据...")
    try:
        # 注意：由于外键约束，需要按顺序删除
        db.query(CapsuleLike).delete()
        db.query(Comment).delete()
        db.query(Emotion).delete()
        db.query(UserAchievement).delete()
        db.query(Capsule).delete()
        db.query(VerificationCode).delete()
        db.query(Achievement).delete()
        db.query(User).delete()
        db.commit()
        print("✓ 所有表数据已清空")
    except Exception as e:
        db.rollback()
        print(f"✗ 清空数据失败: {e}")
        raise

def seed_users(db: Session):
    """生成用户数据"""
    print("\n正在生成用户数据...")
    
    users_data = [
        {
            "nickname": "时空旅行者",
            "email": "contact@example.invalid",
            "phone": "19982442654",
            "password": "123456",
            "avatar": None
        },
        {
            "nickname": "心情记录者",
            "email": "contact@example.invalid",
            "phone": "19989012290",
            "password": "123456",
            "avatar": None
        },
        {
            "nickname": "目标达成者",
            "email": "contact@example.invalid",
            "phone": "19964996120",
            "password": "123456",
            "avatar": None
        },
    ]
    
    users = []
    for user_data in users_data:
        # 检查用户是否已存在（通过邮箱或手机号）
        existing_user = None
        if user_data["email"]:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user and user_data["phone"]:
            existing_user = db.query(User).filter(User.phone == user_data["phone"]).first()
        
        if existing_user:
            # 如果用户已存在，更新密码（确保可以登录）
            existing_user.password_hash = get_password_hash(user_data["password"])
            existing_user.nickname = user_data["nickname"]
            existing_user.is_active = True
            users.append(existing_user)
            print(f"  - 用户已存在，已更新: {user_data['nickname']}")
        else:
            # 创建新用户
            user = User(
                nickname=user_data["nickname"],
                email=user_data["email"],
                phone=user_data["phone"],
                password_hash=get_password_hash(user_data["password"]),
                avatar=user_data["avatar"],
                is_active=True
            )
            db.add(user)
            users.append(user)
    
    db.commit()
    for user in users:
        db.refresh(user)
    
    print(f"✓ 已确保 {len(users)} 个用户存在")
    return users

def seed_achievements(db: Session):
    """生成成就定义数据"""
    print("\n正在生成成就定义数据...")
    
    achievements = []
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
            achievements.append(achievement)
        else:
            achievements.append(existing)
    
    db.commit()
    print(f"✓ 已确保 {len(achievements)} 个成就定义存在")
    return achievements

def seed_capsules(db: Session, users: list):
    """生成胶囊数据"""
    print("\n正在生成胶囊数据...")
    
    now = datetime.now()
    capsules = []
    used_share_codes = set()  # 跟踪已使用的共享码，避免重复
    
    # 为每个用户创建不同类型的胶囊
    for user_idx, user in enumerate(users):
        # 目标胶囊 - 已解锁
        target_capsule = Capsule(
            user_id=user.id,
            type="target",
            title="完成一次马拉松",
            content="希望能在明年完成一次全程马拉松，目标是4小时内完成。",
            target="完成全程马拉松，用时4小时以内",
            unlock_date=now - timedelta(days=5),
            is_unlocked=True,
            is_shared=False,
            share_code=None,
            tags=json.dumps(["运动", "目标", "挑战"]),
            progress=75,
            emotion_score=None,
            review="已经完成了半程马拉松，正在为全程做准备。",
            like_count=0
        )
        db.add(target_capsule)
        capsules.append(target_capsule)
        
        # 目标胶囊 - 未解锁
        target_capsule2 = Capsule(
            user_id=user.id,
            type="target",
            title="学会一门新语言",
            content="想要在6个月内学会日语基础，能够进行日常对话。",
            target="6个月内掌握日语基础，能进行日常对话",
            unlock_date=now + timedelta(days=30),
            is_unlocked=False,
            is_shared=False,
            share_code=None,
            tags=json.dumps(["学习", "语言", "日语"]),
            progress=0,
            emotion_score=None,
            review=None,
            like_count=0
        )
        db.add(target_capsule2)
        capsules.append(target_capsule2)
        
        # 心境胶囊 - 已解锁
        emotion_capsule = Capsule(
            user_id=user.id,
            type="emotion",
            title="今天的心情",
            content="今天天气很好，心情也很不错。完成了工作上的一个重要任务，感觉很有成就感。",
            target=None,
            unlock_date=now - timedelta(days=2),
            is_unlocked=True,
            is_shared=False,
            share_code=None,
            tags=json.dumps(["心情", "工作", "成就感"]),
            progress=0,
            emotion_score=4,
            review="回顾这一天，确实是很充实的一天。",
            like_count=0
        )
        db.add(emotion_capsule)
        capsules.append(emotion_capsule)
        
        # 心境胶囊 - 未解锁
        emotion_capsule2 = Capsule(
            user_id=user.id,
            type="emotion",
            title="未来的心情",
            content="期待未来的自己能够保持积极乐观的心态。",
            target=None,
            unlock_date=now + timedelta(days=15),
            is_unlocked=False,
            is_shared=False,
            share_code=None,
            tags=json.dumps(["期待", "未来"]),
            progress=0,
            emotion_score=None,
            review=None,
            like_count=0
        )
        db.add(emotion_capsule2)
        capsules.append(emotion_capsule2)
        
        # 感恩胶囊 - 已解锁
        gratitude_capsule = Capsule(
            user_id=user.id,
            type="gratitude",
            title="感谢家人",
            content="感谢家人一直以来的支持和理解，让我能够专注于自己的事业。",
            target=None,
            unlock_date=now - timedelta(days=7),
            is_unlocked=True,
            is_shared=False,
            share_code=None,
            tags=json.dumps(["感恩", "家人", "支持"]),
            progress=0,
            emotion_score=None,
            review="家人永远是我最坚强的后盾。",
            like_count=0
        )
        db.add(gratitude_capsule)
        capsules.append(gratitude_capsule)
        
        # 共享胶囊 - 已解锁
        # 生成唯一的共享码
        share_code1 = generate_share_code()
        while share_code1 in used_share_codes:
            share_code1 = generate_share_code()
        used_share_codes.add(share_code1)
        
        share_capsule = Capsule(
            user_id=user.id,
            type="share",
            title="分享我的梦想",
            content="我的梦想是环游世界，体验不同国家的文化和风景。",
            target=None,
            unlock_date=now - timedelta(days=3),
            is_unlocked=True,
            is_shared=True,
            share_code=share_code1,
            tags=json.dumps(["分享", "梦想", "旅行"]),
            progress=0,
            emotion_score=None,
            review="希望有更多人能够实现自己的梦想。",
            like_count=0  # 初始为0，后续由点赞数据更新
        )
        db.add(share_capsule)
        capsules.append(share_capsule)
        
        # 共享胶囊 - 未解锁
        # 生成唯一的共享码
        share_code2 = generate_share_code()
        while share_code2 in used_share_codes:
            share_code2 = generate_share_code()
        used_share_codes.add(share_code2)
        
        share_capsule2 = Capsule(
            user_id=user.id,
            type="share",
            title="未来的计划",
            content="计划在未来一年内完成几个重要目标。",
            target=None,
            unlock_date=now + timedelta(days=60),
            is_unlocked=False,
            is_shared=True,
            share_code=share_code2,
            tags=json.dumps(["计划", "未来"]),
            progress=0,
            emotion_score=None,
            review=None,
            like_count=0
        )
        db.add(share_capsule2)
        capsules.append(share_capsule2)
    
    db.commit()
    for capsule in capsules:
        db.refresh(capsule)
    
    print(f"✓ 已创建 {len(capsules)} 个胶囊")
    return capsules

def seed_emotions(db: Session, users: list, capsules: list):
    """生成情绪记录数据"""
    print("\n正在生成情绪记录数据...")
    
    emotions = []
    now = datetime.now()
    
    # 为每个用户生成最近30天的情绪记录
    for user in users:
        # 找到该用户已解锁的心境胶囊
        user_emotion_capsules = [c for c in capsules if c.user_id == user.id and c.type == "emotion" and c.is_unlocked]
        
        for day in range(30):
            date = now - timedelta(days=day)
            # 随机生成情绪评分（0-4）
            score = random.randint(0, 4)
            
            # 如果有对应的胶囊，关联到胶囊
            capsule_id = None
            if user_emotion_capsules and random.random() > 0.7:
                capsule_id = random.choice(user_emotion_capsules).id
            
            emotion = Emotion(
                user_id=user.id,
                capsule_id=capsule_id,
                score=score,
                date=date
            )
            db.add(emotion)
            emotions.append(emotion)
    
    db.commit()
    print(f"✓ 已创建 {len(emotions)} 条情绪记录")
    return emotions

def seed_user_achievements(db: Session, users: list, achievements: list):
    """生成用户成就数据"""
    print("\n正在生成用户成就数据...")
    
    user_achievements = []
    
    # 为第一个用户解锁部分成就
    if users and achievements:
        user = users[0]
        # 解锁前4个成就
        for achievement in achievements[:4]:
            # 检查是否已存在
            existing = db.query(UserAchievement).filter(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == achievement.id
            ).first()
            if not existing:
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id
                )
                db.add(user_achievement)
                user_achievements.append(user_achievement)
        
        # 为第二个用户解锁2个成就
        if len(users) > 1:
            user2 = users[1]
            for achievement in achievements[:2]:
                # 检查是否已存在
                existing = db.query(UserAchievement).filter(
                    UserAchievement.user_id == user2.id,
                    UserAchievement.achievement_id == achievement.id
                ).first()
                if not existing:
                    user_achievement = UserAchievement(
                        user_id=user2.id,
                        achievement_id=achievement.id
                    )
                    db.add(user_achievement)
                    user_achievements.append(user_achievement)
    
    db.commit()
    print(f"✓ 已创建 {len(user_achievements)} 条用户成就记录")
    return user_achievements

def seed_comments(db: Session, users: list, capsules: list):
    """生成评论数据"""
    print("\n正在生成评论数据...")
    
    comments = []
    # 只对共享胶囊添加评论
    shared_capsules = [c for c in capsules if c.is_shared]
    
    comments_data = [
        "这个想法很棒！",
        "我也想要实现类似的梦想。",
        "加油！你一定可以的！",
        "很棒的分享，谢谢！",
        "期待看到你的进展。",
        "非常有意义的分享！",
        "支持你！",
    ]
    
    # 对已解锁的共享胶囊添加评论（至少2个）
    unlocked_shared = [c for c in shared_capsules if c.is_unlocked]
    for capsule in unlocked_shared[:3]:  # 对前3个已解锁的共享胶囊添加评论
        # 每个胶囊添加2-3条评论
        num_comments = random.randint(2, 3)
        # 确保评论用户不包括胶囊所有者
        available_users = [u for u in users if u.id != capsule.user_id]
        if available_users:
            comment_users = random.sample(available_users, min(num_comments, len(available_users)))
            for comment_user in comment_users:
                comment = Comment(
                    capsule_id=capsule.id,
                    user_id=comment_user.id,
                    content=random.choice(comments_data)
                )
                db.add(comment)
                comments.append(comment)
    
    db.commit()
    print(f"✓ 已创建 {len(comments)} 条评论")
    return comments

def seed_likes(db: Session, users: list, capsules: list):
    """生成点赞数据"""
    print("\n正在生成点赞数据...")
    
    likes = []
    # 只对共享胶囊添加点赞
    shared_capsules = [c for c in capsules if c.is_shared]
    
    for capsule in shared_capsules:
        # 随机选择一些用户点赞（不包括胶囊所有者）
        likers = [u for u in users if u.id != capsule.user_id]
        if not likers:
            continue
        
        # 对已解锁的共享胶囊，至少添加1个点赞
        min_likes = 1 if capsule.is_unlocked else 0
        max_likes = min(3, len(likers))
        num_likes = random.randint(min_likes, max_likes) if max_likes > 0 else 0
        
        if num_likes > 0:
            like_users = random.sample(likers, num_likes)
            for like_user in like_users:
                # 检查是否已点赞（避免重复）
                existing = db.query(CapsuleLike).filter(
                    CapsuleLike.capsule_id == capsule.id,
                    CapsuleLike.user_id == like_user.id
                ).first()
                if not existing:
                    like = CapsuleLike(
                        capsule_id=capsule.id,
                        user_id=like_user.id
                    )
                    db.add(like)
                    likes.append(like)
    
    db.commit()
    
    # 更新胶囊的点赞数（确保与实际点赞记录一致）
    for capsule in shared_capsules:
        like_count = db.query(CapsuleLike).filter(CapsuleLike.capsule_id == capsule.id).count()
        capsule.like_count = like_count
    db.commit()
    
    # 刷新胶囊对象以获取更新后的数据
    for capsule in shared_capsules:
        db.refresh(capsule)
    
    print(f"✓ 已创建 {len(likes)} 条点赞记录")
    return likes

def print_statistics(db: Session):
    """打印数据统计信息"""
    print("\n" + "="*60)
    print("数据统计信息")
    print("="*60)
    
    stats = {
        "用户": db.query(User).count(),
        "成就定义": db.query(Achievement).count(),
        "胶囊": db.query(Capsule).count(),
        "情绪记录": db.query(Emotion).count(),
        "用户成就": db.query(UserAchievement).count(),
        "评论": db.query(Comment).count(),
        "点赞": db.query(CapsuleLike).count(),
    }
    
    for table_name, count in stats.items():
        print(f"  {table_name:12s}: {count:4d} 条")
    
    # 胶囊类型统计
    print("\n胶囊类型统计:")
    capsule_types = db.query(Capsule.type, func.count(Capsule.id)).group_by(Capsule.type).all()
    for ctype, count in capsule_types:
        type_names = {
            "target": "目标胶囊",
            "emotion": "心境胶囊",
            "gratitude": "感恩胶囊",
            "share": "共享胶囊"
        }
        print(f"  {type_names.get(ctype, ctype):12s}: {count:4d} 个")
    
    # 解锁状态统计
    print("\n胶囊解锁状态:")
    unlocked_count = db.query(Capsule).filter(Capsule.is_unlocked == True).count()
    locked_count = db.query(Capsule).filter(Capsule.is_unlocked == False).count()
    print(f"  已解锁: {unlocked_count:4d} 个")
    print(f"  未解锁: {locked_count:4d} 个")
    
    # 用户信息
    print("\n测试用户账号:")
    users = db.query(User).all()
    for user in users:
        login_info = user.email or user.phone
        print(f"  昵称: {user.nickname:12s} | 账号: {login_info:20s} | 密码: REDACTED_SECRET")
    
    # 共享胶囊信息（用于测试共享功能）
    print("\n共享胶囊信息（用于测试 share-unlock 页面）:")
    shared_capsules = db.query(Capsule).filter(Capsule.is_shared == True, Capsule.share_code.isnot(None)).limit(3).all()
    for capsule in shared_capsules:
        owner = db.query(User).filter(User.id == capsule.user_id).first()
        print(f"  标题: {capsule.title:20s} | 共享码: {capsule.share_code:8s} | 所有者: {owner.nickname if owner else '未知'}")
    
    print("\n" + "="*60)
    print("测试数据生成完成！")
    print("="*60)
    print("\n提示：")
    print("  - 可以使用任意测试用户账号登录（密码：REDACTED_SECRET）")
    print("  - 共享胶囊可以通过共享码在 share-unlock 页面查看")
    print("  - 情绪日历会显示最近30天的情绪记录")
    print("  - 成就中心会显示已解锁和未解锁的成就")
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("时空胶囊 - 测试数据生成脚本")
    print("="*60)
    
    # 询问是否清空旧数据
    clear_data = input("\n是否清空所有旧数据？(y/n，默认n): ").strip().lower()
    if clear_data == 'y':
        db = SessionLocal()
        try:
            clear_all_data(db)
        except Exception as e:
            print(f"错误: {e}")
            db.close()
            sys.exit(1)
        finally:
            db.close()
    else:
        print("跳过清空数据步骤")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 生成数据
        users = seed_users(db)
        achievements = seed_achievements(db)
        capsules = seed_capsules(db, users)
        emotions = seed_emotions(db, users, capsules)
        user_achievements = seed_user_achievements(db, users, achievements)
        comments = seed_comments(db, users, capsules)
        likes = seed_likes(db, users, capsules)
        
        # 打印统计信息
        print_statistics(db)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 生成数据失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
