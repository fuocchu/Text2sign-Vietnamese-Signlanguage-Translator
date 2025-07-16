# Vietnamese Sign Language Translator 🤟  
  
Ứng dụng web chuyển đổi văn bản tiếng Việt thành video ngôn ngữ ký hiệu Việt Nam (VSL) sử dụng AI và computer vision.  
  
## Tính năng chính  
  
- **Chuyển đổi văn bản**: Nhập văn bản tiếng Việt và nhận video ngôn ngữ ký hiệu  
- **Xử lý bất đồng bộ**: Hệ thống xử lý background với status tracking  
- **Giao diện thân thiện**: Web interface đơn giản, dễ sử dụng  
- **Hỗ trợ tên riêng**: Tự động fingerspelling cho tên người và từ viết tắt  
  
## Kiến trúc hệ thống  
  
Hệ thống hoạt động theo pipeline 3 giai đoạn:  
  
1. **Text-to-Gloss**: Chuyển văn bản thành gloss sequence bằng Google Gemini API  
2. **Gloss-to-Pose**: Tra cứu pose data từ Vietnamese lexicon   
3. **Pose-to-Video**: Render pose thành video MP4 với FFmpeg  
  
## Cài đặt  
  
### Yêu cầu hệ thống  
- Python 3.8+  
- FFmpeg  
- Google Gemini API key  
  
### Cài đặt dependencies  
```bash  
pip install flask pose-format google-generativeai python-dotenv
