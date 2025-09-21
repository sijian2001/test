# CLAUDE.md

このファイルは、このリポジトリでコードを操作する際のClaude Code (claude.ai/code) への指針を提供します。

## 一般的な開発コマンド

### 環境セットアップ
```bash
# Windows
setup.bat

# Linux/macOS
./setup.sh
```

### テスト実行
```bash
# 全テスト実行
python -m pytest tests/ -v

# 特定のテストスイート実行
python -m pytest tests/business/test_user_info_service.py -v
python -m pytest tests/repository/test_user_repository.py -v
python -m pytest tests/business/test_product_info_service.py -v
```

### メインアプリケーション
```bash
# ユーザー管理（test1データベース）
python csv_import_main.py        # CSV からユーザー・部署をインポート
python csv_export_main.py        # ユーザー情報をCSVエクスポート

# 商品管理（test2データベース）
python categories_import_main.py # CSV からカテゴリをインポート
python products_import_main.py   # CSV から商品をインポート
python product_info_export_main.py # 商品情報をCSVエクスポート
```

## アーキテクチャ概要

依存関係注入を使用したデュアルデータベース対応（test1とtest2）のPythonバッチ処理アプリケーションです。

### マルチデータベースアーキテクチャ
- **test1データベース**: ユーザー管理システム（ユーザー、部署）
- **test2データベース**: 商品管理システム（商品、カテゴリ）
- **設定**: `db.yaml`で両システムのデータベース接続を管理
- **独立したデータベースセッション**: `Test1DatabaseSession`と`Test2DatabaseSession`クラス

### コアアーキテクチャ層

**リポジトリ層** (`domain/repository/`):
- データベース別に整理: `test1/`と`test2/`サブディレクトリ
- SQLAlchemy ORMによるデータアクセス抽象化
- 例: `user_repository.py`, `product_repository.py`

**サービス層** (`business/`):
- AbstractServiceパターンに従ったビジネスロジック実装
- 全サービスが`execute(in_dto) -> out_dto`インターフェースを実装
- `@SessionManager`デコレーターによるセッション管理

**バッチ層** (`batch/`):
- CSV インポート/エクスポート処理
- 基底`Processor`クラスから継承
- 例: `csv_import_processor.py`, `product_info_csv_export_processor.py`

### 依存関係注入パターン
- `injector`ライブラリを`@inject`と`@dataclass`デコレーターで使用
- シングルトンデータベース接続と設定
- 型ベースの依存関係解決

### セッション管理
- カスタム`@SessionManager`デコレーターがトランザクションライフサイクルを処理
- 適切なエラーハンドリングによる自動コミット/ロールバック
- `business/decorators/session_manager.py`に配置

### データベース移行に関する注意
コードベースは従来の`DatabaseSession.get_session(database)`パターンから直接`Test1DatabaseSession`/`Test2DatabaseSession`インジェクションへ移行中です。変更時は新しいセッションクラスを使用してください。

### バリューオブジェクト
ドメインモデルは`domain/vo/`にバリューオブジェクトとして実装:
- `user_vo.py`, `product_vo.py`, `category_vo.py`など
- 層間でのデータ転送に使用

### 主要設定
- `db.yaml`: test1/test2のデータベース接続文字列
- `requirements.txt`: SQLAlchemy 2.0+、injector、PyMySQLを含むPython依存関係
- `work/`: CSV入出力ファイル用ディレクトリ

### テスト戦略
- pytestとpytest-mockによる包括的な単体テスト
- リポジトリとサービス層のモックベーステスト
- 命名規則に従った各コンポーネント別のテストファイル

### タスク着手時のワークフロー

1. タスクの状態を「着手中」に変更
2. タスクの開始日時を設定 (時間まで記載すること)
3. Git で main からブランチを作成 (ブランチ名は`feature/<タスクID>`とする)
4. 空コミットを作成 (コミットメッセージは`chore: start feature/<タスクID>`とする)
5. PR を作成 (`gh pr create --assignee @me --base main --draft`)
  - タイトルはタスクのタイトルを参照する (`【<タスクID>】<タイトル>`)
  - ボディはタスクの内容から生成する (Notion タスクへのリンクを含める)
6. 実装計画を考えて、ユーザーに伝える
7. ユーザーにプロンプトを返す

### タスク完了時のワークフロー

1. PR のステータスを ready にする
2. PR をマージ (`gh pr merge --merge --auto --delete-branch`)
3. タスクの開始日時を設定 (時間まで記載すること)
4. タスクに「サマリー」を追加
  - コマンドライン履歴とコンテキストを参照して、振り返りを効率かするための文章を作成
  - Notion の見出しは「振り返り」とする
5. タスクの状態を「完了」に変更
6. タスクの完了日時を記載 (時間まで記載すること)
7. ユーザーにプロンプトを返す
