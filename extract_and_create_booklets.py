#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生徒別教材冊子生成スクリプト

各生徒に必要な教材をPDFから抽出し、
生徒ごとの個別冊子を生成します。

実行前に以下が必要：
- material_pdf_mapping.json（教材 ↔ PDF マッピング）
- student_materials_mapping.json（生徒別教材リスト）
"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict

REPO_DIR = Path(__file__).parent
MAPPING_FILE = REPO_DIR / "material_pdf_mapping.json"
STUDENT_MATERIALS_FILE = REPO_DIR / "student_materials_mapping.json"
OUTPUT_DIR = REPO_DIR / "student_booklets"
TEMP_DIR = REPO_DIR / ".temp_booklets"


def load_json(filepath):
    """JSONファイルを読み込む"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSONファイルのフォーマットエラー: {e}")
        return None


def check_prerequisites():
    """実行に必要なファイルとツールを確認"""
    print("=" * 70)
    print("前提条件の確認")
    print("=" * 70)

    errors = []

    # ファイル確認
    if not MAPPING_FILE.exists():
        errors.append(f"❌ {MAPPING_FILE.name} が見つかりません")
    else:
        print(f"✅ {MAPPING_FILE.name} 確認")

    if not STUDENT_MATERIALS_FILE.exists():
        errors.append(f"❌ {STUDENT_MATERIALS_FILE.name} が見つかりません")
    else:
        print(f"✅ {STUDENT_MATERIALS_FILE.name} 確認")

    # ツール確認
    tools = ["pdfseparate", "pdfunite"]
    for tool in tools:
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ {tool} 確認")
        else:
            errors.append(f"❌ {tool} がインストールされていません（poppler-utils が必要）")

    if errors:
        print("\n⚠️ 以下の問題があります:\n")
        for error in errors:
            print(f"  {error}")
        return False

    print("\n✅ すべての前提条件を満たしています\n")
    return True


def extract_material_pages(pdf_path, start_page, end_page, output_pdf):
    """
    PDFの指定ページを抽出
    """
    try:
        # PDFから指定ページを抽出
        result = subprocess.run(
            [
                "pdfseparate",
                "-f", str(start_page),
                "-l", str(end_page),
                str(pdf_path),
                str(output_pdf.parent / (output_pdf.stem + "_%d.pdf"))
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True
        else:
            print(f"  ⚠️ ページ抽出エラー: {pdf_path.name}")
            return False

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return False


def merge_pdfs(pdf_list, output_pdf):
    """
    複数のPDFを1つのPDFに統合
    """
    try:
        cmd = ["pdfunite"] + [str(p) for p in pdf_list] + [str(output_pdf)]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return True
        else:
            print(f"  ⚠️ PDF統合エラー: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return False


def create_student_booklet(student_name, materials_list, mapping_data):
    """
    生徒の個別冊子を作成
    """
    print(f"\n📚 {student_name} の冊子を生成中...")

    # 出力ディレクトリ作成
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 抽出するPDFページを収集
    pages_to_merge = []
    materials_found = 0
    materials_missing = []

    for material in materials_list:
        material_name = material["name"]

        # マッピング情報を確認
        if material_name not in mapping_data:
            materials_missing.append(material_name)
            continue

        mapping = mapping_data[material_name]
        pdf_file = mapping.get("pdf_file")
        start_page = mapping.get("start_page")
        end_page = mapping.get("end_page")

        if not pdf_file or start_page == 0 or end_page == 0:
            print(f"  ⚠️ 不完全なマッピング: {material_name}")
            materials_missing.append(material_name)
            continue

        pdf_path = REPO_DIR / pdf_file

        if not pdf_path.exists():
            print(f"  ⚠️ PDFが見つかりません: {pdf_file}")
            materials_missing.append(material_name)
            continue

        # ページを抽出
        temp_pdf = TEMP_DIR / f"{materials_found:02d}_{material_name.replace('/', '_')}.pdf"

        if extract_material_pages(pdf_path, start_page, end_page, temp_pdf):
            pages_to_merge.append(temp_pdf)
            materials_found += 1
            print(f"  ✅ {material_name} (P.{start_page}-{end_page})")
        else:
            materials_missing.append(material_name)

    # 統計
    print(f"\n  統計:")
    print(f"    - 見つかった教材: {materials_found}/{len(materials_list)}")

    if materials_missing:
        print(f"    - 見つからない教材: {len(materials_missing)}")
        for name in materials_missing[:5]:  # 最初の5個のみ表示
            print(f"      • {name}")
        if len(materials_missing) > 5:
            print(f"      ... 他 {len(materials_missing) - 5} 個")

    # 冊子を生成
    if pages_to_merge:
        output_pdf = OUTPUT_DIR / f"{student_name}_教材冊子.pdf"

        if merge_pdfs(pages_to_merge, output_pdf):
            print(f"\n  ✅ 冊子生成完了: {output_pdf.name}")
            return True
        else:
            print(f"\n  ❌ 冊子生成失敗")
            return False
    else:
        print(f"\n  ❌ 教材が見つかりません")
        return False


def cleanup():
    """一時ファイルを削除"""
    try:
        import shutil
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
    except Exception as e:
        print(f"⚠️ 一時ファイル削除エラー: {e}")


def main():
    """メイン処理"""
    print("\n" + "=" * 70)
    print("生徒別教材冊子生成ツール")
    print("=" * 70 + "\n")

    # 前提条件確認
    if not check_prerequisites():
        return

    # ファイル読み込み
    mapping_data = load_json(MAPPING_FILE)
    student_materials_data = load_json(STUDENT_MATERIALS_FILE)

    if not mapping_data or not student_materials_data:
        return

    # マッピング情報が完全か確認
    incomplete_mappings = 0
    for material, info in mapping_data.items():
        if not info.get("pdf_file") or info.get("start_page", 0) == 0 or info.get("end_page", 0) == 0:
            incomplete_mappings += 1

    if incomplete_mappings > 0:
        print(f"⚠️ 警告: {incomplete_mappings}個の教材にマッピング情報が不完全です")
        print("以下のコマンドで確認してください:")
        print(f"  grep -E '\"start_page\": 0|\"end_page\": 0' {MAPPING_FILE.name}\n")

    # 生徒ごとの冊子を生成
    print("=" * 70)
    print("冊子生成処理開始")
    print("=" * 70)

    generated_count = 0
    failed_count = 0

    for student_name, materials in student_materials_data.items():
        # 学生名から番号を取得（例：陳一嘉（富士見台）→ 陳一嘉）
        display_name = student_name.split("（")[0] if "（" in student_name else student_name

        if create_student_booklet(display_name, materials, mapping_data):
            generated_count += 1
        else:
            failed_count += 1

    # 結果サマリー
    print("\n" + "=" * 70)
    print("生成完了サマリー")
    print("=" * 70)
    print(f"\n生成成功: {generated_count}個")
    print(f"生成失敗: {failed_count}個")
    print(f"合計: {generated_count + failed_count}個\n")

    if generated_count > 0:
        print(f"✅ 冊子ファイルは以下に保存されています:")
        print(f"  {OUTPUT_DIR}/\n")

        # 生成されたファイル一覧
        booklets = sorted(OUTPUT_DIR.glob("*_教材冊子.pdf"))
        for i, booklet in enumerate(booklets, 1):
            size_mb = booklet.stat().st_size / (1024 * 1024)
            print(f"  {i:2d}. {booklet.name} ({size_mb:.1f}MB)")

    # 一時ファイル削除
    cleanup()

    print("\n" + "=" * 70)
    print("処理完了")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
