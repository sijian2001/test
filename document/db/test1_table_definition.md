# test1データベース テーブル定義書

## 概要
test1データベースは、ユーザー管理システムのデータを格納するデータベースです。

## データベース接続情報
- **データベース名**: test1
- **ユーザー**: user1
- **ホスト**: localhost
- **ポート**: 3306

## テーブル一覧

### 1. userテーブル（ユーザー）

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|----------|----|----|-------------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | - | ユーザーID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | - | ユーザー名 |
| email | VARCHAR(100) | NOT NULL, UNIQUE | - | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | - | パスワードハッシュ |
| first_name | VARCHAR(50) | - | - | 名 |
| last_name | VARCHAR(50) | - | - | 姓 |
| department_id | INTEGER | - | - | 部署ID |
| created_at | TIMESTAMP | - | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | - | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |
| is_active | BOOLEAN | - | TRUE | アクティブフラグ |

**制約**
- PRIMARY KEY: id
- UNIQUE: username, email

### 2. departmentテーブル（部署）

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|----------|----|----|-------------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | - | 部署ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | - | 部署名 |
| description | TEXT | - | - | 部署説明 |
| manager_id | INTEGER | - | - | 部署マネージャーID |
| created_at | TIMESTAMP | - | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | - | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |
| is_active | BOOLEAN | - | TRUE | アクティブフラグ |

**制約**
- PRIMARY KEY: id
- UNIQUE: name

## ビュー一覧

### 1. user_infoビュー（ユーザー情報）

ユーザーと部署を結合したビューです。

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

| カラム名 | 型 | 説明 |
|----------|----|----|
| user_id | INTEGER | ユーザーID |
| username | VARCHAR(50) | ユーザー名 |
| email | VARCHAR(100) | メールアドレス |
| first_name | VARCHAR(50) | 名 |
| last_name | VARCHAR(50) | 姓 |
| department_name | VARCHAR(100) | 部署名 |
| manager_id | INTEGER | マネージャーID |
| is_active | BOOLEAN | アクティブフラグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## テーブル関係

```
department (1) ←→ (N) user
```

- departmentテーブルとuserテーブルは1対多の関係
- userテーブルのdepartment_idがdepartmentテーブルのidを参照
- departmentテーブルのmanager_idはuserテーブルのidを参照（自己参照）

## 注意事項

- パスワードはハッシュ化して保存される
- 論理削除はis_activeフラグで管理
- 日時項目は自動でタイムスタンプが設定される