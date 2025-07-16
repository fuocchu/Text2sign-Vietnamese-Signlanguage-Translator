# # spoken_to_signed/gloss_to_pose/lookup/vietnamese_lookup.py

# class VietnamesePoseLookup(CSVPoseLookup):
#     def __init__(self):
#         lexicon_dir = Path(__file__).parent.parent.parent / "assets" / "vietnamese_lexicon"
#         super().__init__(directory=str(lexicon_dir))

#     def lookup(self, word: str, gloss: str, spoken_language: str, signed_language: str) -> Pose:
#         # Lookup pose file từ index
#         if word in self.words_index[spoken_language][signed_language]:
#             rows = self.words_index[spoken_language][signed_language][word]
#             return self.get_pose(self.get_best_row(rows, word))
            
#         # Tìm từ gần nghĩa nhất nếu không có từ chính xác
#         closest_word = find_closest_word(word, self.words_index[spoken_language][signed_language].keys())
#         if closest_word:
#             rows = self.words_index[spoken_language][signed_language][closest_word] 
#             return self.get_pose(self.get_best_row(rows, closest_word))
            
#         raise FileNotFoundError(f"No pose found for {word}")
from pathlib import Path
from .lookup import CSVPoseLookup

class VietnamesePoseLookup(CSVPoseLookup):
    def __init__(self):
        lexicon_dir = Path(__file__).parent.parent.parent / "assets" / "vietnamese_lexicon"
        super().__init__(directory=str(lexicon_dir))

    def lookup(self, text: str, gloss: str, spoken_language: str, signed_language: str):
        
        if text in self.words_index[spoken_language][signed_language]:
            rows = self.words_index[spoken_language][signed_language][text]
            return self.get_pose(self.get_best_row(rows, text))
        
        raise FileNotFoundError(f"No pose found for {text}")