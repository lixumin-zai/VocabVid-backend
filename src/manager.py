# -*- coding: utf-8 -*-
# @Time    :   2025/04/07 13:06:58
# @Author  :   lixumin1030@gmail.com
# @FileName:   manage.py


import os
from src.server import GeminiGenerator

class VocabVidManager:
    def __init__(self):
        self.gemini_generator = GeminiGenerator()
        self.db = None
    
    def get_example_senctence(self, words):
        return self.gemini_generator.get_example_senctence(" ".join(words))

