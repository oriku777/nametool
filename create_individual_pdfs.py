#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
各生徒ごとの個別課題PDFを生成するスクリプト
"""

import re
import subprocess
import os
from pathlib import Path

# ファイルの場所
REPO_DIR = Path(__file__).parent
PART1_FILE = REPO_DIR / "all_students_tasks_part1.md"
INAMI_FILE = REPO_DIR / "inami_ishin_tasks.md"
PDF_OUTPUT_DIR = REPO_DIR / "student_pdfs"

# 出力ディレクトリを作成
PDF_OUTPUT_DIR.mkdir(exist_ok=True)

# 北辰受験者の生徒名リスト（part1から順に）
HOKUSIN_STUDENTS = [
    "陳一嘉（富士見台）",
    "小暮理奈葉（勝瀬）",
    "井上結寿（勝瀬）",
    "濱尾紗那（勝瀬）",
    "渡邉裕莉（勝瀬）",
    "大和田悠月（勝瀬）",
    "田野史陽（富士見台）",
    "富樫菜々美（富士見東）",
    "斉藤栞（勝瀬）",
    "榎本大雅（富士見台）",
    "吉田蒼（富士見台）",
    "紫関啓文（富士見東）",
    "浦部莉乃（勝瀬）",
]

def extract_student_section(content, student_name):
    """
    Markdownコンテンツから特定の生徒のセクションを抽出
    """
    # 生徒名を含むセクションを探す
    pattern = rf"##\s*【{re.escape(student_name)}】.*?(?=##\s*【|$)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        section = match.group(0)
        # 最後の---を削除
        section = re.sub(r'\n---\s*$', '', section)
        return section
    return None

def create_individual_pdf_from_part1():
    """
    part1から各生徒のセクションを抽出してPDFを作成
    """
    print("📖 all_students_tasks_part1.md から生徒ごとのPDFを生成中...")

    with open(PART1_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # ファイルの先頭にあるメタデータを取得
    header_match = re.match(r'(#.*?\n\n.*?\n\n---)', content, re.DOTALL)
    header = header_match.group(0) if header_match else ""

    for i, student_name in enumerate(HOKUSIN_STUDENTS, 1):
        print(f"  [{i:2d}/13] {student_name}...", end="", flush=True)

        # 生徒セクションを抽出
        section = extract_student_section(content, student_name)

        if not section:
            print(" ❌ セクション見つかりません")
            continue

        # 新しいMarkdownを作成
        md_content = f"""{header}

{section}

---

**作成日：2026年8月5日**
**このファイルは個人用の弱点補強課題です。**
"""

        # 临时ファイルを保存
        temp_md = PDF_OUTPUT_DIR / f"temp_{i:02d}_{student_name.split('（')[0]}.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # PDFに変換
        pdf_filename = f"{i:02d}_{student_name.split('（')[0]}.pdf"
        pdf_path = PDF_OUTPUT_DIR / pdf_filename

        try:
            # pandocでPDFに変換（日本語対応）
            cmd = [
                'pandoc',
                str(temp_md),
                '-o', str(pdf_path),
                '--pdf-engine=wkhtmltopdf',
                '-V', 'geometry:margin=1in',
                '-V', 'fontsize=10pt',
                '--toc',
                '--toc-depth=2',
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                # wkhtmltopdfが失敗した場合、xelatexを試す
                cmd = [
                    'pandoc',
                    str(temp_md),
                    '-o', str(pdf_path),
                    '--pdf-engine=xelatex',
                    '-V', 'geometry:margin=1in',
                    '-V', 'fontsize=10pt',
                    '--toc',
                    '--toc-depth=2',
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f" ✅ {pdf_filename}")
            else:
                print(f" ⚠️  変換エラー: {result.stderr[:100]}")
        except Exception as e:
            print(f" ❌ {str(e)[:50]}")
        finally:
            # 临时ファイルを削除
            temp_md.unlink(missing_ok=True)

def create_inami_pdf():
    """
    稲見維真のPDFを作成
    """
    print("\n📖 inami_ishin_tasks.md からPDFを生成中...")

    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    temp_md = PDF_OUTPUT_DIR / "temp_inami.md"
    with open(temp_md, 'w', encoding='utf-8') as f:
        f.write(content)

    pdf_path = PDF_OUTPUT_DIR / "14_稲見維真.pdf"

    try:
        cmd = [
            'pandoc',
            str(temp_md),
            '-o', str(pdf_path),
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=1in',
            '-V', 'fontsize=10pt',
            '--toc',
            '--toc-depth=2',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  [14/14] 稲見維真 ✅ 14_稲見維真.pdf")
        else:
            print(f"  [14/14] 稲見維真 ❌ エラー: {result.stderr[:100]}")
    except Exception as e:
        print(f"  [14/14] 稲見維真 ❌ {str(e)[:50]}")
    finally:
        temp_md.unlink(missing_ok=True)

def main():
    print("=" * 60)
    print("中3弱点補強課題 - 個別PDF生成ツール")
    print("=" * 60 + "\n")

    create_individual_pdf_from_part1()
    create_inami_pdf()

    # 結果を表示
    pdf_files = sorted(PDF_OUTPUT_DIR.glob("*.pdf"))
    print("\n" + "=" * 60)
    print(f"✅ 完成しました！")
    print(f"📁 出力ディレクトリ: {PDF_OUTPUT_DIR}")
    print(f"📊 作成されたPDFファイル: {len(pdf_files)}個")
    print("=" * 60)

    for pdf in pdf_files:
        size_kb = pdf.stat().st_size / 1024
        print(f"  • {pdf.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
