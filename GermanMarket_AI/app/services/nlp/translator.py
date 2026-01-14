# -*- coding: utf-8 -*-
"""
德语翻译服务
============
支持德语<->中文/英文翻译
"""

from typing import List, Optional
from dataclasses import dataclass

from transformers import MarianMTModel, MarianTokenizer


@dataclass
class TranslationResult:
    """翻译结果"""
    source: str
    target: str
    source_lang: str
    target_lang: str


class GermanTranslator:
    """德语翻译器"""
    
    def __init__(
        self,
        model_de_zh: str = "Helsinki-NLP/opus-mt-de-zh",
        model_de_en: str = "Helsinki-NLP/opus-mt-de-en"
    ):
        self.model_names = {
            "de-zh": model_de_zh,
            "de-en": model_de_en
        }
        
        # 懒加载
        self._models = {}
        self._tokenizers = {}
    
    def _load_model(self, direction: str):
        """加载指定方向的翻译模型"""
        if direction in self._models:
            return
        
        model_name = self.model_names.get(direction)
        if not model_name:
            raise ValueError(f"不支持的翻译方向: {direction}")
        
        print(f"加载翻译模型: {model_name}")
        self._tokenizers[direction] = MarianTokenizer.from_pretrained(model_name)
        self._models[direction] = MarianMTModel.from_pretrained(model_name)
        print(f"✓ {direction} 模型加载完成")
    
    def translate(
        self,
        text: str,
        target_lang: str = "zh",
        source_lang: str = "de"
    ) -> TranslationResult:
        """
        翻译单条文本
        
        Args:
            text: 德语文本
            target_lang: 目标语言 (zh/en)
            source_lang: 源语言 (默认de)
        """
        direction = f"{source_lang}-{target_lang}"
        self._load_model(direction)
        
        tokenizer = self._tokenizers[direction]
        model = self._models[direction]
        
        # 编码
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # 翻译
        outputs = model.generate(**inputs, max_length=512)
        
        # 解码
        translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return TranslationResult(
            source=text,
            target=translated,
            source_lang=source_lang,
            target_lang=target_lang
        )
    
    def translate_batch(
        self,
        texts: List[str],
        target_lang: str = "zh"
    ) -> List[TranslationResult]:
        """批量翻译"""
        from tqdm import tqdm
        return [
            self.translate(t, target_lang=target_lang) 
            for t in tqdm(texts, desc=f"翻译->{ target_lang}")
        ]
    
    def de_to_zh(self, text: str) -> str:
        """德语转中文（便捷方法）"""
        return self.translate(text, target_lang="zh").target
    
    def de_to_en(self, text: str) -> str:
        """德语转英文（便捷方法）"""
        return self.translate(text, target_lang="en").target

