# test2データベース テーブル定義書

## 概要
test2データベースは、商品管理システムのデータを格納するデータベースです。

## データベース接続情報
- **データベース名**: test2
- **ユーザー**: user2
- **ホスト**: localhost
- **ポート**: 3306

## テーブル一覧

### 1. categoriesテーブル（カテゴリ）

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|----------|----|----|-------------|------|
| category_id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | - | カテゴリID |
| category_name | VARCHAR(255) | NOT NULL, UNIQUE | - | カテゴリ名 |
| category_description | TEXT | - | - | カテゴリ説明 |
| parent_category_id | INTEGER | FOREIGN KEY | - | 親カテゴリID |
| created_at | TIMESTAMP | - | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | - | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

**制約**
- PRIMARY KEY: category_id
- UNIQUE: category_name
- FOREIGN KEY: parent_category_id REFERENCES categories(category_id)

### 2. productsテーブル（商品）

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|----------|----|----|-------------|------|
| product_id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | - | 商品ID |
| product_name | VARCHAR(255) | NOT NULL | - | 商品名 |
| description | TEXT | - | - | 商品説明 |
| price | DECIMAL(10, 2) | NOT NULL | - | 価格 |
| stock_quantity | INTEGER | NOT NULL | 0 | 在庫数量 |
| category_id | INTEGER | FOREIGN KEY | - | カテゴリID |
| created_at | TIMESTAMP | - | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | - | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

**制約**
- PRIMARY KEY: product_id
- FOREIGN KEY: category_id REFERENCES categories(category_id)

## ビュー一覧

### 1. product_infoビュー（商品情報）

商品とカテゴリを結合したビューです。

```sql
CREATE VIEW product_info AS
SELECT
    p.product_id,
    p.product_name,
    p.description,
    p.price,
    p.stock_quantity,
    c.category_name,
    p.created_at,
    p.updated_at
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id;
```

| カラム名 | 型 | 説明 |
|----------|----|----|
| product_id | INTEGER | 商品ID |
| product_name | VARCHAR(255) | 商品名 |
| description | TEXT | 商品説明 |
| price | DECIMAL(10, 2) | 価格 |
| stock_quantity | INTEGER | 在庫数量 |
| category_name | VARCHAR(255) | カテゴリ名 |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## テーブル関係

```
categories (1) ←→ (N) products
categories (1) ←→ (N) categories (自己参照)
```

- categoriesテーブルとproductsテーブルは1対多の関係
- productsテーブルのcategory_idがcategoriesテーブルのcategory_idを参照
- categoriesテーブルは階層構造をサポート（parent_category_idによる自己参照）

## 注意事項

- 価格はDECIMAL(10, 2)で小数点以下2桁まで対応
- 在庫数量はデフォルト値0
- カテゴリは階層構造をサポート
- 日時項目は自動でタイムスタンプが設定される