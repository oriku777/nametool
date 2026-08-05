#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全生徒の教材マッピング抽出スクリプト
"""

import re
import json
from pathlib import Path
from collections import defaultdict

REPO_DIR = Path(__file__).parent
PART1_FILE = REPO_DIR / "all_students_tasks_part1.md"
EXTENDED_FILE = REPO_DIR / "all_students_tasks_extended.md"
INAMI_FILE = REPO_DIR / "inami_ishin_tasks.md"

# 生徒リスト (name, school, source_file)
STUDENTS = [
    ("陳一嘉", "富士見台", "part1"),
    ("小暮理奈葉", "勝瀬", "part1"),
    ("井上結寿", "勝瀬", "part1"),
    ("濱尾紗那", "勝瀬", "extended"),
    ("渡邉裕莉", "勝瀬", "extended"),
    ("大和田悠月", "勝瀬", "extended"),
    ("田野史陽", "富士見台", "extended"),
    ("富樫菜々美", "富士見東", "extended"),
    ("斉藤栞", "勝瀬", "extended"),
    ("榎本大雅", "富士見台", "extended"),
    ("吉田蒼", "富士見台", "extended"),
    ("紫関啓文", "富士見東", "extended"),
    ("浦部莉乃", "勝瀬", "extended"),
]

def extract_student_materials(content, student_name, school):
    """
    生徒セクションから教材情報を抽出
    """
    # Fix: Use \n## 【 to ensure line start matching
    pattern = rf'## 【{re.escape(student_name)}（{re.escape(school)}）】\n.*?(?=\n## 【|$)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    section = match.group(0)
    materials = []

    # Extract materials
    material_pattern = r'- 教材名：([^\n]+)\n.*?- ページ/問題形式：([^\n]+)'

    for mat_match in re.finditer(material_pattern, section, re.DOTALL):
        material_name = mat_match.group(1).strip()
        page_info = mat_match.group(2).strip()
        materials.append({
            'name': material_name,
            'page_info': page_info
        })

    return materials if materials else None

def main():
    print("=" * 70)
    print("全生徒教材マッピング抽出")
    print("=" * 70)

    # Load files
    with open(PART1_FILE, 'r', encoding='utf-8') as f:
        part1_content = f.read()

    with open(EXTENDED_FILE, 'r', encoding='utf-8') as f:
        extended_content = f.read()

    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        inami_content = f.read()

    # Build student materials mapping
    student_materials = {}

    print("\n【北辰テスト受験生12名】\n")

    for student_name, school, source_file in STUDENTS:
        content = part1_content if source_file == "part1" else extended_content

        materials = extract_student_materials(content, student_name, school)

        if materials:
            student_id = f"{student_name}（{school}）"
            student_materials[student_id] = materials
            print(f"✅ {student_name}（{school}）: {len(materials)}種類の教材")
        else:
            print(f"❌ {student_name}（{school}）: 教材情報が見つかりません")

    # Extract inami materials
    print("\n【稲見維真（定期テスト対応）】\n")

    pattern = r'## 【稲見維真[^】]*】\n.*?(?=\n## 【|$)'
    match = re.search(pattern, inami_content, re.DOTALL)

    if match:
        section = match.group(0)
        materials = []
        material_pattern = r'- 教材名：([^\n]+)\n.*?- ページ/問題形式：([^\n]+)'

        for mat_match in re.finditer(material_pattern, section, re.DOTALL):
            material_name = mat_match.group(1).strip()
            page_info = mat_match.group(2).strip()
            materials.append({'name': material_name, 'page_info': page_info})

        if materials:
            student_materials["稲見維真"] = materials
            print(f"✅ 稲見維真: {len(materials)}種類の教材")

    # Generate unique materials list
    print("\n" + "=" * 70)
    print("必要な教材一覧（ユニーク）")
    print("=" * 70 + "\n")

    all_materials = {}
    for student, materials in student_materials.items():
        for mat in materials:
            mat_name = mat['name']
            if mat_name not in all_materials:
                all_materials[mat_name] = {
                    'students': [],
                    'page_ranges': []
                }
            if student not in all_materials[mat_name]['students']:
                all_materials[mat_name]['students'].append(student)
            if mat['page_info'] not in all_materials[mat_name]['page_ranges']:
                all_materials[mat_name]['page_ranges'].append(mat['page_info'])

    # Create mapping template
    mapping = {}
    for mat_name in sorted(all_materials.keys()):
        students_list = sorted(all_materials[mat_name]['students'])
        page_ranges = sorted(all_materials[mat_name]['page_ranges'])

        mapping[mat_name] = {
            'pdf_file': '',
            'start_page': 0,
            'end_page': 0,
            'needed_by': students_list,
            'page_ranges': page_ranges,
            'notes': ''
        }

        # Print
        print(f"📚 {mat_name}")
        print(f"   必要な生徒: {len(students_list)}")
        print(f"   ページ範囲: {page_ranges}")
        print()

    # Statistics
    print("=" * 70)
    print(f"統計情報")
    print("=" * 70)
    print(f"生徒数: {len(student_materials)}")
    print(f"ユニーク教材数: {len(mapping)}")
    print(f"\n本ステップでするべきこと:")
    print("1. 各PDFファイルの内容を確認")
    print("2. 教材名とPDFファイルのマッピングを作成")
    print("3. material_pdf_mapping.json を編集")
    print("4. extract_and_create_booklets.py を実行")

    # Save template
    output_file = REPO_DIR / "material_pdf_mapping_template.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n✅ テンプレート生成: {output_file}")

    # Also save the student-materials mapping
    student_mapping_file = REPO_DIR / "student_materials_mapping.json"
    student_mapping = {
        student: [
            {'name': m['name'], 'page_info': m['page_info']}
            for m in materials
        ]
        for student, materials in student_materials.items()
    }

    with open(student_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(student_mapping, f, ensure_ascii=False, indent=2)

    print(f"✅ 生徒マッピング保存: {student_mapping_file}")

if __name__ == "__main__":
    main()
