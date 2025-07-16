from flask import Flask, request, render_template, redirect, url_for, session
import os
import uuid
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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

    以下のキーと値のペアで、1行ずつ厳密に出力してください。
    値が存在しない場合は「なし」と出力してください。
    複数のイベントがある場合は、--- (ハイフン3つ) で区切ってください。

    日付:YYYY-MM-DD
    時間:HH:MM-HH:MM
    イベント名:イベントの名称
    場所:場所の名称
    ---
    日付:YYYY-MM-DD
    時間:HH:MM-HH:MM
    イベント名:イベントの名称
    場所:場所の名称
    """

    response = model.generate_content([prompt, image], stream=False)
    return response.text

def parse_gemini_result(result_text):
    events = []
    # --- (ハイフン3つ) で各イベントのテキストに分割
    event_blocks = result_text.strip().split('---')

    for block in event_blocks:
        if not block.strip():
            continue # 空のブロックはスキップ

        event_data = {}
        lines = block.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                event_data[key.strip()] = value.strip()

        # 時間を分割して開始と終了に分ける
        if '時間' in event_data and '-' in event_data['時間']:
            start_time, end_time = event_data['時間'].split('-', 1)
            event_data['開始時間'] = start_time.strip()
            event_data['終了時間'] = end_time.strip()

        events.append(event_data)

    return events

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
                result_text = analyze_schedule_image(filepath)
                events = parse_gemini_result(result_text)
                return render_template(
                    "result.html",
                    events=events,  # ✍️ htmlに渡す変数
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

        return render_template(
            "result.html",
            events=events,  # パースしたリストを渡す
            image_url=f"/static/uploads/{filename}",
        )


    # GETリクエストの場合 (ログイン済みで、ただトップページを表示するとき)
    return render_template("index.html", is_logged_in=True)

@app.route('/create_event', methods=['POST'])
def create_event():
    # Googleカレンダーに登録するので、ログインしているか確認
    if 'credentials' not in session:
        return redirect(url_for('login'))

    # htmlから送信されたデータを取得
    summary = request.form.get('summary')
    date_str = request.form.get('date')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    location = request.form.get('location')

    # セッションからGoogleカレンダーに連携するため、ログイン時の認証情報を読み込む
    creds_dict = session['credentials']
    credentials = Credentials(**creds_dict)

    # Googleカレンダーに連携
    service = build("calendar", "v3", credentials=credentials)

    # APIに渡すため、RFC3339形式のUTC文字列（YYYY-MM-DDTHH:MM:SS）に変換
    start_datetime_for_api = f"{date_str}T{start_time_str}:00"
    end_datetime_for_api = f"{date_str}T{end_time_str}:00"

    # APIに渡すイベントデータ（辞書）を作成
    event_body = {
        'summary': summary,
        'location': location,
        'start': {
            'dateTime': start_datetime_for_api,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_datetime_for_api,
            'timeZone': 'Asia/Tokyo',
        },
    }

    try:
        # 'primary'はメインカレンダーのこと
        created_event = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()

        # イベント登録したら、ユーザーにメッセージとカレンダーへのリンクを見せる
        event_url = created_event.get('htmlLink')
        return f"""
            イベント「{summary}」をカレンダーに登録しました！<br>
            <a href="{event_url}" target="_blank">カレンダーで確認する</a><br><br>
            <a href="{url_for('index')}">トップページに戻る</a>
        """

    except Exception as e:
        # --- デバッグのためのコードを追加 ---
        print("--- エラー発生 ---")
        print(f"エラーの種類: {type(e)}")
        print(f"エラーの詳細: {e}")
        print("-----------------")
        # -----------------------------
        return f"エラーが発生しました: {e}"



@app.route("/login", methods=["GET"])
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    # ✍️ 認証URLとランダムな文字列である合言葉 (state）を生成してセッションに保存
    authorization_url, state = flow.authorization_url(
    # ✍️ リフレッシュトークンを取得し、毎回同意画面を表示させる
        access_type='offline',
        prompt='consent'
    )
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
