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
├── batch/                                  # バッチ処理関連
│   ├── csv_export_batch_processor.py     # CSV出力バッチ処理
│   ├── csv_export_processor.py           # CSV出力処理
│   ├── csv_import_processor.py           # CSV取込処理
│   ├── data_batch_processor.py           # データバッチ処理
│   └── processor.py                      # 処理基底クラス
├── business/                               # ビジネスロジック
│   ├── decorators/                        # デコレータ
│   │   └── session_manager.py            # セッション管理デコレータ
│   ├── abstract_service.py               # サービス抽象クラス
│   ├── csv_export_service.py             # CSV出力サービス
│   ├── depart_user_regist_service.py     # 部署ユーザー登録サービス
│   ├── department_regist_service.py      # 部署登録サービス
│   ├── user_info_service.py              # ユーザー情報サービス
│   └── user_regist_service.py            # ユーザー登録サービス
├── domain/                                 # ドメインモデル・リポジトリ
│   ├── model/                             # データモデル
│   │   ├── base.py                       # ベースモデル
│   │   ├── department.py                 # 部署モデル
│   │   ├── user.py                       # ユーザーモデル
│   │   └── user_info.py                  # ユーザー情報ビューモデル
│   ├── repository/                        # リポジトリ
│   │   ├── department_repository.py      # 部署リポジトリ
│   │   ├── user_info_repository.py       # ユーザー情報リポジトリ
│   │   └── user_repository.py            # ユーザーリポジトリ
│   ├── vo/                                # バリューオブジェクト
│   │   ├── department_vo.py              # 部署VO
│   │   └── user_vo.py                    # ユーザーVO
│   └── database.py                        # データベース接続
├── sql/                                    # SQLファイル
│   ├── create_db_user.sql                # DB・ユーザー作成
│   ├── create_department_table.sql       # 部署テーブル作成
│   ├── create_user_info_view.sql         # ユーザー情報ビュー作成
│   └── create_user_table.sql             # ユーザーテーブル作成
├── tests/                                  # 単体テスト
│   ├── test_csv_export_processor.py      # CSV出力処理テスト
│   ├── test_user_info_repository.py      # リポジトリテスト
│   └── test_user_info_service.py         # サービステスト
├── work/                                   # 作業用ディレクトリ（CSV入出力）
│   ├── department.csv                    # 部署CSVサンプル
│   ├── report.csv                        # ユーザー情報出力
│   └── user.csv                          # ユーザーCSVサンプル
├── csv_export_main.py                      # CSV出力メインプログラム
├── csv_import_main.py                      # CSV取込メインプログラム
├── db.yaml                                 # データベース設定
├── main.py                                 # 共通メインプログラム
├── requirements.txt                        # Python依存関係
├── setup.bat                               # Windows環境セットアップ
├── setup.sh                               # Linux/macOS環境セットアップ
└── README.md                              # このファイル
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