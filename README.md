![デモ動画](https://github.com/HAYASHInnn/calendar_capture/blob/main/docs/images/demo.gif)
_このデモ動画は、アプリの主要な機能（ログイン → 画像アップロード → AI による解析 → カレンダー登録）を示しています。_

# 📅 Calendar Capture

  <a href="https://www.python.org/" target="_blank" rel="noreferrer">
    <img src="https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://flask.palletsprojects.com/" target="_blank" rel="noreferrer">
    <img src="https://img.shields.io/badge/Flask-2.x-000000.svg?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  </a>
  <a href="LICENSE" target="_blank" rel="noreferrer">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT">
  </a>

## はじめに

**Calendar Capture**は、画像に含まれるスケジュール情報を AI が自動で読み取り、Google カレンダーに登録できる Web アプリケーションです。メモの写真やチャットのスクリーンショットを**アップロード**することで、Google カレンダーへの登録を簡略化します。

- **きっかけ**<br>
  とある友人が<br>
  「LINE で予定を決めた後に、カレンダーに登録するのがめんどくさい…🙂」<br>
  「スクショで登録できるようにしてほしい…🙂」<br>
  と嘆いていたことから開発してみました。

- **技術的動機**<br>
  Python で AI を使った Web アプリケーションの開発に挑戦し、実用的なプロダクトを通じて技術を習得したいと思い開発しました。

## 特徴

- **AI による画像解析**: Google の AI モデル「Gemini」が、画像内の文字を認識し、日付、時間、イベント名、場所を抽出します。
- **自然言語にも対応**:「明日」「来週の金曜日」といった曖昧な表現も、AIが今日の日付を基準に解釈してくれます。
- **Google カレンダー連携**: 抽出されたスケジュール情報を、ワンクリックで自分の Google カレンダーに登録できます。
- **セキュアな認証**: Google OAuth 2.0 を利用しており、安全にアカウント連携ができます。
- **プライバシー配慮**: アップロードされた画像は、解析後にサーバーからすぐに削除されます。

## 使用技術

- **バックエンド**<br>
  <a href="https://www.python.org/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://flask.palletsprojects.com/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  </a>

- **AI モデル**<br>
  <a href="https://ai.google.dev/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google-gemini&logoColor=white" alt="Google Gemini">
  </a>

- **API 連携 / 認証**<br>
  <a href="https://developers.google.com/calendar" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/Google%20Calendar%20API-4285F4?style=for-the-badge&logo=google-calendar&logoColor=white" alt="Google Calendar API">
  </a>
  <a href="https://developers.google.com/identity/protocols/oauth2" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/OAuth%202.0-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google OAuth 2.0">
  </a>

- **主要ライブラリ**<br>
  <a href="https://pypi.org/project/google-generativeai/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/google--generativeai-4A90E2?style=for-the-badge" alt="google-generativeai">
  </a>
  <a href="https://pypi.org/project/google-api-python-client/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/google--api--python--client-34A853?style=for-the-badge" alt="google-api-python-client">
  </a>
  <a href="https://pypi.org/project/google-auth-oauthlib/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/google--auth--oauthlib-EA4335?style=for-the-badge" alt="google-auth-oauthlib">
  </a>
  <a href="https://pypi.org/project/Pillow/" target="_blank" rel="noreferrer">
  <img src="https://img.shields.io/badge/Pillow-306998?style=for-the-badge" alt="Pillow">
  </a>

## システム構図
![システム構図](https://github.com/HAYASHInnn/calendar_capture/blob/main/docs/images/system-diagram.png)

## ローカル環境での実行方法

ローカル環境で実行するには、以下の手順に従ってください。

### 1. 前提条件

- Python 3.9 以上
- Git
- Google Cloud Platform (GCP) アカウント

### 2. API のセットアップ

本アプリケーションを実行するには、GCP で以下の API を有効にし、認証情報を取得する必要があります。

1.  **Google Gemini API の有効化と API キーの取得**:

    - GCP プロジェクトで「Vertex AI API」または「Generative Language API」を有効にします。
    - [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセスし、API キーを取得します。

2.  **Google Calendar API の有効化と OAuth 2.0 クライアント ID の取得**:

    - GCP プロジェクトで「Google Calendar API」を有効にします。
    - 「API とサービス」 > 「認証情報」から「OAuth クライアント ID」を作成します。
      - アプリケーションの種類: **ウェブアプリケーション**
    - 作成後、**JSON ファイルをダウンロード**し、プロジェクトのルートディレクトリに `credentials.json` という名前で保存します。

3.  **承認済みリダイレクト URI とテストユーザーの設定**:
    - 作成した OAuth クライアント ID の設定画面で、「承認済みのリダイレクト URI」に以下を追加します。
      - `http://localhost:3000/oauth2callback`
    - 「OAuth 同意画面」の設定に戻り、公開ステータスが**「テスト」**になっていることを確認し、「テストユーザー」にご自身の Google アカウント（`@gmail.com`）を追加します。

### 3. 環境構築

#### Step 1: リポジトリのクローン

```bash
git clone https://github.com/HAYASHInnn/calendar_capture.git
cd calendar_capture
```

#### Step 2: 環境変数の設定

プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の内容を記述します。

```.env
# 取得したGemini APIキー
GEMINI_API_KEY="ここにあなたのGemini APIキーを貼り付け"

# Flaskのセッション用秘密鍵（任意のランダムな文字列でOK）
SECRET_KEY="your-super-secret-and-random-key"
```

#### Step 3: 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

_(注: このリポジトリには `requirements.txt` が含まれています。)_

### 4. アプリケーションの実行

```bash
python app.py
```

実行後、`http://localhost:3000` にブラウザでアクセスしてください。

## parse_gemini_result メソッドの入出力イメージ

- **Gemini から返ってくる入力値**<br>

```python
日付:2024-10-26
時間:14:00-16:00
イベント名:Python勉強会
場所:会議室A
---
日付:2024-10-27
時間:12:00-13:00
イベント名:チームランチ
場所:なし
```

- **プログラムが扱うための出力値**<br>

```python
[
  { # 1つ目のイベント
    '日付': '2024-10-26',
    '時間': '14:00-16:00',
    'イベント名': 'Python勉強会',
    '場所': '会議室A',
    '開始時間': '14:00',
    '終了時間': '16:00'
  },
  { # 2つ目のイベント
    '日付': '2024-10-27',
    '時間': '12:00-13:00',
    'イベント名': 'チームランチ',
    '場所': 'なし',
    '開始時間': '12:00',
    '終了時間': '13:00'
  }
]
```

## 今後 実装予定の機能

- テキスト入力からの直接解析
- イベントカラーの選択機能
- 複数の予定の一括登録
- LINE Bot化

## おわりに

感想・コメント等ございましたら、お気軽にXアカウントまでご連絡いただけますと幸いです。

<a href="https://x.com/makaJava368748" target="_blank" rel="noreferrer" style="display: inline-flex; align-items: center; text-decoration: none; color: inherit;">
  <img src="https://github.com/user-attachments/assets/5df37342-c70e-4e0d-b9cd-21e390c9069c" width="20px" alt="X(Twitter) Icon" style="margin-right: 8px;">
  <span>@makaJava368748</span>
</a>
