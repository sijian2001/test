#!/usr/bin/env python3
"""
循環importチェックスクリプト

このスクリプトは、プロジェクト内の循環importを検出します。
特にアーキテクチャ違反（例: domain層からbusiness層への依存）をチェックします。

使用方法:
    python scripts/check_circular_imports.py

前提条件:
    pip install pydeps
"""

import os
import sys
import subprocess
from pathlib import Path


def check_circular_imports():
    """循環importをチェックする"""
    print("循環importをチェックしています...")

    # プロジェクトルートディレクトリ
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # pydepsを使用して循環importをチェック
    try:
        result = subprocess.run(
            ["pydeps", "app", "--max-bacon=2", "--cluster", "--show-cycles"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print("エラー: pydepsの実行に失敗しました")
            print(result.stderr)
            return False

        # 循環が検出されたかチェック
        if "Cycle" in result.stdout or "cycle" in result.stdout:
            print("[WARNING] 循環importが検出されました:")
            print(result.stdout)
            return False
        else:
            print("[OK] 循環importは検出されませんでした")
            return True

    except FileNotFoundError:
        print("[INFO] pydepsがインストールされていません")
        print("       pydepsによる循環importチェックをスキップします")
        print("       インストール方法: pip install pydeps")
        return True  # pydepsなしでも続行
    except subprocess.TimeoutExpired:
        print("[ERROR] pydepsの実行がタイムアウトしました")
        return False


def check_architecture_violations():
    """アーキテクチャ違反をチェックする"""
    print("\nアーキテクチャ違反をチェックしています...")

    violations = []

    # domain層からbusiness層への依存をチェック
    domain_path = Path("app/domain")
    if domain_path.exists():
        for py_file in domain_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # business層へのimportをチェック
            if "from app.business" in content or "import app.business" in content:
                violations.append(f"{py_file}: domain層からbusiness層への依存が検出されました")

    # domain層からbatch層への依存をチェック
    if domain_path.exists():
        for py_file in domain_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # batch層へのimportをチェック
            if "from app.batch" in content or "import app.batch" in content:
                violations.append(f"{py_file}: domain層からbatch層への依存が検出されました")

    if violations:
        print("[WARNING] アーキテクチャ違反が検出されました:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print("[OK] アーキテクチャ違反は検出されませんでした")
        return True


def main():
    """メイン処理"""
    print("=" * 60)
    print("循環import & アーキテクチャチェック")
    print("=" * 60)

    # 循環importチェック
    circular_ok = check_circular_imports()

    # アーキテクチャチェック
    arch_ok = check_architecture_violations()

    print("\n" + "=" * 60)
    if circular_ok and arch_ok:
        print("[SUCCESS] すべてのチェックが正常に完了しました")
        return 0
    else:
        print("[FAILED] チェックに失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
