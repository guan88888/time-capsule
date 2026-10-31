import os
"""
短信验证码服务 - 使用阿里云DYPNS号码认证服务
"""
from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
from alibabacloud_tea_util import models as util_models
import json

# 阿里云配置信息
ALIYUN_ACCESS_KEY_ID = os.environ["ALIYUN_ACCESS_KEY_ID"]
ALIYUN_ACCESS_KEY_SECRET = os.environ["ALIYUN_ACCESS_KEY_SECRET"]
ALIYUN_SIGN_NAME = '速通互联验证码'
ALIYUN_ENDPOINT = 'dypnsapi.aliyuncs.com'

# 模板代码映射
TEMPLATE_CODES = {
    'register': '100001',           # 注册/登录
    'login': '100001',              # 注册/登录
    'change_phone': '100002',       # 修改手机号
    'reset_password': '100003',     # 重置密码
    'bind_phone': '100004',         # 绑定新手机号
    'verify_bind_phone': '100005'   # 验证绑定手机号
}

# 错误码映射
ERROR_MESSAGES = {
    'MOBILE_NUMBER_ILLEGAL': '手机号格式不正确',
    'BUSINESS_LIMIT_CONTROL': '发送次数超限，请明天再试',
    'FREQUENCY_FAIL': '发送太频繁，请稍后再试'
}


def _get_client():
    """创建阿里云客户端"""
    config = open_api_models.Config(
        access_key_id=ALIYUN_ACCESS_KEY_ID,
        access_key_secret=ALIYUN_ACCESS_KEY_SECRET,
        endpoint=ALIYUN_ENDPOINT
    )
    return DypnsapiClient(config)


def send_sms(phone: str, scene: str = 'register') -> dict:
    """
    发送短信验证码
    
    Args:
        phone: 手机号
        scene: 场景类型 (register/login/reset_password/change_phone/bind_phone/verify_bind_phone)
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'code': str (可选，仅在成功时返回)
        }
    """
    try:
        # 获取模板代码
        template_code = TEMPLATE_CODES.get(scene, TEMPLATE_CODES['register'])
        
        # 创建客户端
        client = _get_client()
        
        # 创建请求
        request = dypnsapi_models.SendSmsVerifyCodeRequest(
            phone_number=phone,
            sign_name=ALIYUN_SIGN_NAME,
            template_code=template_code,
            template_param=json.dumps({"code": "##code##", "min": "5"}),  # 阿里云自动生成验证码
            code_length=6,      # 6位验证码
            valid_time=300,     # 5分钟有效
            interval=60,        # 60秒发送间隔
            code_type=1         # 纯数字
        )
        
        # 发送请求
        runtime = util_models.RuntimeOptions()
        response = client.send_sms_verify_code_with_options(request, runtime)
        
        # 解析响应
        if response.status_code == 200:
            body = response.body
            if body.code == 'OK':
                return {
                    'success': True,
                    'message': '验证码发送成功',
                    'code': body.model.code if hasattr(body, 'model') and hasattr(body.model, 'code') else None
                }
            else:
                # 处理错误码
                error_code = body.code
                error_message = body.message if hasattr(body, 'message') else ''
                
                # 添加调试日志
                print(f"[DEBUG] 发送短信API返回错误 - code: {error_code}, message: {error_message}")
                
                # 检查是否是频率限制错误（多种可能的错误码和消息）
                error_code_lower = error_code.lower() if error_code else ''
                error_message_lower = error_message.lower() if error_message else ''
                
                if (error_code == 'Throttling.User' or 
                    'FREQUENCY_FAIL' in error_code or 
                    'frequency' in error_code_lower or
                    'check frequency' in error_message_lower or
                    '发送太频繁' in error_message or 
                    '频繁' in error_message):
                    return {
                        'success': False,
                        'message': ERROR_MESSAGES.get('FREQUENCY_FAIL', '发送太频繁，请稍后再试')
                    }
                
                # 检查其他已知错误码
                error_message = ERROR_MESSAGES.get(error_code, error_message or '发送验证码失败')
                return {
                    'success': False,
                    'message': error_message
                }
        else:
            return {
                'success': False,
                'message': f'请求失败，状态码: {response.status_code}'
            }
            
    except Exception as e:
        # 处理异常，打印详细错误信息用于调试
        import traceback
        error_str = str(e)
        error_str_lower = error_str.lower()
        error_trace = traceback.format_exc()
        
        # 打印详细错误信息到控制台（用于调试）
        print(f"发送短信验证码时发生错误:")
        print(f"错误信息: {error_str}")
        print(f"错误堆栈: {error_trace}")
        
        # 检查是否是已知错误码（不区分大小写）
        if 'frequency' in error_str_lower or 'throttling' in error_str_lower or '频繁' in error_str or '60' in error_str:
            return {
                'success': False,
                'message': ERROR_MESSAGES.get('FREQUENCY_FAIL', '发送太频繁，请稍后再试')
            }
        
        # 检查是否是手机号格式错误
        if 'mobile' in error_str_lower or 'phone' in error_str_lower or '手机号' in error_str:
            return {
                'success': False,
                'message': ERROR_MESSAGES.get('MOBILE_NUMBER_ILLEGAL', '手机号格式不正确')
            }
        
        # 检查其他已知错误码
        for error_code, error_msg in ERROR_MESSAGES.items():
            if error_code.lower() in error_str_lower:
                return {
                    'success': False,
                    'message': error_msg
                }
        
        # 返回详细错误信息（开发环境），生产环境可以简化
        # 注意：在生产环境中，应该只返回用户友好的错误信息，而不是详细的错误堆栈
        return {
            'success': False,
            'message': f'发送验证码失败: {error_str}'
        }


def check_sms_code(phone: str, code: str) -> dict:
    """
    校验短信验证码
    
    Args:
        phone: 手机号
        code: 验证码
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'verify_result': str (可选，仅在成功时返回)
        }
    """
    try:
        # 创建客户端
        client = _get_client()
        
        # 创建请求
        request = dypnsapi_models.CheckSmsVerifyCodeRequest(
            phone_number=phone,
            verify_code=code
        )
        
        # 发送请求
        runtime = util_models.RuntimeOptions()
        response = client.check_sms_verify_code_with_options(request, runtime)
        
        # 解析响应
        if response.status_code == 200:
            body = response.body
            # 添加调试日志
            print(f"[DEBUG] 验证码校验响应 - status_code: {response.status_code}")
            print(f"[DEBUG] body.code: {getattr(body, 'code', 'N/A')}")
            print(f"[DEBUG] body 属性: {dir(body)}")
            
            if hasattr(body, 'model'):
                print(f"[DEBUG] body.model 属性: {dir(body.model)}")
                if hasattr(body.model, 'verify_result'):
                    print(f"[DEBUG] body.model.verify_result: {body.model.verify_result}")
            
            if body.code == 'OK':
                # 检查验证结果
                verify_result = None
                if hasattr(body, 'model') and hasattr(body.model, 'verify_result'):
                    verify_result = body.model.verify_result
                elif hasattr(body, 'verify_result'):
                    verify_result = body.verify_result
                
                print(f"[DEBUG] 最终 verify_result: {verify_result}")
                
                if verify_result == 'PASS':
                    return {
                        'success': True,
                        'message': '验证码校验成功',
                        'verify_result': verify_result
                    }
                else:
                    # 验证失败，返回友好提示
                    error_msg = f"验证码错误或已过期（verify_result: {verify_result}）"
                    print(f"[DEBUG] {error_msg}")
                    return {
                        'success': False,
                        'message': '验证码错误或已过期，请重新获取'
                    }
            else:
                # 处理错误码
                error_code = body.code if hasattr(body, 'code') else ''
                error_message = body.message if hasattr(body, 'message') else '验证码校验失败'
                
                print(f"[DEBUG] API返回错误 - code: {error_code}, message: {error_message}")
                
                # 检查是否是验证失败错误
                if 'ValidateFail' in error_code or '验证失败' in error_message:
                    return {
                        'success': False,
                        'message': '验证码错误或已过期，请重新获取'
                    }
                
                # 返回友好的错误信息
                return {
                    'success': False,
                    'message': error_message or '验证码校验失败'
                }
        else:
            return {
                'success': False,
                'message': f'请求失败，状态码: {response.status_code}'
            }
            
    except Exception as e:
        # 处理异常，提供更友好的错误信息
        error_str = str(e)
        error_str_lower = error_str.lower()
        
        # 检查是否是验证失败错误
        if 'validatefail' in error_str_lower or '验证失败' in error_str:
            return {
                'success': False,
                'message': '验证码错误或已过期，请重新获取'
            }
        
        # 打印详细错误信息用于调试
        import traceback
        print(f"校验验证码异常:")
        print(f"错误信息: {error_str}")
        print(f"错误堆栈: {traceback.format_exc()}")
        
        return {
            'success': False,
            'message': '验证码校验失败，请重试'
        }


# 为了保持向后兼容，保留旧的方法
def generate_verification_code(length=6):
    """生成验证码（仅用于测试，实际使用阿里云自动生成）"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
