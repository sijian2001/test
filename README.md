# Python Batch Processing Application

Python依存関係注入を使用したバッチ処理アプリケーションです。

## 機能

- データベース管理（SQLAlchemy）
- 依存関係注入（Injector）
- CSV インポート処理
- ユーザー・部署管理
- YAML設定ファイル管理

## 必要条件

- Python 3.8以上
- pip

## 開発環境セットアップ

### 自動セットアップ（推奨）

#### Windows
```bash
setup.bat
```

#### Linux/macOS
```bash
./setup.sh
```

### 手動セットアップ

1. **仮想環境を作成**
   ```bash
   python -m venv venv
   ```

2. **仮想環境を有効化**

   Windows:
   ```bash
   venv\Scripts\activate
   ```

   Linux/macOS:
   ```bash
   source venv/bin/activate
   ```

3. **依存関係をインストール**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### 仮想環境の使用

- **有効化**: 開発開始時に実行
  - Windows: `venv\Scripts\activate`
  - Linux/macOS: `source venv/bin/activate`

- **無効化**: 開発終了時に実行
  ```bash
  deactivate
  ```

## 設定

### データベース設定

`db.yaml`ファイルでデータベース設定を管理：

```yaml
database:
  url: "sqlite:///batch_example.db"
  echo: true
```

## 実行方法

1. 仮想環境を有効化
2. アプリケーションを実行：
   ```bash
   python main.py
   ```

## プロジェクト構造

```
.
├── batch/              # バッチ処理関連
├── business/           # ビジネスロジック
├── domain/             # ドメインモデル・リポジトリ
├── sql/                # SQLファイル
├── work/               # 作業用ディレクトリ
├── db.yaml             # データベース設定
├── requirements.txt    # Python依存関係
└── README.md          # このファイル
```