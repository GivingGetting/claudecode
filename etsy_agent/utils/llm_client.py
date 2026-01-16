"""
LLM Client - 统一的AI模型调用接口
支持 Anthropic Claude 和 OpenAI GPT
"""

import os
import json
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMClient:
    """统一的LLM客户端，支持多种AI提供商"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.provider = provider or os.getenv("AI_PROVIDER", "anthropic")
        self.model = model or os.getenv("AI_MODEL", "claude-sonnet-4-20250514")
        self.api_key = api_key

        if self.provider == "anthropic":
            self._init_anthropic()
        elif self.provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"不支持的AI提供商: {self.provider}")

    def _init_anthropic(self):
        """初始化Anthropic客户端"""
        try:
            import anthropic

            api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("请安装 anthropic: pip install anthropic")

    def _init_openai(self):
        """初始化OpenAI客户端"""
        try:
            import openai

            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("请设置 OPENAI_API_KEY 环境变量")
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("请安装 openai: pip install openai")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        发送消息并获取回复

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数 (0-1)
            max_tokens: 最大输出token数

        Returns:
            AI的回复文本
        """
        if self.provider == "anthropic":
            return self._chat_anthropic(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._chat_openai(prompt, system_prompt, temperature, max_tokens)

    def _chat_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Anthropic Claude API调用"""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        # Claude doesn't use temperature in the same way, using top_p instead
        if temperature < 1.0:
            kwargs["temperature"] = temperature

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _chat_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """OpenAI GPT API调用"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """
        发送消息并获取JSON格式的回复

        Args:
            prompt: 用户提示（应该要求返回JSON）
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大输出token数

        Returns:
            解析后的JSON字典
        """
        json_system = (system_prompt or "") + "\n\n请只返回有效的JSON格式，不要包含任何其他文本或markdown代码块标记。"

        response = self.chat(prompt, json_system, temperature, max_tokens)

        # 清理响应文本
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # 尝试提取JSON部分
            import re

            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # 尝试数组
            array_match = re.search(r"\[[\s\S]*\]", response)
            if array_match:
                try:
                    return json.loads(array_match.group())
                except json.JSONDecodeError:
                    pass

            raise ValueError(f"无法解析JSON响应: {e}\n原始响应: {response[:500]}")
