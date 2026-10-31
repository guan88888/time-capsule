"""
认证相关路由（注册、登录、忘记密码、验证码登录）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, VerificationCode
from app.schemas import (
    RegisterRequest, LoginRequest, ForgotPasswordRequest,
    ResetPasswordRequest, AuthResponse, MessageResponse, UserInfo,
    SendCodeRequest, CodeLoginRequest
)
from app.utils import (
    get_password_hash, verify_password, create_access_token,
    is_email, is_phone
)
from app.services.sms_service import send_sms, check_sms_code, generate_verification_code

router = APIRouter()

@router.post("/register", response_model=AuthResponse, summary="用户注册")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **nickname**: 昵称
    - **account**: 邮箱或手机号
    - **password**: 密码（至少6位）
    - **sms_code**: 短信验证码（手机号注册时必需）
    """
    try:
        # 验证账号格式
        if not is_email(request.account) and not is_phone(request.account):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号格式不正确，请输入邮箱或手机号"
            )
        
        # 如果是手机号注册，验证短信验证码
        if is_phone(request.account):
            if not request.sms_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="手机号注册需要提供短信验证码"
                )
            
            # 校验短信验证码（使用阿里云API）
            verify_result = check_sms_code(request.account, request.sms_code)
            if not verify_result['success']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=verify_result['message']
                )
        
        # 检查用户是否已存在
        if is_email(request.account):
            existing_user = db.query(User).filter(User.email == request.account).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该邮箱已被注册"
                )
        else:
            existing_user = db.query(User).filter(User.phone == request.account).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已被注册"
                )
        
        # 创建新用户
        password_hash = get_password_hash(request.password)
        new_user = User(
            nickname=request.nickname,
            email=request.account if is_email(request.account) else None,
            phone=request.account if is_phone(request.account) else None,
            password_hash=password_hash
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 生成token
        token = create_access_token(data={"sub": str(new_user.id)})
        
        # 返回用户信息
        user_info = UserInfo(
            id=new_user.id,
            nickname=new_user.nickname,
            email=new_user.email,
            phone=new_user.phone,
            avatar=new_user.avatar,
            created_at=new_user.created_at
        )
        
        return AuthResponse(token=token, user=user_info)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"注册错误: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse, summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **account**: 邮箱或手机号
    - **password**: 密码
    """
    # 查找用户
    if is_email(request.account):
        user = db.query(User).filter(User.email == request.account).first()
    elif is_phone(request.account):
        user = db.query(User).filter(User.phone == request.account).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号格式不正确，请输入邮箱或手机号"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 生成token
    token = create_access_token(data={"sub": str(user.id)})
    
    # 返回用户信息
    user_info = UserInfo(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        created_at=user.created_at
    )
    
    return AuthResponse(token=token, user=user_info)

@router.post("/forgot-password", response_model=MessageResponse, summary="忘记密码")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    忘记密码（发送重置链接或验证码）
    
    - **account**: 邮箱或手机号
    """
    # 验证账号格式
    if not is_email(request.account) and not is_phone(request.account):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号格式不正确，请输入邮箱或手机号"
        )
    
    # 查找用户
    if is_email(request.account):
        user = db.query(User).filter(User.email == request.account).first()
    else:
        user = db.query(User).filter(User.phone == request.account).first()
    
    if not user:
        # 为了安全，不暴露用户是否存在
        return MessageResponse(
            message="如果该账号存在，重置链接已发送",
            success=True
        )
    
    # TODO: 这里应该发送邮件或短信验证码
    # 目前简化处理，直接返回成功消息
    # 实际项目中应该：
    # 1. 生成重置token或验证码
    # 2. 存储到数据库（带过期时间）
    # 3. 发送邮件或短信
    
    return MessageResponse(
        message="重置链接已发送，请查收邮件或短信",
        success=True
    )

@router.post("/reset-password", response_model=MessageResponse, summary="重置密码")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    重置密码
    
    - **account**: 邮箱或手机号
    - **new_password**: 新密码
    - **sms_code**: 短信验证码（手机号重置密码时必需）
    """
    # 验证账号格式
    if not is_email(request.account) and not is_phone(request.account):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号格式不正确，请输入邮箱或手机号"
        )
    
    # 手机号重置密码必须先验证验证码
    if is_phone(request.account):
        if not request.sms_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号重置密码需要提供短信验证码"
            )
        
        # 先校验短信验证码（使用阿里云API）
        verify_result = check_sms_code(request.account, request.sms_code)
        if not verify_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=verify_result['message']
            )
        
        # 验证码正确后，查找用户
        user = db.query(User).filter(User.phone == request.account).first()
    else:
        # 邮箱重置密码暂不支持
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱重置密码功能暂未开放，请使用手机号重置"
        )
    
    if not user:
        # 为了安全，不暴露用户是否存在（验证码已正确，但用户不存在）
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return MessageResponse(
        message="密码重置成功",
        success=True
    )

@router.post("/send-sms", response_model=MessageResponse, summary="发送短信验证码")
async def send_sms_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    """
    发送短信验证码
    
    - **phone**: 手机号
    - **scene**: 场景类型 (register/login/reset_password/change_phone/bind_phone/verify_bind_phone)
    """
    # 验证手机号格式
    if not is_phone(request.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 发送短信（使用阿里云API，会自动生成验证码并处理60秒间隔限制）
    try:
        sms_result = send_sms(request.phone, request.scene)
        
        if not sms_result['success']:
            # 如果是发送太频繁等业务错误，返回400，否则返回500
            if '发送太频繁' in sms_result['message'] or 'FREQUENCY_FAIL' in sms_result['message']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=sms_result['message']
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=sms_result['message']
                )
        
        # 发送成功，不需要保存到数据库
        # 注意：由于使用阿里云API自动生成和管理验证码，我们无法存储实际的验证码值
        # 验证码校验完全通过阿里云API进行，不需要在数据库中保存记录
        
        return MessageResponse(
            message="验证码已发送，请查收短信（5分钟内有效）",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"发送验证码接口异常:")
        print(f"错误信息: {str(e)}")
        print(f"错误堆栈: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送验证码时发生错误: {str(e)}"
        )


# 保留旧的 /send-code 接口以保持向后兼容
@router.post("/send-code", response_model=MessageResponse, summary="发送验证码（兼容接口）")
async def send_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    """发送验证码（兼容旧接口，默认场景为login，因为主要用于验证码登录）"""
    # /send-code 接口主要用于验证码登录，所以默认使用 login 场景
    # 如果前端没有传 scene，会使用 schema 中的默认值 "register"，这里改为 "login"
    if not hasattr(request, 'scene') or request.scene == "register":
        request.scene = "login"
    return await send_sms_code(request, db)

@router.post("/code-login", response_model=AuthResponse, summary="验证码登录")
async def code_login(request: CodeLoginRequest, db: Session = Depends(get_db)):
    """
    验证码登录
    
    - **phone**: 手机号
    - **code**: 验证码
    """
    # 验证手机号格式
    if not is_phone(request.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 使用阿里云API校验短信验证码（不再使用数据库校验）
    verify_result = check_sms_code(request.phone, request.code)
    if not verify_result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=verify_result['message']
        )
    
    # 验证码校验成功，查找或创建用户
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # 如果用户不存在，自动创建用户
        user = User(
            nickname=f"用户{request.phone[-4:]}",  # 默认昵称为手机号后4位
            phone=request.phone,
            password_hash=None,  # 验证码登录不需要密码
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 检查用户是否激活
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
    
    # 生成token
    token = create_access_token(data={"sub": str(user.id)})
    
    # 返回用户信息
    user_info = UserInfo(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        created_at=user.created_at
    )
    
    return AuthResponse(token=token, user=user_info)

