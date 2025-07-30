/**
 * 結果画面の機能
 * イベント削除、追加機能を管理
 */

class ResultManager {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
  }

  /**
   * イベントリスナーの設定
   */
  setupEventListeners() {
    // 削除ボタンのイベントリスナー設定
    document.querySelectorAll(".btn-outline-danger").forEach((button) => {
      button.addEventListener("click", () => this.removeEvent(button));
    });

    // 一括追加ボタンのイベントリスナー設定
    const addAllButton = document.querySelector(
      'button[onclick="addAllEvents()"]'
    );
    if (addAllButton) {
      addAllButton.removeAttribute("onclick");
      addAllButton.addEventListener("click", () => this.addAllEvents());
    }
  }

  /**
   * イベントの削除
   * @param {HTMLElement} button - 削除ボタン要素
   */
  removeEvent(button) {
    if (confirm("このイベントを削除しますか？")) {
      const card = button.closest(".card");
      if (card) {
        card.remove();
        CommonUtils.showAlert("イベントを削除しました。", "info");
      }
    }
  }

  /**
   * 全てのイベントを一括追加
   */
  async addAllEvents() {
    const forms = document.querySelectorAll(".card form");

    if (forms.length === 0) {
      CommonUtils.showAlert("追加するイベントがありません", "warning");
      return;
    }

    if (
      !confirm(
        `${forms.length}個のイベントを全てGoogleカレンダーに追加しますか？`
      )
    ) {
      return;
    }

    // ローディング状態を設定
    CommonUtils.setLoading(true);

    try {
      let completed = 0;
      const promises = Array.from(forms).map((form) => {
        const formData = new FormData(form);

        return fetch(form.action, {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then((data) => {
            completed++;
            return data;
          });
      });

      // 全てのリクエストが完了するまで待機
      await Promise.all(promises);

      CommonUtils.showAlert("全てのイベントが追加されました！", "success");

      // 少し待ってからリダイレクト
      setTimeout(() => {
        window.location.href = this.getIndexUrl();
      }, 2000);
    } catch (error) {
      console.error("Error:", error);
      CommonUtils.showAlert(
        "エラーが発生しました。再度お試しください。",
        "danger"
      );
    } finally {
      CommonUtils.setLoading(false);
    }
  }

  /**
   * 個別のイベント追加
   * @param {HTMLFormElement} form - 送信するフォーム
   */
  async addSingleEvent(form) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');

    // 送信ボタンのローディング状態を設定
    const originalText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML =
      '<span class="spinner-border spinner-border-sm"></span> 追加中...';

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        CommonUtils.showAlert(
          "イベントがGoogleカレンダーに追加されました！",
          "success"
        );
        // フォームを削除または無効化
        form.closest(".card").style.opacity = "0.5";
        submitButton.innerHTML = "✓ 追加済み";
        submitButton.classList.remove("btn-success");
        submitButton.classList.add("btn-secondary");
      } else {
        throw new Error(data.message || "イベントの追加に失敗しました");
      }
    } catch (error) {
      console.error("Error:", error);
      CommonUtils.showAlert(
        "エラーが発生しました。再度お試しください。",
        "danger"
      );

      // 元の状態に戻す
      submitButton.disabled = false;
      submitButton.innerHTML = originalText;
    }
  }

  /**
   * インデックスページのURLを取得
   * @returns {string} - インデックスページのURL
   */
  getIndexUrl() {
    // Flask url_for の代替として、相対パスを使用
    return "/";
  }
}
