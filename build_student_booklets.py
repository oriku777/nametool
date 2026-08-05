#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生徒ごとの個別教材冊子を作成するスクリプト
pdfseparate と pdfunite を使用してページ抽出・結合を実行
"""

import os
import re
import subprocess
import json
from pathlib import Path
from collections import defaultdict

REPO_DIR = Path(__file__).parent
TASKS_FILE = REPO_DIR / "all_students_tasks_extended.md"
INAMI_FILE = REPO_DIR / "inami_ishin_tasks.md"
MATERIALS_DIR = REPO_DIR / "teaching_materials"
BOOKLETS_OUTPUT_DIR = REPO_DIR / "student_booklets"
TEMP_PAGES_DIR = REPO_DIR / ".temp_pages"
MATERIAL_MAPPING_FILE = REPO_DIR / "material_pdf_mapping.json"

# ディレクトリを作成
BOOKLETS_OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_PAGES_DIR.mkdir(exist_ok=True)

# 生徒リスト
STUDENTS = [
    ("陳一嘉", "富士見台"),
    ("小暮理奈葉", "勝瀬"),
    ("井上結寿", "勝瀬"),
    ("濱尾紗那", "勝瀬"),
    ("渡邉裕莉", "勝瀬"),
    ("大和田悠月", "勝瀬"),
    ("田野史陽", "富士見台"),
    ("富樫菜々美", "富士見東"),
    ("斉藤栞", "勝瀬"),
    ("榎本大雅", "富士見台"),
    ("吉田蒼", "富士見台"),
    ("紫関啓文", "富士見東"),
    ("浦部莉乃", "勝瀬"),
]

def get_pdf_page_count(pdf_path):
    """
    PDFのページ数を取得
    """
    try:
        result = subprocess.run(
            ['pdfinfo', str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    return int(line.split(':')[1].strip())
    except Exception as e:
        print(f"Error getting page count: {e}")
    return 0

def extract_student_materials(content, student_name, school=None):
    """
    生徒セクションから教材情報を抽出
    """
    # 学校名がある場合はそれを含めてマッチ
    if school:
        pattern = rf'## 【{re.escape(student_name)}（{re.escape(school)}）】.*?(?=## 【|$)'
    else:
        # 学校名がない場合は、括弧内の任意のテキストを許可
        pattern = rf'## 【{re.escape(student_name)}[^】]*】.*?(?=## 【|$)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    section = match.group(0)
    materials = []

    # 教材名とページを抽出
    material_pattern = r'- 教材名：([^\n]+)\n.*?- ページ/問題形式：([^\n]+)'

    for mat_match in re.finditer(material_pattern, section, re.DOTALL):
        material_name = mat_match.group(1).strip()
        page_info = mat_match.group(2).strip()
        materials.append({
            'name': material_name,
            'page_info': page_info
        })

    return materials

def list_available_materials():
    """
    利用可能な教材（PDFファイル）をリスト
    """
    print("\n" + "=" * 70)
    print("利用可能なPDFファイル")
    print("=" * 70)

    if not MATERIALS_DIR.exists():
        print("教材ディレクトリが見つかりません")
        return []

    pdfs = sorted(MATERIALS_DIR.glob('*.pdf'))

    print(f"\n合計: {len(pdfs)}個のPDFファイル\n")

    for i, pdf in enumerate(pdfs, 1):
        page_count = get_pdf_page_count(pdf)
        size_mb = pdf.stat().st_size / 1024 / 1024
        print(f"[{i:2d}] {pdf.name}")
        print(f"     ページ数: {page_count}p, サイズ: {size_mb:.1f}MB\n")

    return pdfs

def create_mapping_template():
    """
    教材からPDFへのマッピングテンプレートを作成
    """
    mapping = {}

    # Extract all unique materials
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    all_materials = set()
    for name, _ in STUDENTS:
        materials = extract_student_materials(content, name)
        if materials:
            for mat in materials:
                all_materials.add(mat['name'])

    # With inami
    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        inami_content = f.read()

    materials = extract_student_materials(inami_content, "稲見維真")
    if materials:
        for mat in materials:
            all_materials.add(mat['name'])

    # Create template
    for material in sorted(all_materials):
        mapping[material] = {
            'pdf_file': '',  # e.g., 'teaching_materials/file.pdf'
            'start_page': 1,
            'end_page': 1,
            'notes': ''
        }

    return mapping

def create_material_mapping_guide():
    """
    マッピングガイドを表示して、ユーザーに教材とPDFの関係を確認させる
    """
    print("\n" + "=" * 70)
    print("教材別にPDFのマッピングを行う必要があります")
    print("=" * 70)

    print("""
例えば、以下のような対応関係を確認してください：

【北辰テスト対応読解教材 - 文学的文章編】
  ↓ どのPDFに含まれているか？
  → 例: teaching_materials/1e13943c-20260804222302260_part01_p0119.pdf

【古典読解テキスト「基礎から応用へ」】
  ↓ どのPDFに含まれているか？
  → 例: teaching_materials/0018affd-20260804224416182_part03_p4464.pdf

各教材がどのPDFファイルの何ページから何ページまでなのかを
把握する必要があります。

以下のステップを実行してください：

1. 各PDFファイルの内容を確認（pdftotext で確認できます）
2. 教材名とPDFのマッピングテーブルを作成
3. 各教材の開始ページと終了ページを指定
4. material_pdf_mapping.json に記録
5. build_student_booklets.py の generate_booklets() を実行
    """)

def print_student_material_requirements():
    """
    各生徒の必要教材をリスト
    """
    print("\n" + "=" * 70)
    print("生徒ごとの必要教材")
    print("=" * 70)

    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    for i, (student_name, school) in enumerate(STUDENTS, 1):
        materials = extract_student_materials(content, student_name, school)

        if not materials:
            print(f"\n[{i:2d}] {student_name}（{school}）")
            print("     教材情報が見つかりません")
            continue

        print(f"\n[{i:2d}] {student_name}（{school}）")
        print(f"     必要な教材: {len(materials)}種類")

        for j, mat in enumerate(materials, 1):
            print(f"       • {mat['name']}")

    # 稲見維真
    print("\n" + "-" * 70)
    print("[14] 稲見維真（特別対応）")

    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        inami_content = f.read()

    inami_materials = extract_student_materials(inami_content, "稲見維真")
    if inami_materials:
        print(f"     必要な教材: {len(inami_materials)}種類")
        for j, mat in enumerate(inami_materials, 1):
            print(f"       • {mat['name']}")

def check_mapping_file():
    """
    マッピングファイルが存在し、完全か確認
    """
    if not MATERIAL_MAPPING_FILE.exists():
        print("\n⚠️  material_pdf_mapping.json が見つかりません")
        print("   各教材とPDFのマッピングを定義する必要があります")
        return False

    try:
        with open(MATERIAL_MAPPING_FILE, 'r', encoding='utf-8') as f:
            mapping = json.load(f)

        incomplete = []
        for material, info in mapping.items():
            if not info.get('pdf_file') or not info.get('end_page'):
                incomplete.append(material)

        if incomplete:
            print(f"\n⚠️  {len(incomplete)}個の教材がマッピングされていません:")
            for mat in incomplete:
                print(f"   • {mat}")
            return False

        print(f"\n✅ マッピング完了: {len(mapping)}個の教材")
        return True

    except Exception as e:
        print(f"\n❌ マッピングファイルの読み込みエラー: {e}")
        return False

def main():
    print("=" * 70)
    print("生徒ごとの個別教材冊子生成システム")
    print("=" * 70)

    # PDFファイルを表示
    pdfs = list_available_materials()

    # 生徒の必要教材を表示
    print_student_material_requirements()

    # マッピングの状態を確認
    print("\n" + "=" * 70)
    print("マッピング状態確認")
    print("=" * 70)

    is_mapped = check_mapping_file()

    if not is_mapped:
        create_material_mapping_guide()

        # Template を作成（手動確認用）
        template = create_mapping_template()

        # output as JSON
        output_path = REPO_DIR / "material_pdf_mapping_template.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)

        print(f"\n作成されたテンプレート: {output_path}")
        print("このファイルを編集して、material_pdf_mapping.json として保存してください。")

if __name__ == "__main__":
    main()
