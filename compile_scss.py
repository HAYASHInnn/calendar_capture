import sass
import os
import sys


def compile_scss():
    """SCSSファイルをCSSにコンパイル"""
    try:
        # 入力と出力のパス
        scss_path = "static/css/scss/main.scss"
        css_path = "static/css/style.css"

        # SCSSファイルの存在確認
        if not os.path.exists(scss_path):
            print(f"❌ SCSSファイルが見つかりません: {scss_path}")
            return False

        # コンパイル実行
        print("🔄 SCSSをコンパイル中...")
        compiled_css = sass.compile(
            filename=scss_path,
            output_style="compressed",  # 圧縮
            source_map_filename=css_path + ".map",
        )

        # CSSファイルに書き込み (修正箇所)
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(compiled_css[0])  # タプルの最初の要素(CSS文字列)を書き込む

        print(f"✅ コンパイル完了: {css_path}")
        return True

    except Exception as e:
        print(compiled_css)  # デバッグ用に出力
        print(f"❌ コンパイルエラー: {str(e)}")
        return False


def watch_scss():
    """SCSSファイルの変更を監視してコンパイル"""
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class SCSSHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".scss"):
                print(f"📝 {event.src_path} が変更されました")
                compile_scss()

    # 監視開始
    event_handler = SCSSHandler()
    observer = Observer()
    observer.schedule(event_handler, "static/css/scss", recursive=True)
    observer.start()

    print("👀 SCSSファイルを監視中... (Ctrl+C で停止)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 監視を停止しました")

    observer.join()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # 監視モード
        try:
            import watchdog
        except ImportError:
            print("📦 watchdogをインストールしています...")
            os.system("pip install watchdog")
            import watchdog

        compile_scss()  # 初回コンパイル
        watch_scss()
    else:
        # 一回だけコンパイル
        compile_scss()
