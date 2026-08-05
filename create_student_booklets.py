#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生徒ごとの個別教材冊子を作成するスクリプト
"""

import os
import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter

REPO_DIR = Path(__file__).parent
TASKS_FILE = REPO_DIR / "all_students_tasks_extended.md"
INAMI_FILE = REPO_DIR / "inami_ishin_tasks.md"
MATERIALS_DIR = REPO_DIR / "teaching_materials"
BOOKLETS_OUTPUT_DIR = REPO_DIR / "student_booklets"
MAPPING_FILE = REPO_DIR / "teaching_materials_mapping.txt"

# 出力ディレクトリを作成
BOOKLETS_OUTPUT_DIR.mkdir(exist_ok=True)

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

def extract_student_materials(content, student_name):
    """
    生徒セクションから教材情報を抽出
    """
    # 生徒セクションを取得
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

def create_material_mapping():
    """
    各PDFファイルに含まれる教材情報をマッピング（手動作成）
    実際には以下のような情報が必要：
    {
        'material_name': {
            'pdf_file': 'filename.pdf',
            'pages': [(start, end), ...],
            'subjects': ['Japanese', 'Math', 'English']
        }
    }
    """
    # ここで手動でPDFファイルを教材にマッピング
    # 実装には、各PDFの内容を確認して適切にマッピングする必要があります

    mapping = {
        # Example structure - to be filled based on actual PDF contents
        # 'Material Name': {
        #     'pdf_file': 'teaching_materials/filename.pdf',
        #     'start_page': 1,
        #     'end_page': 10
        # }
    }
    return mapping

def get_available_pdfs():
    """
    利用可能なPDFファイルのリストを取得
    """
    if not MATERIALS_DIR.exists():
        return []

    pdfs = sorted(MATERIALS_DIR.glob('*.pdf'))
    return pdfs

def create_student_mapping_document():
    """
    各生徒の必要教材をマッピングドキュメントとして作成
    """
    print("=" * 70)
    print("生徒ごとの必要教材マッピング")
    print("=" * 70)

    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    for i, (student_name, school) in enumerate(STUDENTS, 1):
        materials = extract_student_materials(content, student_name)

        if not materials:
            print(f"\n[{i:2d}] {student_name}（{school}）")
            print("    教材情報が見つかりません")
            continue

        print(f"\n[{i:2d}] {student_name}（{school}）")
        print(f"    必要な教材: {len(materials)}種類")

        for j, mat in enumerate(materials, 1):
            print(f"      {j}. {mat['name']}")
            print(f"         ページ: {mat['page_info']}")

    # 稲見維真
    print("\n" + "-" * 70)
    print("[14] 稲見維真（特別対応）")

    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        inami_content = f.read()

    inami_materials = extract_student_materials(inami_content, "稲見維真")
    if inami_materials:
        print(f"    必要な教材: {len(inami_materials)}種類")
        for j, mat in enumerate(inami_materials, 1):
            print(f"      {j}. {mat['name']}")
            print(f"         ページ: {mat['page_info']}")

    # 利用可能なPDFを表示
    print("\n" + "=" * 70)
    print("利用可能なPDFファイル")
    print("=" * 70)

    pdfs = get_available_pdfs()
    print(f"\n合計: {len(pdfs)}個のPDFファイル\n")

    for i, pdf in enumerate(pdfs, 1):
        try:
            reader = PdfReader(str(pdf))
            page_count = len(reader.pages)
            print(f"  [{i:2d}] {pdf.name}")
            print(f"        ページ数: {page_count}, サイズ: {pdf.stat().st_size / 1024 / 1024:.1f}MB")
        except Exception as e:
            print(f"  [{i:2d}] {pdf.name}")
            print(f"        読み込みエラー: {str(e)[:50]}")

def main():
    # マッピングドキュメントを作成
    create_student_mapping_document()

    print("\n" + "=" * 70)
    print("次のステップ:")
    print("=" * 70)
    print("""
1. 各PDFファイルの内容を確認
2. 教材名とPDFファイルのマッピングを作成
3. 各生徒のページ抽出指定を作成
4. ページ抽出スクリプトを実行
5. 生徒ごとの個別冊子を生成
    """)

if __name__ == "__main__":
    main()
