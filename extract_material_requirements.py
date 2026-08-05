#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タスク定義から、生徒ごとの必要な教材ページ情報を抽出
"""

import re
from pathlib import Path
from collections import defaultdict

REPO_DIR = Path(__file__).parent
TASKS_FILE = REPO_DIR / "all_students_tasks_extended.md"
INAMI_FILE = REPO_DIR / "inami_ishin_tasks.md"

def extract_material_requirements(content):
    """
    タスクファイルから生徒ごとの教材要件を抽出
    """
    # 生徒セクションを分割
    student_pattern = r'^## 【([^】]+)】$'
    requirements = {}

    # ファイル全体を行ごとに処理
    lines = content.split('\n')
    current_student = None
    materials = []

    for i, line in enumerate(lines):
        # 生徒名の検出
        match = re.match(student_pattern, line)
        if match:
            if current_student and materials:
                requirements[current_student] = materials
            current_student = match.group(1)
            materials = []

        # 教材名の検出
        if line.startswith('- 教材名：'):
            material_name = line.replace('- 教材名：', '').strip()
            # 次の行でページ情報を探す
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].startswith('- ページ/問題形式：'):
                    page_info = lines[j].replace('- ページ/問題形式：', '').strip()
                    materials.append({
                        'name': material_name,
                        'page_info': page_info
                    })
                    break

    # 最後の生徒を追加
    if current_student and materials:
        requirements[current_student] = materials

    return requirements

def print_requirements(requirements, title=""):
    """
    抽出した要件を見やすく表示
    """
    if title:
        print(f"\n{title}")

    for student, materials in sorted(requirements.items()):
        print(f"\n【{student}】")
        for i, mat in enumerate(materials, 1):
            print(f"  {i}. {mat['name']}")
            print(f"     → {mat['page_info']}")

def main():
    print("=" * 70)
    print("生徒ごとの教材ページ要件抽出")
    print("=" * 70)

    # タスクファイルを読み込み
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 要件を抽出
    requirements = extract_material_requirements(content)

    # 表示
    print_requirements(requirements)

    # 稲見維真の要件も読み込み
    print("\n" + "=" * 70)
    print("稲見維真（特別対応）")
    print("=" * 70)

    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        inami_content = f.read()

    inami_requirements = extract_material_requirements(inami_content)
    print_requirements(inami_requirements)

    # サマリーを作成
    print("\n" + "=" * 70)
    print("必要な教材一覧（ユニーク）")
    print("=" * 70)

    all_materials = {}
    for materials in list(requirements.values()) + list(inami_requirements.values()):
        for mat in materials:
            mat_name = mat['name']
            if mat_name not in all_materials:
                all_materials[mat_name] = []
            all_materials[mat_name].append(mat['page_info'])

    for mat in sorted(all_materials.keys()):
        print(f"\n• {mat}")
        for page_info in set(all_materials[mat]):
            print(f"  → {page_info}")

    print(f"\n\n合計: {len(all_materials)}種類の教材が必要")

if __name__ == "__main__":
    main()
