/**
 * 画像アップロード機能
 * ドラッグ&ドロップ、ファイル選択、プレビュー表示を管理
 */

class ImageUploader {
  constructor() {
    this.uploadArea = document.getElementById("uploadArea");
    this.imageInput = document.getElementById("imageInput");
    this.preview = document.getElementById("preview");
    this.previewImage = document.getElementById("previewImage");
    this.analyzeBtn = document.getElementById("analyzeBtn");
    this.uploadForm = document.getElementById("uploadForm");
    this.spinner = document.getElementById("spinner");

    this.init();
  }

  init() {
    this.setupDragAndDrop();
    this.setupFileInput();
    this.setupFormSubmission();
  }

  /**
   * ドラッグ&ドロップ機能の設定
   */
  setupDragAndDrop() {
    this.uploadArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      this.uploadArea.classList.add("dragover");
    });

    this.uploadArea.addEventListener("dragleave", () => {
      this.uploadArea.classList.remove("dragover");
    });

    this.uploadArea.addEventListener("drop", (e) => {
      e.preventDefault();
      this.uploadArea.classList.remove("dragover");
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.handleFileSelection(files);
      }
    });
  }

  /**
   * ファイル入力の設定
   */
  setupFileInput() {
    this.imageInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        this.handleFileSelection(e.target.files);
      }
    });
  }

  /**
   * フォーム送信の設定
   */
  setupFormSubmission() {
    this.uploadForm.addEventListener("submit", () => {
      this.setLoadingState();
    });
  }

  /**
   * ファイル選択の処理
   * @param {FileList} files - 選択されたファイルリスト
   */
  handleFileSelection(files) {
    if (files.length > 0) {
      this.imageInput.files = files;
      this.showPreview(files[0]);
    }
  }

  /**
   * プレビュー表示
   * @param {File} file - 表示するファイル
   */
  showPreview(file) {
    // ファイルタイプの検証
    if (!file.type.startsWith("image/")) {
      alert("画像ファイルを選択してください。");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      this.previewImage.src = e.target.result;
      this.preview.style.display = "block";
      this.analyzeBtn.disabled = false;
    };
    reader.onerror = () => {
      alert("ファイルの読み込みに失敗しました。");
    };
    reader.readAsDataURL(file);
  }

  /**
   * ローディング状態の設定
   */
  setLoadingState() {
    this.analyzeBtn.disabled = true;
    this.spinner.classList.remove("d-none");
    this.analyzeBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm"></span> 解析中...';
  }
}

// DOMContentLoadedイベントでクラスを初期化
document.addEventListener("DOMContentLoaded", () => {
  new ImageUploader();
});
