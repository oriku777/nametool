#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDFファイルの内容を分析して教材を特定するスクリプト
"""

import os
import subprocess
import re
from pathlib import Path

MATERIALS_DIR = Path(__file__).parent / "teaching_materials"

# 教材のキーワード（検索用）
MATERIAL_KEYWORDS = {
    '北辰テスト対応読解教材': ['北辰', '読解'],
    '古典読解テキスト': ['古典', '古文'],
    '漢字識別テキスト': ['漢字', '識別'],
    '説明的文章読解テキスト': ['説明文', '論説'],
    '敬語テキスト': ['敬語'],
    '敬語・文法テキスト': ['敬語', '文法'],
    '文法の基礎テキスト': ['文法', '品詞'],
    '校舎対抗バトル': ['バトル', '勉強'],
    '高校入試数学': ['高校入試', '数学'],
    '英語長文読解': ['長文', '読解'],
    '英文法': ['英文法', '文法'],
    '単語': ['単語', 'vocabulary'],
    'リスニング': ['リスニング', 'listening'],
    '確率': ['確率'],
    '方程式': ['方程式'],
}

def extract_pdf_text(pdf_path, num_pages=5):
    """
    PDFのテキストを抽出（最初のN ページ）
    """
    try:
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            lines = result.stdout.split('\n')
            # 最初の pages ページ分のテキストを抽出
            # Usually ~50 lines per page
            return '\n'.join(lines[:num_pages * 50])
        return ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def identify_material(pdf_path, text):
    """
    PDFのテキストから教材を特定
    """
    if not text:
        return []

    text_lower = text.lower()
    identified = []

    # Check file name
    filename = pdf_path.name.lower()

    # Try to match materials
    for material, keywords in MATERIAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower or keyword.lower() in filename:
                if material not in identified:
                    identified.append(material)
                break

    return identified

def main():
    print("=" * 70)
    print("PDFファイル内容分析")
    print("=" * 70)

    if not MATERIALS_DIR.exists():
        print(f"教材ディレクトリが見つかりません: {MATERIALS_DIR}")
        return

    pdfs = sorted(MATERIALS_DIR.glob("*.pdf"))

    print(f"\n分析対象: {len(pdfs)}個のPDFファイル\n")

    # Analyze each PDF
    pdf_materials = {}

    for i, pdf in enumerate(pdfs, 1):
        print(f"[{i:2d}/{len(pdfs)}] {pdf.name}")

        # Extract text
        text = extract_pdf_text(pdf, num_pages=3)

        # Identify materials
        materials = identify_material(pdf, text)

        if materials:
            print(f"     → {', '.join(materials)}")
            pdf_materials[pdf.name] = materials
        else:
            # Show first 200 chars of text for manual inspection
            print(f"     → [Unknown]")
            print(f"        First text: {text[:200]}")

        print()

    # Summary
    print("\n" + "=" * 70)
    print("サマリー")
    print("=" * 70 + "\n")

    for pdf_name, materials in pdf_materials.items():
        print(f"✅ {pdf_name}")
        for mat in materials:
            print(f"   • {mat}")

    # Files with no identified materials
    unknown_files = [p.name for p in pdfs if p.name not in pdf_materials]
    if unknown_files:
        print(f"\n⚠️  未特定のファイル ({len(unknown_files)}個):")
        for filename in unknown_files:
            print(f"   • {filename}")

    print(f"\n次のステップ:")
    print("1. 上記の分析結果を確認")
    print("2. 必要に応じて手動で material_pdf_mapping.json を編集")
    print("3. extract_and_create_booklets.py を実行")

if __name__ == "__main__":
    main()
