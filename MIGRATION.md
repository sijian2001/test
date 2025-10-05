# ソースフォルダ構造変更 移行ガイド

## 概要

このドキュメントは、Issue #13「ソースフォルダ構造を変更する」に伴う移行ガイドです。
プロジェクトのソースコードが`app/`ディレクトリ配下に再編成されました。

## 変更内容

### ディレクトリ構造の変更

**変更前:**
```
.
├── batch/
├── business/
├── domain/
├── utils/
└── tests/
```

**変更後:**
```
.
├── app/
│   ├── batch/
│   ├── business/
│   ├── domain/
│   └── utils/
└── tests/
```

## 影響を受ける箇所と対応方法

### 1. Pythonスクリプトの実行コマンド

#### ユーザー管理システム (test1データベース)

**変更前:**
```bash
python batch/csv_import_main.py
python batch/csv_export_main.py
```

**変更後:**
```bash
python app/batch/csv_import_main.py
python app/batch/csv_export_main.py

# または、パッケージインストール後
csv-import
csv-export
```

#### 商品管理システム (test2データベース)

**変更前:**
```bash
python batch/categories_import_main.py
python batch/products_import_main.py
python batch/product_info_export_main.py
```

**変更後:**
```bash
python app/batch/categories_import_main.py
python app/batch/products_import_main.py
python app/batch/product_info_export_main.py

# または、パッケージインストール後
categories-import
products-import
product-info-export
```

### 2. Import文の変更

**変更前:**
```python
from batch.csv_import_processor import DataCsvImportProcessor
from business.user_regist_service import UserRegistService
from domain.repository.test1.user_repository import UserRepository
from utils.logger_utils import setup_application_logging
```

**変更後:**
```python
from app.batch.csv_import_processor import DataCsvImportProcessor
from app.business.user_regist_service import UserRegistService
from app.domain.repository.test1.user_repository import UserRepository
from app.utils.logger_utils import setup_application_logging
```

### 3. テストコード

テストコードのimport文も同様に更新が必要です。

**変更前:**
```python
from batch.categories_csv_import_processor import CategoriesCsvImportProcessorImpl
from business.category_regist_service import CategoryRegistService
```

**変更後:**
```python
from app.batch.categories_csv_import_processor import CategoriesCsvImportProcessorImpl
from app.business.category_regist_service import CategoryRegistService
```

### 4. CI/CDパイプライン

CI/CDスクリプトやジョブ定義で、Pythonスクリプトのパスを参照している場合は更新が必要です。

**例 (GitHub Actions):**
```yaml
# 変更前
- run: python batch/csv_import_main.py

# 変更後
- run: python app/batch/csv_import_main.py
```

### 5. ドキュメント・README

プロジェクトのドキュメント内で、ソースコードのパスを参照している箇所は更新済みです。
- `README.md`
- `CLAUDE.md`

社内ドキュメントやWikiなどの外部ドキュメントも同様に更新してください。

## パッケージとしてのインストール方法

### 開発環境でのインストール

```bash
# プロジェクトルートで実行
pip install -e .

# または、開発用依存関係も含めてインストール
pip install -e ".[dev]"
```

### インストール後の利用方法

パッケージとしてインストールすると、以下のコマンドが使用可能になります:

```bash
# ユーザー管理システム
csv-import          # ユーザー・部署CSVインポート
csv-export          # ユーザー情報CSVエクスポート

# 商品管理システム
categories-import   # カテゴリCSVインポート
products-import     # 商品CSVインポート
product-info-export # 商品情報CSVエクスポート
```

また、Pythonコードから直接importすることも可能です:

```python
from app.batch import DataCsvImportProcessor
from app.business import UserRegistService
from app.domain.repository.test1 import UserRepository
```

## 循環importのチェック

新しい構造で循環importが発生していないか確認するためのツールを用意しています。

```bash
# 循環importチェックツールのインストール
pip install -e ".[dev]"

# チェック実行
python scripts/check_circular_imports.py
```

## トラブルシューティング

### ModuleNotFoundError が発生する場合

**エラー例:**
```
ModuleNotFoundError: No module named 'batch'
```

**対処法:**
1. import文を`from app.batch`に修正
2. または、パッケージとしてインストール (`pip install -e .`)

### テストが失敗する場合

**症状:**
- テストのimportエラー
- モックパスの不一致

**対処法:**
1. テストファイルのimport文を確認し、`app.`プレフィックスを追加
2. `@patch`デコレーターのパスを`app.`付きに修正

**例:**
```python
# 変更前
@patch('batch.csv_import_processor.open')

# 変更後
@patch('app.batch.csv_import_processor.open')
```

### パス関連のエラー

**症状:**
- 設定ファイル(db.yaml, logger.yaml)が見つからない

**原因:**
- `sys.path`の設定が正しくない

**対処法:**
- メインスクリプト内の`sys.path.insert()`を確認
- プロジェクトルートからの相対パスが正しいか確認

## 後方互換性に関する注意

この変更により、以下の点で後方互換性が失われています:

1. **スクリプトのパス**: `batch/` → `app/batch/`
2. **Import文**: `from batch` → `from app.batch`
3. **パッケージ名**: 明示的なパッケージ名 `batch-processing-app`

既存のスクリプトやツールを使用している場合は、上記の変更に合わせて更新が必要です。

## チェックリスト

移行作業が完了したら、以下の項目を確認してください:

- [ ] 全てのメインスクリプトが正常に実行できる
- [ ] 全てのテストが成功する (`python -m pytest tests/ -v`)
- [ ] CI/CDパイプラインが正常に動作する
- [ ] ドキュメントが更新されている
- [ ] 循環importチェックが成功する (`python scripts/check_circular_imports.py`)

## サポート

移行に関して問題が発生した場合は、以下を確認してください:

1. このMIGRATION.mdドキュメント
2. README.mdの「実行方法」セクション
3. CLAUDE.mdの「メインアプリケーション」セクション

それでも解決しない場合は、開発チームに問い合わせてください。
