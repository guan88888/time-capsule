"""
用户相关路由（个人资料、头像上传等）
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime
from app.database import get_db
from app.models import User
from app.schemas import UserInfo, MessageResponse
from app.middleware.auth import get_current_user

router = APIRouter()

# 头像上传目录
AVATAR_UPLOAD_DIR = "uploads/avatars"
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None

@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    """
    return UserInfo(
        id=current_user.id,
        nickname=current_user.nickname,
        email=current_user.email,
        phone=current_user.phone,
        avatar=current_user.avatar,
        created_at=current_user.created_at
    )

class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None

@router.put("/profile", response_model=UserInfo, summary="更新用户资料")
async def update_profile(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户资料
    
    - **nickname**: 昵称（可选）
    - **email**: 邮箱（可选）
    """
    # 更新昵称
    if request.nickname is not None:
        nickname = request.nickname.strip()
        if len(nickname) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称不能为空"
            )
        if len(nickname) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="昵称长度不能超过50个字符"
            )
        current_user.nickname = nickname
    
    # 更新邮箱
    if request.email is not None:
        from app.utils import is_email
        email = request.email.strip() if request.email else ""
        if email and not is_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式不正确"
            )
        # 检查邮箱是否已被其他用户使用
        if email:
            existing_user = db.query(User).filter(
                User.email == email,
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该邮箱已被其他用户使用"
                )
            current_user.email = email
        else:
            current_user.email = None
    
    db.commit()
    db.refresh(current_user)
    
    return UserInfo(
        id=current_user.id,
        nickname=current_user.nickname,
        email=current_user.email,
        phone=current_user.phone,
        avatar=current_user.avatar,
        created_at=current_user.created_at
    )

@router.post("/avatar", response_model=MessageResponse, summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传用户头像
    
    - **file**: 图片文件（支持jpg、png、gif等格式）
    """
    # 验证文件类型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式，仅支持: {', '.join(allowed_extensions)}"
        )
    
    # 验证文件大小（最大5MB）
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过5MB"
        )
    
    # 生成文件名：用户ID_时间戳.扩展名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{current_user.id}_{timestamp}{file_ext}"
    file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)
    
    # 如果用户已有头像，删除旧头像
    if current_user.avatar:
        old_avatar_path = current_user.avatar
        # 如果是相对路径，转换为完整路径
        if not os.path.isabs(old_avatar_path):
            old_avatar_path = os.path.join(AVATAR_UPLOAD_DIR, os.path.basename(old_avatar_path))
        if os.path.exists(old_avatar_path):
            try:
                os.remove(old_avatar_path)
            except:
                pass  # 忽略删除错误
    
    # 保存新头像
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    # 更新数据库中的头像路径（存储相对路径，用于URL访问）
    avatar_url = f"avatars/{filename}"
    current_user.avatar = avatar_url
    db.commit()
    
    # 返回完整的头像URL（前端需要拼接BASE_URL）
    return MessageResponse(
        message=f"头像上传成功|{avatar_url}",  # 使用|分隔消息和相对路径
        success=True
    )

@router.delete("/avatar", response_model=MessageResponse, summary="删除头像")
async def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户头像
    """
    if not current_user.avatar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前没有头像"
        )
    
    # 删除文件
    avatar_path = os.path.join(AVATAR_UPLOAD_DIR, os.path.basename(current_user.avatar))
    if os.path.exists(avatar_path):
        try:
            os.remove(avatar_path)
        except:
            pass
    
    # 更新数据库
    current_user.avatar = None
    db.commit()
    
    return MessageResponse(
        message="头像删除成功",
        success=True
    )

