# Transactionalデコレーター設計書

## 概要
Spring Frameworkの@Transactionalアノテーションを参考にした、Pythonのトランザクション管理デコレーターを実装する。

## 目的
- 宣言的なトランザクション管理を提供
- コードの可読性向上（トランザクション境界を明確化）
- Spring開発者にとって馴染みのあるAPIを提供
- 既存のSessionManagerと統合

## Spring Boot @Transactionalの動作

Context7調査結果に基づく実装参考:

### Spring Bootが行うDB操作
1. **トランザクション開始**: `connection.setAutoCommit(false)`
2. **トランザクション終了**:
   - 成功時: `connection.commit()`
   - 例外時: `connection.rollback()`
3. **セッション管理**: AOPプロキシがEntityManager/Sessionのライフサイクルを管理
4. **セッションクローズ**: トランザクション終了時にEntityManager.close()を自動実行

### 実装メカニズム
- AOPプロキシがメソッド呼び出しをインターセプト
- TransactionInterceptorがトランザクションライフサイクルを管理
- finallyブロックで確実にリソースをクリーンアップ

## 要件

### 機能要件

#### FR-1: トランザクション自動管理
- メソッド開始時にトランザクションを開始
- メソッド成功時に自動コミット
- 例外発生時に自動ロールバック

#### FR-2: セッション管理統合
- 既存のSessionManagerと統合可能
- セッションの取得・クローズを自動化

#### FR-3: ロールバック制御
- デフォルト: すべての例外でロールバック
- オプション: 特定の例外のみロールバック（rollback_for）
- オプション: 特定の例外を除外（no_rollback_for）

#### FR-4: 読み取り専用トランザクション
- read_onlyオプションでパフォーマンス最適化のヒントを提供

#### FR-5: データベース指定
- databaseパラメータでtest1/test2データベースを指定

### 非機能要件

#### NFR-1: 既存コードとの互換性
- 既存のSessionManagerを使用しているコードと共存可能
- 段階的な移行が可能

#### NFR-2: ロギング
- トランザクション開始・終了・ロールバックをログ出力
- デバッグ時の追跡を容易にする

#### NFR-3: テスタビリティ
- ユニットテストでモック可能
- トランザクション動作を検証可能

## アーキテクチャ設計

### クラス構成

```
app/business/decorators/
├── session_manager.py          # 既存: セッション管理デコレーター
└── transactional.py            # 新規: トランザクション管理デコレーター
```

### Transactionalデコレーターの設計

#### クラス図（疑似）
```
Transactional
├── __init__(database, read_only, rollback_for, no_rollback_for)
├── __call__(func) -> wrapper
└── _should_rollback(exception) -> bool
```

#### 処理フロー
```python
@Transactional(database=DatabaseType.TEST1)
def service_method(self, dto):
    # ユーザーコード
    pass

# 実行時の処理フロー:
# 1. デコレーター呼び出し
# 2. セッション取得
# 3. トランザクション開始（暗黙的）
# 4. service_method実行
# 5a. 成功 → session.commit()
# 5b. 例外 → session.rollback()
# 6. session.close() (finally)
```

### SessionManagerとの関係

#### 現在のSessionManager
```python
@dataclass
class SessionManager:
    """セッションのライフサイクル管理のみ"""
    database: DatabaseType

    def __call__(self, func):
        def wrapper(self_instance, *args, **kwargs):
            session = get_session()
            try:
                return func(self_instance, *args, **kwargs)
            finally:
                session.close()
```

#### 新しいTransactional
```python
@dataclass
class Transactional:
    """トランザクション境界を明示的に管理"""
    database: DatabaseType
    read_only: bool = False
    rollback_for: tuple = (Exception,)
    no_rollback_for: tuple = ()

    def __call__(self, func):
        def wrapper(self_instance, *args, **kwargs):
            session = get_session()
            try:
                result = func(self_instance, *args, **kwargs)
                session.commit()  # 明示的なコミット
                return result
            except Exception as e:
                if self._should_rollback(e):
                    session.rollback()
                raise
            finally:
                session.close()
```

### 使い分け

| デコレーター | 用途 | トランザクション制御 | セッション管理 |
|------------|------|-------------------|--------------|
| SessionManager | セッション管理のみ必要 | なし（手動） | 自動 |
| Transactional | トランザクション境界を明示 | 自動 | 自動 |

## 実装仕様

### パラメータ仕様

#### database: DatabaseType (必須)
- `DatabaseType.TEST1`: test1データベース
- `DatabaseType.TEST2`: test2データベース

#### read_only: bool (デフォルト: False)
- `True`: 読み取り専用トランザクション（最適化ヒント）
- `False`: 読み書きトランザクション

#### rollback_for: tuple (デフォルト: (Exception,))
- ロールバック対象の例外クラスのタプル
- デフォルトではすべての例外でロールバック

#### no_rollback_for: tuple (デフォルト: ())
- ロールバックしない例外クラスのタプル
- rollback_forより優先度が高い

### 例外処理仕様

#### ロールバック判定ロジック
```python
def _should_rollback(self, exception: Exception) -> bool:
    """
    例外がロールバック対象かを判定

    優先順位:
    1. no_rollback_for に含まれる → ロールバックしない
    2. rollback_for に含まれる → ロールバックする
    3. どちらにも含まれない → ロールバックしない
    """
    if isinstance(exception, self.no_rollback_for):
        return False
    if isinstance(exception, self.rollback_for):
        return True
    return False
```

### ログ出力仕様

#### ログレベルとメッセージ
- INFO: トランザクション開始・コミット
- WARNING: ロールバック
- ERROR: 予期しないエラー

#### ログフォーマット例
```
[INFO] Transaction started for test1
[INFO] Transaction committed for test1
[WARNING] Transaction rolled back for test1: ValueError: Invalid input
```

## 使用例

### 基本的な使用例
```python
from app.business.decorators.transactional import Transactional
from app.infrastructure.database.database_type import DatabaseType

class UserService:
    @Transactional(database=DatabaseType.TEST1)
    def create_user(self, in_dto: CreateUserInDto) -> CreateUserOutDto:
        # トランザクション内で実行
        # 成功時: 自動コミット
        # 例外時: 自動ロールバック
        user = self.user_repository.create_user(...)
        return CreateUserOutDto(user_id=user.id)
```

### 読み取り専用トランザクション
```python
@Transactional(database=DatabaseType.TEST1, read_only=True)
def get_all_users(self, in_dto: GetAllUsersInDto) -> GetAllUsersOutDto:
    # 読み取り専用トランザクション
    users = self.user_repository.get_all_users()
    return GetAllUsersOutDto(users=users)
```

### カスタムロールバック制御
```python
@Transactional(
    database=DatabaseType.TEST1,
    rollback_for=(ValueError, TypeError),
    no_rollback_for=(KeyError,)
)
def process_data(self, in_dto: ProcessDataInDto) -> ProcessDataOutDto:
    # ValueError, TypeError: ロールバック
    # KeyError: コミット（ロールバックしない）
    pass
```

## テスト戦略

### ユニットテスト

#### テストケース一覧
1. **正常系**:
   - メソッド成功時に自動コミット
   - セッションが確実にクローズされる
2. **異常系**:
   - 例外発生時に自動ロールバック
   - セッションが確実にクローズされる（finally）
3. **ロールバック制御**:
   - rollback_forで指定した例外でロールバック
   - no_rollback_forで指定した例外でコミット
4. **読み取り専用**:
   - read_only=Trueの動作確認
5. **データベース指定**:
   - TEST1/TEST2の切り替え

### テストダブル
- モック: セッション、リポジトリ
- スパイ: commit/rollback/close呼び出しの検証

## 移行計画

### フェーズ1: Transactionalデコレーター実装
- transactional.py作成
- ユニットテスト作成

### フェーズ2: 既存コードへの適用（サンプル）
- 1つのサービスクラスでTransactionalを試験的に使用
- 既存テストがすべてパスすることを確認

### フェーズ3: ドキュメント更新
- CLAUDE.md更新
- README.md更新

### フェーズ4: 今後の展開（Issue #15の範囲外）
- 段階的に他のサービスクラスへ適用
- SessionManagerからの移行検討

## 制約事項

### 現在のバージョンでの制約
1. **トランザクション伝播未対応**:
   - 既存トランザクションへの参加/新規作成の制御は未実装
   - 将来的な拡張として検討
2. **ネストしたトランザクション未対応**:
   - セーブポイントを使用したネストトランザクションは未実装
3. **タイムアウト制御未対応**:
   - トランザクションタイムアウトの設定は未実装

## 参考資料

### Spring Framework @Transactional
- Context7調査結果（2025-10-05実施）
- Spring Bootのトランザクション管理メカニズム
- AOPプロキシとTransactionInterceptor

### SQLAlchemy
- セッション管理ベストプラクティス
- トランザクション境界の制御
- コネクションプール管理
