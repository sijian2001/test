# Python Batch Processing Application

Python依存関係注入を使用したバッチ処理アプリケーションです。

## 機能

- データベース管理（SQLAlchemy + MySQL）
- 依存関係注入（Injector）
- CSV インポート/エクスポート処理
- **test1データベース（ユーザー管理システム）**
  - ユーザー・部署管理
  - ユーザー情報検索・抽出機能
- **test2データベース（商品管理システム）**
  - 商品・カテゴリ管理
  - 商品情報検索・抽出機能
- 包括的な単体テスト（pytest + mock）
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
  test1:
    url: "mysql+pymysql://user1:1234@localhost:3306/test1"
    echo: true
  test2:
    url: "mysql+pymysql://user1:1234@localhost:3306/test2"
    echo: true
```

#### MySQL設定詳細
- **test1データベース（ユーザー管理）**
  - データベース名: test1
  - ユーザー: user1
  - パスワード: 1234
- **test2データベース（商品管理）**
  - データベース名: test2
  - ユーザー: user1
  - パスワード: 1234
- **共通設定**
  - ホスト: localhost
  - ポート: 3306

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

### test1データベース（ユーザー管理システム）

#### CSV インポート処理
```bash
python batch/csv_import_main.py
```

#### CSV エクスポート処理（ユーザー情報抽出）
```bash
python batch/csv_export_main.py
```

### test2データベース（商品管理システム）

#### カテゴリCSV インポート処理
```bash
python batch/categories_import_main.py
```

#### 商品CSV インポート処理
```bash
python batch/products_import_main.py
```

#### 商品情報CSV エクスポート処理
```bash
python batch/product_info_export_main.py
```

### 単体テスト実行
全ての単体テストを実行：
```bash
python -m pytest tests/ -v
```

特定のテストを実行：
```bash
# ユーザー管理システムのテスト
python -m pytest tests/business/test_user_info_service.py -v
python -m pytest tests/repository/test_user_repository.py -v

# 商品管理システムのテスト
python -m pytest tests/business/test_product_info_service.py -v
python -m pytest tests/repository/test_product_repository.py -v
python -m pytest tests/business/test_category_regist_service.py -v
```

## プロジェクト構造

```
.
├── batch/                                          # バッチ処理関連
│   ├── categories_csv_import_processor.py         # カテゴリCSV取込処理
│   ├── categories_import_main.py                  # カテゴリ取込メインプログラム
│   ├── csv_export_batch_processor.py             # CSV出力バッチ処理
│   ├── csv_export_main.py                         # ユーザー情報出力メインプログラム
│   ├── csv_export_processor.py                   # CSV出力処理
│   ├── csv_import_main.py                         # ユーザー取込メインプログラム
│   ├── csv_import_processor.py                   # CSV取込処理
│   ├── data_batch_processor.py                   # データバッチ処理
│   ├── processor.py                              # 処理基底クラス
│   ├── product_info_csv_export_processor.py      # 商品情報CSV出力処理
│   ├── product_info_export_main.py                # 商品情報出力メインプログラム
│   ├── products_csv_import_processor.py          # 商品CSV取込処理
│   └── products_import_main.py                    # 商品取込メインプログラム
├── business/                                       # ビジネスロジック
│   ├── decorators/                                # デコレータ
│   │   └── session_manager.py                    # セッション管理デコレータ
│   ├── abstract_service.py                       # サービス抽象クラス
│   ├── category_regist_service.py                # カテゴリ登録サービス
│   ├── csv_export_service.py                     # CSV出力サービス
│   ├── department_regist_service.py              # 部署登録サービス
│   ├── depart_user_regist_service.py             # 部署ユーザー登録サービス
│   ├── product_info_service.py                   # 商品情報サービス
│   ├── product_regist_service.py                 # 商品登録サービス
│   ├── user_info_service.py                      # ユーザー情報サービス
│   └── user_regist_service.py                    # ユーザー登録サービス
├── domain/                                         # ドメインモデル・リポジトリ
│   ├── model/                                     # データモデル（未使用）
│   ├── repository/                                # リポジトリ
│   │   ├── test1/                                 # test1データベース用
│   │   │   ├── department_repository.py          # 部署リポジトリ
│   │   │   ├── user_info_repository.py           # ユーザー情報リポジトリ
│   │   │   └── user_repository.py                # ユーザーリポジトリ
│   │   └── test2/                                 # test2データベース用
│   │       ├── category_repository.py            # カテゴリリポジトリ
│   │       ├── product_info_repository.py        # 商品情報リポジトリ
│   │       └── product_repository.py             # 商品リポジトリ
│   ├── vo/                                        # バリューオブジェクト
│   │   ├── category_vo.py                        # カテゴリVO
│   │   ├── department_vo.py                      # 部署VO
│   │   ├── product_info_vo.py                    # 商品情報VO
│   │   ├── product_vo.py                         # 商品VO
│   │   └── user_vo.py                            # ユーザーVO
│   └── database.py                                # データベース接続
├── sql/                                            # SQLファイル
│   ├── create_db_user.sql                        # DB・ユーザー作成
│   ├── create_department_table.sql               # 部署テーブル作成
│   ├── create_user_info_view.sql                 # ユーザー情報ビュー作成
│   └── create_user_table.sql                     # ユーザーテーブル作成
├── tests/                                          # 単体テスト
│   ├── batch/                                     # バッチ処理テスト
│   │   ├── test_categories_csv_import_processor.py
│   │   ├── test_csv_export_processor.py
│   │   ├── test_product_info_csv_export_processor.py
│   │   └── test_products_csv_import_processor.py
│   ├── business/                                  # ビジネスロジックテスト
│   │   ├── test_category_regist_service.py
│   │   ├── test_department_regist_service.py
│   │   ├── test_product_info_service.py
│   │   ├── test_product_regist_service.py
│   │   ├── test_user_info_service.py
│   │   └── test_user_regist_service.py
│   └── repository/                                # リポジトリテスト
│       ├── test_category_repository.py
│       ├── test_department_repository.py
│       ├── test_product_info_repository.py
│       ├── test_product_repository.py
│       ├── test_user_info_repository.py
│       └── test_user_repository.py
├── work/                                           # 作業用ディレクトリ（CSV入出力）
│   ├── categories.csv                            # カテゴリCSVサンプル
│   ├── department.csv                            # 部署CSVサンプル
│   ├── products.csv                              # 商品CSVサンプル
│   ├── product_report.csv                        # 商品情報出力
│   ├── report.csv                                # ユーザー情報出力
│   └── user.csv                                  # ユーザーCSVサンプル
├── db.yaml                                         # データベース設定
├── logger.yaml                                     # ロガー設定
├── main.py                                         # 共通メインプログラム
├── requirements.txt                                # Python依存関係
├── setup.bat                                       # Windows環境セットアップ
├── setup.sh                                       # Linux/macOS環境セットアップ
└── README.md                                      # このファイル
```

## 主要機能

### test1データベース（ユーザー管理システム）
- **ユーザー情報管理**
  - user_id、username、department_nameによる検索
  - 全ユーザー情報の取得
  - CSV出力（work/report.csv）
- **部署管理**
  - 部署情報の登録・管理

### test2データベース（商品管理システム）
- **商品情報管理**
  - 商品情報の登録・検索
  - カテゴリ別商品検索
  - CSV出力（work/product_report.csv）
- **カテゴリ管理**
  - カテゴリ情報の登録・管理

### アーキテクチャ
- **Repository層**: データアクセス処理（test1/test2別）
- **Service層**: ビジネスロジック処理
- **Batch層**: バッチ処理実行
- **依存関係注入**: @inject、@dataclassによるDI実装
- **マルチデータベース対応**: test1とtest2の独立した管理

### テスト構成
- **包括的な単体テスト**: 全層の完全なテストカバレッジ
- **モック使用**: 外部依存の分離テスト
- **例外処理テスト**: 異常系シナリオのカバー
- **マルチデータベーステスト**: test1/test2両システムのテスト