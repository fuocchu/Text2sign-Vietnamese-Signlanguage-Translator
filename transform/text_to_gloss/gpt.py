import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv

from spoken_to_signed.text_to_gloss.types import Gloss, GlossItem


VOCAB_LIST = ["xin chào", "tạm biệt", "chó cắn", "anh ruột", "bạn yêu tôi", "chết", "chị", "cha", "chạy", "ăn uống", "ai", "bạn", "ai bảo", "xin lỗi", "yếu", "yêu cầu", "yêu mến", "xảy ra", "xe máy", "trường", "vô duyên", "tôi yêu bạn", "yên tâm", "thầy giáo", "việt nam", "tính toán", "là gì", "ngôn ngữ kí hiệu", "tên là gì", "trung quốc", "tên", "hối hận", "nhưng", "tẩy chay", "ô trống", "mẹ", "ở ngoài", "nấu nướng", "sức khỏe", "suy nghĩ", "nhầm lẫn", "nghiên cứu", "ghen", "kịp thời", "học tập", "em trai", "không có", "đồ ăn", "hằng ngày", "hoan hô", "khoa học", "giết", "có không", "em gái", "đúng không", "đi học", "chúng tôi", "dạy", "tôi", "7", "1", "3", "2", "4", "9", "8", "6", "5", "10", "dấu sắc", "dấu ngã", "dấu huyền", "dấu nặng", "dấu hỏi", "y", "ư", "v", "ă", "đ", "â", "ơ", "ê", "t", "ô", "x", "r", "e", "u", "o", "q", "h", "l", "m", "p", "s", "b", "n", "c", "g", "d", "i", "a", "k", "năng lực", "ôn luyện", "lớp học", "đánh giá", "đi dạo"]

SYSTEM_PROMPT = f"""
Bạn là trợ lý chuyển đổi văn bản tiếng Việt thành gloss cho ngôn ngữ ký hiệu Việt Nam.

NHIỆM VỤ:
- Tìm các cụm từ/từ trong câu đầu vào có trong danh sách từ vựng
- Chỉ trả về những từ/cụm từ có trong vocab list
- Không tách nhỏ các cụm từ thành từng từ đơn lẻ
- Giữ nguyên format "từ gốc" (không cần chuyển đổi gì)
- XỬ LÝ TÊN RIÊNG VÀ TỪ VIẾT TẮT: Tách thành từng chữ cái riêng biệt

DANH SÁCH TỪ VỰNG:
{', '.join(VOCAB_LIST)}

QUY TẮC ĐẶC BIỆT:
1. TÊN RIÊNG (tên người): Tách thành từng chữ cái + dấu thanh riêng
   - Ví dụ: "Thành" → "t", "h", "a", "n", "h", "dấu huyền"
   - Ví dụ: "Hiển" → "h", "i", "ê", "n", "dấu hỏi"]
   - Ví dụ: "Hà" → "h", "a", "dấu huyền"

2. TỪ VIẾT TẮT (chữ in hoa): Tách thành từng chữ cái
   - Ví dụ: "UIT" → "u", "i", "t"
   - Ví dụ: "HCMUS" → "h", "c", "m", "u", "s"

VÍ DỤ THÔNG THƯỜNG:
Input: "Thầy tôi đang ôn đánh giá năng lực cho lớp tôi"
Output: ["thầy giáo", "tôi", "ôn luyện", "đánh giá", "năng lực", "lớp học", "tôi"]

VÍ DỤ VỚI TÊN RIÊNG:
Input: "Tôi tên là Thành"
Output: ["tôi", "tên", "t", "h", "a", "n", "h", "dấu huyền"

VÍ DỤ VỚI TỪ VIẾT TẮT:
Input: "Tôi học ở UIT"
Output: ["tôi", "học", "u", "i", "t"]

Input: "bạn Hiển từ HCMUS"
Output: "bạn", "h", "i", "ê", "n", "dấu hỏi", "h", "c", "m", "u", "s"

ĐỊNH DẠNG ĐẦU RA:
CHỈ trả về JSON array các cụm từ có trong vocab hoặc array các chữ cái cho tên riêng/từ viết tắt, không có markdown:
""".strip()

@lru_cache(maxsize=1)
def get_gemini_client():
    api_key = "YOUR_API_KEY"
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def sentence_to_glosses(sentence: str) -> GlossItem:
 
    yield sentence.strip(), sentence.strip()

def text_to_gloss(text: str, language: str, signed_language: str, **kwargs) -> List[Gloss]:
    try:
        full_prompt = f"""
{SYSTEM_PROMPT}

Tìm các từ/cụm từ trong câu sau có trong vocab list:
"{text}"

Chỉ trả về JSON array:
"""

        model = get_gemini_client()
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                max_output_tokens=200,
            )
        )

        prediction = response.text.strip()
        print(f"Gemini response: {prediction}")
        
        # Clean up markdown
        prediction = prediction.replace('```json', '').replace('```', '').strip()
        
        try:
            sentences = json.loads(prediction)
            if isinstance(sentences, str):
                sentences = [sentences]
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {prediction}")
            
            sentences = []
            for vocab_word in VOCAB_LIST:
                if vocab_word.lower() in text.lower():
                    sentences.append(vocab_word)
        
        print(f"Found vocab words: {sentences}")
        
        
        result = [list(sentence_to_glosses(sentence)) for sentence in sentences]
        print(f"Generated glosses: {result}")
        return result
        
    except Exception as e:
        print(f"Error in text_to_gloss: {str(e)}")
        return []

if __name__ == '__main__':
    text = "Thầy tôi đang ôn đánh giá năng lực cho lớp tôi"
    language = "vi"
    signed_language = "vsl"
    result = text_to_gloss(text, language, signed_language)
    print(f"Final result: {result}")