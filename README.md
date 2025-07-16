# Vietnamese Sign Language Translator 🤟  
  
Ứng dụng chuyển đổi văn bản tiếng Việt thành video ngôn ngữ ký hiệu Việt Nam (VSL)  

https://github.com/user-attachments/assets/151a83ba-34c4-40cd-9188-9d5384dcd802

## Kiến trúc hệ thống  
<img width="4042" height="1803" alt="main_pipline" src="https://github.com/user-attachments/assets/f4627e9f-fd7d-4e91-bdac-911a049b2b85" />
Hệ thống hoạt động theo pipeline 3 giai đoạn:  
  
1. **Text-to-Gloss**: Chuyển văn bản thành gloss sequence bằng Google Gemini API  
2. **Gloss-to-Pose**: Tra cứu pose data từ Vietnamese lexicon  
3. **Pose-to-Video**: Render pose thành video MP4  
## Cài đặt  
### Yêu cầu hệ thống  
- Python 3.8+  
- FFmpeg  
- Google Gemini API key  
  
### Cài đặt dependencies  
```bash  
pip install -r requirements.txt
