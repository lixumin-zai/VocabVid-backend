# -*- coding: utf-8 -*-
# @Time    :   2025/04/06 23:24:01
# @Author  :   lixumin1030@gmail.com
# @FileName:   gemini.py


import base64
import os
from google import genai
from google.genai import types


class GeminiGenerator:
    def __init__(self, api_key=None):
        """
        初始化 GeminiGenerator 类
        
        Args:
            api_key: Google API 密钥，如果为 None，则从环境变量获取
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"
        
    def _create_system_instruction(self):
        """创建系统指令"""
        return [
            types.Part.from_text(text="""# Role
你是一个雅思英语老师

# Task
给定多个中英文单词，帮我组个雅思难度的长句子, 并按照格式输出

# Ouput Format
**句子**
Each component element plays a critical role in the success of the project.
**中文翻译**
每个组件元素在项目的成功中都起着关键作用.
**结构解析**
|原文分词|译文完全对应词|具体解释|
|---|---|---|
|Each|每个|表示"每一个"，修饰"component element"，指代所有构成要素中的任意一个|
|component|-|修饰"element"，表示构成整体的部分，与"要素"共同表达"构成要素"|
|element|元素|指整体中的某个部分，这里是项目成功的关键组成部分|
|plays|起着|表示承担或扮演某种角色，强调其作用，在这里意为"起到……作用"|
|a|-|不定冠词，用于修饰"critical role"，表示"一个关键作用"|
|critical|关键|修饰"role"，表明这个作用是至关重要的|
|role|作用|指某事物在特定情境下所发挥的功能，这里是"关键作用"|
|in|在|介词，表示范围或领域，说明作用发生的范围|
|the|-|定冠词，特指"success"即项目的成功|
|success|成功|指项目达成预期目标的结果|
|of|-|连接"success"和"project"，表示所属关系，即项目的成功|
|the|-|定冠词，特指"project"|
|project|项目|指具体的工作或计划，这里是讨论的对象|
""")
        ]
    
    def get_example_senctence(self, prompt, stream=True):
        """
        生成内容
        
        Args:
            prompt: 用户输入的提示词
            stream: 是否使用流式输出，默认为 True
            
        Returns:
            如果 stream=False，返回完整响应；否则打印流式输出
        """
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction=self._create_system_instruction(),
        )
        
        if stream:
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                yield chunk.text
        else:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            return response.text


if __name__ == "__main__":
    generator = GeminiGenerator()
    generator.generate("爱情 知识 无知 提高 存在")
