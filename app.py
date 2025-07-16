from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import uuid
from threading import Thread
from pose_format import Pose
from pose_format.pose_visualizer import PoseVisualizer

import sys
sys.path.append('.')
from spoken_to_signed.bin import _text_to_gloss, _gloss_to_pose

app = Flask(__name__)

os.makedirs('static/videos', exist_ok=True)
os.makedirs('static/poses', exist_ok=True)

class VideoProcessor:
    def __init__(self):
        self.processing_status = {}
    
    def text_to_pose_direct(self, text, task_id):
        """Gọi trực tiếp function thay vì subprocess"""
        try:
            self.processing_status[task_id] = {"status": "processing", "step": "Đang chuyển text thành pose..."}
            
            
            sentences = _text_to_gloss(
                text=text,
                language="vi",
                glosser="gpt",
                signed_language="vsl"
            )
            
            if not sentences:
                self.processing_status[task_id] = {"status": "error", "message": "Không tạo được gloss từ text"}
                return None
            
            self.processing_status[task_id]["step"] = "Đang tạo pose từ gloss..."
            
            pose = _gloss_to_pose(
                sentences=sentences,
                lexicon="assets/vietnamese_lexicon",
                spoken_language="vi",
                signed_language="vsl"
            )
            
            if pose is None:
                self.processing_status[task_id] = {"status": "error", "message": "Không tạo được pose"}
                return None
            
           
            pose_file = f"static/poses/{task_id}.pose"
            with open(pose_file, "wb") as f:
                pose.write(f)
                
            return pose_file
            
        except Exception as e:
            self.processing_status[task_id] = {"status": "error", "message": f"Lỗi: {str(e)}"}
            return None
    
    def pose_to_video(self, pose_file, task_id):
        """Chuyển pose thành video H.264"""
        try:
            print(f"🔍 Starting pose_to_video: {pose_file}")
            self.processing_status[task_id]["step"] = "Đang tạo video từ pose..."

            if not os.path.exists(pose_file):
                print(f"❌ Pose file not found: {pose_file}")
                self.processing_status[task_id] = {"status": "error", "message": "Pose file không tồn tại"}
                return None

            with open(pose_file, "rb") as f:
                pose = Pose.read(f.read())

            v = PoseVisualizer(pose)

            raw_video = f"static/videos/{task_id}_raw.mp4"
            final_video = f"static/videos/{task_id}.mp4"

            
            v.save_video(raw_video, v.draw())

            
            import subprocess
            ffmpeg_cmd = [
                "/usr/bin/ffmpeg", "-y",
                "-i", raw_video,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "25",
                final_video
            ]
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ FFmpeg conversion successful")
                os.remove(raw_video)
            else:
                print("❌ FFmpeg error:")
                print(result.stderr)
                self.processing_status[task_id] = {"status": "error", "message": "FFmpeg lỗi: " + result.stderr}
                return None

            
            result = subprocess.run(
                ['/usr/bin/ffprobe', '-v', 'quiet', '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', final_video],
                capture_output=True, text=True
            )
            codec = result.stdout.strip()
            print(f"✅ Final video codec: {codec}")

            self.processing_status[task_id] = {"status": "completed", "video": final_video}
            return final_video

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.processing_status[task_id] = {"status": "error", "message": f"Lỗi tạo video: {str(e)}"}
            return None


    def process_text(self, text, task_id):
        """Xử lý toàn bộ: text -> pose -> video"""
        
        pose_file = self.text_to_pose_direct(text, task_id)
        if not pose_file:
            return
        
        
        self.pose_to_video(pose_file, task_id)

processor = VideoProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_text():
    text = request.json.get('text', '')
    
    if not text.strip():
        return jsonify({"error": "Vui lòng nhập văn bản"}), 400
    
    task_id = str(uuid.uuid4())
    
    thread = Thread(target=processor.process_text, args=(text, task_id))
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/status/<task_id>')
def get_status(task_id):
    status = processor.processing_status.get(task_id, {"status": "not_found"})
    return jsonify(status)

# Route cũ cho video
@app.route('/video/<filename>')
def serve_video(filename):
    try:
        video_path = f'static/videos/{filename}'
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
        else:
            return "Video not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        return f"Static file error: {str(e)}", 500


@app.route('/static/videos/<filename>')
def serve_video_static(filename):
    try:
        return send_from_directory('static/videos', filename, mimetype='video/mp4')
    except Exception as e:
        return f"Video error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)