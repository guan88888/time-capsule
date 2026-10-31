"""
火山方舟AI服务封装
"""
import requests
import json
import logging
from typing import Optional, List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.api_key = settings.volcano_ark_api_key
        self.api_url = settings.volcano_ark_api_url
        self.model = settings.volcano_ark_model
        self.max_tokens = settings.ai_max_tokens
        self.temperature = settings.ai_temperature
        self.enable_thinking = settings.ai_enable_thinking
    
    def _call_api(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        调用火山方舟API
        
        Args:
            prompt: 用户提示词
            max_tokens: 最大token数
            temperature: 温度参数（0-1）
            system_prompt: 系统提示词
            
        Returns:
            API响应结果
        """
        if not self.api_key:
            raise ValueError("AI API Key未配置")
        
        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # 构建请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature
        }
        
        # 关闭深度思考
        if not self.enable_thinking:
            data["thinking"] = {"type": "disabled"}
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            logger.info(f"[AI] 调用API: model={self.model}, prompt_length={len(prompt)}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30  # 30秒超时
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取返回内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                return {
                    "success": True,
                    "content": content,
                    "raw_response": result
                }
            else:
                logger.error(f"[AI] API响应格式异常: {result}")
                return {
                    "success": False,
                    "error": "API响应格式异常",
                    "raw_response": result
                }
                
        except requests.exceptions.Timeout:
            logger.error("[AI] API请求超时")
            return {
                "success": False,
                "error": "AI请求超时，请稍后重试"
            }
        except requests.exceptions.HTTPError as e:
            # HTTPError 通常在 raise_for_status() 后触发，response 应该存在
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            error_detail = e.response.text if hasattr(e, 'response') and hasattr(e.response, 'text') else str(e)
            logger.error(f"[AI] API请求失败: {e}, 状态码: {status_code}")
            return {
                "success": False,
                "error": f"AI请求失败: {error_detail}",
                "status_code": status_code
            }
        except requests.exceptions.RequestException as e:
            # 处理其他请求异常（连接错误、DNS错误等）
            logger.error(f"[AI] 网络请求异常: {e}")
            return {
                "success": False,
                "error": f"网络请求失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"[AI] 未知错误: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"AI服务异常: {str(e)}"
            }
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        生成文本（简化接口）
        
        Args:
            prompt: 用户提示词
            max_tokens: 最大token数
            temperature: 温度参数
            system_prompt: 系统提示词
            
        Returns:
            生成的文本内容
            
        Raises:
            ValueError: 当API调用失败时
        """
        result = self._call_api(prompt, max_tokens, temperature, system_prompt)
        
        if result["success"]:
            return result["content"]
        else:
            error_msg = result.get("error", "未知错误")
            raise ValueError(f"AI生成失败: {error_msg}")


# 全局AI服务实例
ai_service = AIService()


# 便捷函数
def generate_text(
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None
) -> str:
    """
    生成文本的便捷函数
    
    使用示例:
        content = generate_text("你好")
    """
    return ai_service.generate_text(prompt, max_tokens, temperature, system_prompt)


def call_ai_api(
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    调用AI API的便捷函数（返回完整结果）
    
    使用示例:
        result = call_ai_api("你好")
        if result["success"]:
            print(result["content"])
    """
    return ai_service._call_api(prompt, max_tokens, temperature, system_prompt)
