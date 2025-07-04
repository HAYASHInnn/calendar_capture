/**
 * 共通機能
 * 全ページで使用できるユーティリティ関数
 */

class CommonUtils {
  /**
   * アラート表示
   * @param {string} message - メッセージ
   * @param {string} type - アラートタイプ（success, warning, danger, info）
   */
  static showAlert(message, type = "info") {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

    // mainContentの先頭に挿入
    const mainContent = document.querySelector(".main-content");
    mainContent.insertBefore(alertDiv, mainContent.firstChild);

    // 5秒後に自動削除
    setTimeout(() => {
      if (alertDiv.parentElement) {
        alertDiv.remove();
      }
    }, 5000);
  }

  /**
   * ローディング状態の管理
   * @param {boolean} isLoading - ローディング状態
   * @param {string} targetId - 対象要素のID
   */
  static setLoading(isLoading, targetId = null) {
    const elements = targetId
      ? [document.getElementById(targetId)]
      : document.querySelectorAll(".btn");

    elements.forEach((element) => {
      if (element) {
        element.disabled = isLoading;
        if (isLoading) {
          element.classList.add("loading");
        } else {
          element.classList.remove("loading");
        }
      }
    });
  }

  /**
   * ファイルサイズの検証
   * @param {File} file - 検証するファイル
   * @param {number} maxSize - 最大サイズ（バイト）
   * @returns {boolean} - 検証結果
   */
  static validateFileSize(file, maxSize = 10 * 1024 * 1024) {
    // デフォルト10MB
    if (file.size > maxSize) {
      this.showAlert(
        `ファイルサイズが大きすぎます。${Math.round(
          maxSize / (1024 * 1024)
        )}MB以下のファイルを選択してください。`,
        "warning"
      );
      return false;
    }
    return true;
  }

  /**
   * 画像ファイルの検証
   * @param {File} file - 検証するファイル
   * @returns {boolean} - 検証結果
   */
  static validateImageFile(file) {
    const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      this.showAlert(
        "サポートされていないファイル形式です。JPEG、PNG、GIF、WebPファイルを選択してください。",
        "warning"
      );
      return false;
    }
    return true;
  }

  /**
   * デバウンス関数
   * @param {Function} func - 実行する関数
   * @param {number} delay - 遅延時間（ミリ秒）
   * @returns {Function} - デバウンスされた関数
   */
  static debounce(func, delay) {
    let timeoutId;
    return function (...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * 日付フォーマット
   * @param {Date} date - フォーマットする日付
   * @param {string} format - フォーマット形式
   * @returns {string} - フォーマットされた日付文字列
   */
  static formatDate(date, format = "YYYY-MM-DD") {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return format
      .replace("YYYY", year)
      .replace("MM", month)
      .replace("DD", day)
      .replace("HH", hours)
      .replace("mm", minutes);
  }
}

// グローバルエラーハンドラ
window.addEventListener("error", (e) => {
  console.error("JavaScript Error:", e.error);
  CommonUtils.showAlert(
    "エラーが発生しました。ページを再読み込みしてください。",
    "danger"
  );
});

// 未処理のPromise拒否をキャッチ
window.addEventListener("unhandledrejection", (e) => {
  console.error("Unhandled Promise Rejection:", e.reason);
  CommonUtils.showAlert("処理中にエラーが発生しました。", "danger");
});
