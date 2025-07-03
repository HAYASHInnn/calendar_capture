from flask import Flask, request, render_template, redirect, url_for
import os
import uuid
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# ディレクトリ作成
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Gemini API設定
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def analyze_schedule_image(image_path):
    """画像から日程情報を解析"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    image = Image.open(image_path)
    
    prompt = """
    この画像から日程・スケジュール情報を抽出してください。
    以下の形式で回答してください：
    
    日付: YYYY-MM-DD
    時間: HH:MM-HH:MM
    イベント名: [イベント名]
    場所: [場所名]（記載があれば）
    
    複数のイベントがある場合は、それぞれ分けて記載してください。
    """
    
    response = model.generate_content([prompt, image], stream=False)
    return response.text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")
        if file and file.filename:
            # ファイル保存
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            
            try:
                # 画像解析
                result = analyze_schedule_image(filepath)
                return render_template("result.html", 
                                     result=result, 
                                     image_url=f"/static/uploads/{filename}")
            except Exception as e:
                return render_template("index.html", 
                                     error="画像解析に失敗しました: " + str(e))
            finally:
                # 画像ファイル削除
                if os.path.exists(filepath):
                    os.remove(filepath)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
