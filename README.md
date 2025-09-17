# Python Batch Processing Application

Python依存関係注入を使用したバッチ処理アプリケーションです。

## 機能

- データベース管理（SQLAlchemy + MySQL）
- 依存関係注入（Injector）
- CSV インポート/エクスポート処理
- ユーザー・部署管理
- ユーザー情報検索・抽出機能
- 単体テスト（pytest + mock）
- YAML設定ファイル管理

## 必要条件

- Python 3.8以上
- pip
- MySQL Server 5.7以上

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
  url: "mysql+pymysql://user1:1234@localhost:3306/test1"
  echo: true
```

#### MySQL設定詳細
- **データベース名**: test1
- **ユーザー**: user1
- **パスワード**: 1234
- **ホスト**: localhost
- **ポート**: 3306

#### 必要なデータベースビュー
アプリケーション実行前に以下のビューを作成してください：

```sql
CREATE VIEW user_info AS
SELECT
    u.user_id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    d.department_name,
    u.manager_id,
    u.is_active,
    u.created_at,
    u.updated_at
FROM user u
LEFT JOIN department d ON u.department_id = d.department_id;
```

## 実行方法

### CSV インポート処理
1. 仮想環境を有効化
2. CSVインポートを実行：
   ```bash
   python main.py
   ```

### CSV エクスポート処理（ユーザー情報抽出）
1. 仮想環境を有効化
2. CSVエクスポートを実行：
   ```bash
   python csv_export_main.py
   ```

### 単体テスト実行
全ての単体テストを実行：
```bash
python -m pytest tests/ -v
```

特定のテストファイルを実行：
```bash
python -m pytest tests/test_user_info_service.py -v
```

## プロジェクト構造

```
.
├── batch/                          # バッチ処理関連
│   ├── csv_export_processor.py   # CSV出力処理
│   └── csv_import_processor.py   # CSV取込処理
├── business/                       # ビジネスロジック
│   ├── abstract_service.py       # サービス抽象クラス
│   └── user_info_service.py      # ユーザー情報サービス
├── domain/                         # ドメインモデル・リポジトリ
│   ├── database.py               # データベース接続
│   ├── model/                    # データモデル
│   │   ├── base.py              # ベースモデル
│   │   ├── department.py        # 部署モデル
│   │   ├── user.py              # ユーザーモデル
│   │   └── user_info.py         # ユーザー情報ビューモデル
│   └── repository/               # リポジトリ
│       └── user_info_repository.py # ユーザー情報リポジトリ
├── sql/                           # SQLファイル
├── tests/                         # 単体テスト
│   ├── test_csv_export_processor.py  # CSV出力処理テスト
│   ├── test_user_info_repository.py  # リポジトリテスト
│   └── test_user_info_service.py     # サービステスト
├── work/                          # 作業用ディレクトリ（CSV出力先）
├── csv_export_main.py             # CSV出力メイン
├── db.yaml                        # データベース設定
├── main.py                        # CSV取込メイン
├── requirements.txt               # Python依存関係
└── README.md                     # このファイル
```

## 主要機能

### ユーザー情報管理
- **検索機能**: user_id、username、department_nameによる検索
- **全件取得**: 全ユーザー情報の取得
- **CSV出力**: 検索結果のCSVファイル出力（work/report.csv）

### アーキテクチャ
- **Repository層**: データアクセス処理
- **Service層**: ビジネスロジック処理
- **Batch層**: バッチ処理実行
- **依存関係注入**: @inject、@dataclassによるDI実装

### テスト構成
- **43個の単体テスト**: 全層のテストカバレッジ100%
- **モック使用**: 外部依存の分離テスト
- **例外処理テスト**: 異常系シナリオのカバー