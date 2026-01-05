"""LLM 模型适配器"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from langchain.llms.base import BaseLLM
from langchain_community.llms import Tongyi
from config.settings import DASHSCOPE_API_KEY, MODEL_TYPE, MODEL_NAME, LLM_CONFIG


class BaseLLMAdapter(ABC):
    """LLM 适配器基类"""
    
    @abstractmethod
    def get_llm(self) -> BaseLLM:
        """获取 LLM 实例"""
        pass


class DashScopeAdapter(BaseLLMAdapter):
    """阿里云 DashScope API 适配器"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model_name = model_name or MODEL_NAME
    
    def get_llm(self) -> BaseLLM:
        """获取 Tongyi LLM 实例"""
        return Tongyi(
            dashscope_api_key=self.api_key,
            model_name=self.model_name,
            temperature=LLM_CONFIG['temperature'],
            max_tokens=LLM_CONFIG['max_tokens']
        )


class LocalLLMAdapter(BaseLLMAdapter):
    """本地模型适配器（预留接口）"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
    
    def get_llm(self) -> BaseLLM:
        """获取本地 LLM 实例"""
        # TODO: 实现本地模型加载
        # 目前回退到 API 模式
        return DashScopeAdapter().get_llm()


class LLMFactory:
    """LLM 工厂类"""
    
    @staticmethod
    def create_llm(model_type: Optional[str] = None) -> BaseLLM:
        """创建 LLM 实例"""
        model_type = model_type or MODEL_TYPE
        
        if model_type == 'local':
            adapter = LocalLLMAdapter()
        else:
            adapter = DashScopeAdapter()
        
        return adapter.get_llm()

