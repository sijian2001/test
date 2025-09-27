# システム設計書

## 1. 概要

### 1.1 システム名
デュアルデータベース対応Pythonバッチ処理システム

### 1.2 目的
- ユーザー管理システム（test1データベース）
- 商品管理システム（test2データベース）
- CSVデータのインポート/エクスポート機能
- クリーンアーキテクチャに基づく保守性の高いシステム

### 1.3 対象システム
- Python 3.9+
- MySQL 8.0+
- SQLAlchemy 2.0+

## 2. アーキテクチャ設計

### 2.1 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    Batch Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ CSV Import      │  │ CSV Export      │              │
│  │ Processors      │  │ Processors      │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                   Business Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Service Classes │  │ Value Objects   │              │
│  │ (CRUD+Search)   │  │ (DTOs)          │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                   Domain Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Repository      │  │ Domain Models   │              │
│  │ Interfaces      │  │ (SQLAlchemy)    │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                Infrastructure Layer                     │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ test1 DB     │  │ test2 DB     │                    │
│  │ (Users/Dept) │  │ (Products)   │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 レイヤー構成

#### 2.2.1 Batch Layer (`batch/`)
- **責務**: CSV処理、バッチ処理の制御
- **主要コンポーネント**:
  - `Processor` (基底クラス)
  - CSV Import Processors
  - CSV Export Processors
- **特徴**: Business Layerを呼び出してデータ処理を実行

#### 2.2.2 Business Layer (`business/`)
- **責務**: ビジネスロジック、データ変換、ワークフロー制御
- **主要コンポーネント**:
  - `AbstractService` パターン
  - Value Objects (DTOs)
  - Session Management Decorators
- **特徴**: `execute(in_dto) -> out_dto` の統一インターフェース

#### 2.2.3 Domain Layer (`domain/`)
- **責務**: ドメインモデル、データアクセス抽象化
- **主要コンポーネント**:
  - SQLAlchemy Entity Models
  - Repository Classes
  - Database Session Management
- **特徴**: データベース別に分離されたリポジトリ

### 2.3 依存関係注入

```python
# 基本パターン
from injector import inject, Injector
from dataclasses import dataclass

@dataclass
class UserRegistService:
    user_repository: UserRepository = inject

    def execute(self, in_dto: UserRegistInDto) -> UserRegistOutDto:
        # ビジネスロジック実装
        pass
```

### 2.4 セッション管理

```python
# デコレーターパターンによるトランザクション管理
from business.decorators.session_manager import SessionManager

@SessionManager(database='test1')
def execute(self, in_dto):
    # 自動的にセッション開始・終了
    # エラー時は自動ロールバック
    pass
```

## 3. データベース設計

### 3.1 デュアルデータベース構成

#### 3.1.1 test1データベース（ユーザー管理）

**userテーブル**
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INT | PK, AUTO_INCREMENT | ユーザーID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | ユーザー名 |
| email | VARCHAR(100) | NOT NULL, UNIQUE | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | パスワードハッシュ |
| first_name | VARCHAR(50) | | 名 |
| last_name | VARCHAR(50) | | 姓 |
| department_id | INT | | 部署ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新日時 |
| is_active | BOOLEAN | DEFAULT TRUE | 有効フラグ |

**departmentテーブル**
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| id | INT | PK, AUTO_INCREMENT | 部署ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 部署名 |
| description | TEXT | | 説明 |
| manager_id | INT | | 管理者ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新日時 |
| is_active | BOOLEAN | DEFAULT TRUE | 有効フラグ |

#### 3.1.2 test2データベース（商品管理）

**productsテーブル**
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| product_id | INT | PK, AUTO_INCREMENT | 商品ID |
| product_name | VARCHAR(255) | NOT NULL | 商品名 |
| description | TEXT | | 商品説明 |
| price | DECIMAL(10,2) | NOT NULL | 価格 |
| stock_quantity | INT | NOT NULL, DEFAULT 0 | 在庫数 |
| category_id | INT | FK → categories.category_id | カテゴリID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

**categoriesテーブル**
| カラム名 | データ型 | 制約 | 説明 |
|----------|----------|------|------|
| category_id | INT | PK, AUTO_INCREMENT | カテゴリID |
| category_name | VARCHAR(255) | NOT NULL, UNIQUE | カテゴリ名 |
| category_description | TEXT | | カテゴリ説明 |
| parent_category_id | INT | FK → categories.category_id | 親カテゴリID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### 3.2 データベース接続設定

```yaml
# db.yaml
database:
  test1:
    url: "mysql+pymysql://user1:1234@localhost:3306/test1"
    echo: true
  test2:
    url: "mysql+pymysql://user2:1234@localhost:3306/test2"
    echo: true
```

## 4. コンポーネント設計

### 4.1 Business Layer Components

#### 4.1.1 Service Classes
- **共通パターン**: `AbstractService` を継承
- **インターフェース**: `execute(in_dto: AbstractInDto) -> AbstractOutDto`
- **主要サービス**:
  - `UserRegistService`: ユーザー登録
  - `UserInfoService`: ユーザー情報検索
  - `ProductRegistService`: 商品登録
  - `ProductInfoService`: 商品情報検索
  - `CategoryRegistService`: カテゴリ登録
  - `DepartmentRegistService`: 部署登録

#### 4.1.2 Value Objects (DTOs)
**配置**: `business/vo/`

**UserVo**
```python
@dataclass
class UserVo:
    username: str
    email: str
    password_hash: str
    first_name: str = None
    last_name: str = None
    department_id: int = None
    is_active: bool = True
```

**ProductVo**
```python
@dataclass
class ProductVo:
    product_name: str
    description: str
    price: float
    stock_quantity: int
    category_id: int = None
```

### 4.2 Batch Layer Components

#### 4.2.1 Processor Classes
**基底クラス**: `Processor`

**主要プロセッサー**:
- `CsvImportProcessor`: ユーザー・部署一括インポート
- `ProductsCsvImportProcessor`: 商品一括インポート
- `CategoriesCsvImportProcessor`: カテゴリ一括インポート
- `UserInfoCsvExportProcessor`: ユーザー情報エクスポート
- `ProductInfoCsvExportProcessor`: 商品情報エクスポート

#### 4.2.2 処理フロー
```
CSV読み込み → 行データバリデーション → VO変換 → Service呼び出し → 結果集計
```

### 4.3 Domain Layer Components

#### 4.3.1 Repository Classes
**パターン**: データベース別の分離構成

**test1データベース用**:
- `UserRepository`: ユーザーCRUD操作
- `DepartmentRepository`: 部署CRUD操作
- `UserInfoRepository`: ユーザー情報検索（JOIN処理）

**test2データベース用**:
- `ProductRepository`: 商品CRUD操作
- `CategoryRepository`: カテゴリCRUD操作
- `ProductInfoRepository`: 商品情報検索（JOIN処理）

#### 4.3.2 Database Session Management
```python
class Test1DatabaseSession:
    """test1データベース専用セッション"""

class Test2DatabaseSession:
    """test2データベース専用セッション"""
```

## 5. API設計

### 5.1 Service Interface 標準化

**統一インターフェース**:
```python
class Service(AbstractService):
    def execute(self, in_dto: InDto) -> OutDto:
        """
        Args:
            in_dto: 入力データ転送オブジェクト
        Returns:
            out_dto: 出力データ転送オブジェクト
        """
```

### 5.2 主要API一覧

#### 5.2.1 ユーザー管理API
- `UserRegistService.execute(UserRegistInDto) -> UserRegistOutDto`
- `UserInfoService.execute(UserInfoSearchInDto) -> UserInfoOutDto`

#### 5.2.2 商品管理API
- `ProductRegistService.execute(ProductRegistInDto) -> ProductRegistOutDto`
- `ProductInfoService.execute(ProductInfoSearchInDto) -> ProductInfoOutDto`

#### 5.2.3 バッチ処理API
- `CsvImportProcessor.run_csv_import_process(file_path) -> ProcessResult`
- `CsvExportProcessor.run_csv_export_process() -> ProcessResult`

## 6. 非機能要件

### 6.1 パフォーマンス
- **バッチ処理**: 1万件/分の処理速度目標
- **データベース接続**: コネクションプール活用
- **メモリ使用量**: 大容量CSVの逐次処理対応

### 6.2 信頼性
- **トランザクション管理**: 自動コミット/ロールバック
- **エラーハンドリング**: 段階的エラー処理
- **データ整合性**: 外部キー制約による整合性保証

### 6.3 保守性
- **テスト戦略**: 単体テスト率90%以上
- **ログ設計**: 構造化ログによる追跡性確保
- **設定管理**: YAML設定ファイルによる環境別管理

### 6.4 セキュリティ
- **パスワード管理**: ハッシュ化によるパスワード保護
- **データベースアクセス**: ユーザー別アクセス制御
- **入力検証**: CSV入力データの事前バリデーション

## 7. 開発・運用

### 7.1 開発環境
```bash
# 環境セットアップ
python -m venv venv
pip install -r requirements.txt

# テスト実行
python -m pytest tests/ -v

# バッチ実行例
python csv_import_main.py
python product_info_export_main.py
```

### 7.2 依存関係
- **Core**: SQLAlchemy 2.0+, PyMySQL 1.0+
- **DI**: injector 0.20+
- **Configuration**: PyYAML 6.0+, python-dotenv 1.0+
- **Testing**: pytest 7.0+, pytest-mock 3.10+

### 7.3 ディレクトリ構成
```
├── batch/                  # バッチ処理層
├── business/              # ビジネスロジック層
│   ├── decorators/        # デコレーター
│   └── vo/               # Value Objects
├── domain/               # ドメイン層
│   ├── model/            # ドメインモデル
│   │   ├── test1/        # test1DB用モデル
│   │   └── test2/        # test2DB用モデル
│   └── repository/       # リポジトリ
│       ├── test1/        # test1DB用リポジトリ
│       └── test2/        # test2DB用リポジトリ
├── tests/                # テストコード
├── work/                 # CSV入出力ディレクトリ
├── db.yaml              # データベース設定
├── requirements.txt     # Python依存関係
└── CLAUDE.md           # 開発ガイド
```

## 8. 今後の拡張計画

### 8.1 機能拡張
- REST API レイヤーの追加
- 非同期処理による高速化
- データ暗号化機能の実装

### 8.2 技術的改善
- GraphQL API対応
- Redis によるキャッシュ機能
- Docker コンテナ化対応

### 8.3 運用改善
- CI/CD パイプライン構築
- 監視・アラート機能
- 自動バックアップ機能

---

**文書バージョン**: 1.0
**作成日**: 2025-09-23
**最終更新**: 2025-09-23
**作成者**: Claude Code