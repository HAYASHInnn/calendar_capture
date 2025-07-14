from flask import Flask, request, render_template, redirect, url_for, session
import os
import uuid
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import Flow

# Google Calendar API関連の設定
CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)
# アップロードディレクトリ設定
app.config["UPLOAD_FOLDER"] = "static/uploads"

# セッションを安全に使うための「秘密鍵」を設定
SECRET_KEY = os.environ.get("SECRET_KEY")
app.secret_key = SECRET_KEY

# ディレクトリ作成
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Gemini API設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def analyze_schedule_image(image_path):
    """画像から日程情報を解析"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    image = Image.open(image_path)

    today = datetime.now()
    today = today.astimezone(timezone(timedelta(hours=9)))
    today_str = today.strftime("%Y年%m月%d日")

    prompt = f"""
    この画像から日程・スケジュール情報を抽出してください。
    今日の日付は{today_str}です。

    以下の形式で回答してください：

    日付: YYYY-MM-DD
    時間: HH:MM-HH:MM
    イベント名: [イベント名]
    場所: [場所名]（記載があれば）

    注意事項：
    - 複数のイベントがある場合は、それぞれ分けて記載してください
    """

    response = model.generate_content([prompt, image], stream=False)
    return response.text


@app.route("/", methods=["GET", "POST"])
def index():
    # セッションに 'credentials' があればログイン済み
    is_logged_in = 'credentials' in session

    if not is_logged_in:
        # ログインしていなければ、ログインを促すページを表示
        return render_template("index.html", is_logged_in=False)

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
                return render_template(
                    "result.html",
                    result=result,
                    image_url=f"/static/uploads/{filename}",
                )
            except Exception as e:
                return render_template(
                    "index.html", error="画像解析に失敗しました: " + str(e)
                )
            finally:
                # 画像ファイル削除
                if os.path.exists(filepath):
                    os.remove(filepath)

        return render_template("index.html")

    # GETリクエストの場合 (ログイン済みで、ただトップページを表示するとき)
    return render_template("index.html", is_logged_in=True)


@app.route("/login", methods=["GET"])
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    # 認証URLとstateを取得
    # ✍️ ランダムな文字列である合言葉 (state）を生成してセッションに保存
    authorization_url, state = flow.authorization_url()
    session["state"] = state

    # ユーザーをGoogleの認証ページへリダイレクト
    # ✍️ ここで、合言葉(state)が埋め込まれた認証URLにユーザーを飛ばす（CSRF対策）
    return redirect(authorization_url)

# セッションが保存できる辞書形式に変換する関数
def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

@app.route("/oauth2callback", methods=["GET"])
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session["state"],
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    # 認証コードをアクセストークンに交換
    flow.fetch_token(authorization_response=request.url)

    # 認証情報をセッションに保存
    credentials = flow.credentials
    session["credentials"] = credentials_to_dict(credentials)

    return redirect(url_for("index"))

@app.route('/logout')
def logout():
    # セッションからcredentialsを削除
    session.pop('credentials', None)
    # トップページにリダイレクト
    return redirect(url_for('index'))


if __name__ == "__main__":
    # 開発環境でHTTPでのOAuth認証を許可するための設定
    # ❗ 本番環境ではこの行は削除し、必ずHTTPSを使用する！！！
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, host="0.0.0.0", port=3000)
