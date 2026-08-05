#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全13名の個別学生課題PDFを生成するスクリプト
"""

import re
import subprocess
import os
from pathlib import Path

REPO_DIR = Path(__file__).parent
PDF_OUTPUT_DIR = REPO_DIR / "student_pdfs"
EXTENDED_FILE = REPO_DIR / "all_students_tasks_extended.md"
INAMI_FILE = REPO_DIR / "inami_ishin_tasks.md"

# 出力ディレクトリを作成
PDF_OUTPUT_DIR.mkdir(exist_ok=True)

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

def extract_student_markdown(content, student_name):
    """
    Markdownコンテンツから特定の生徒のセクションを抽出
    """
    # 生徒名を含むセクションを探す（学校名は不要）
    pattern = rf"##\s*【{re.escape(student_name)}.*?】.*?(?=##\s*【|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        section = match.group(0)
        # 最後の---を削除
        section = re.sub(r'\n---\s*$', '', section)
        return section
    return None

def create_markdown_for_pdf(student_name, markdown_section):
    """
    PDFに適したMarkdownを作成
    """
    header = f"""# 中3弱点補強課題 - 個別課題

**対象生徒：{student_name}**
**作成日：2026年8月5日**

---

"""
    footer = """

---

**このファイルは個人用の弱点補強課題です。**
**北辰テスト対策として、指定された教材に基づいて学習してください。**
"""
    return header + markdown_section + footer

def convert_markdown_to_pdf(markdown_file, pdf_file, student_name):
    """
    MarkdownをPDFに変換
    複数のエンジンを試す
    """
    # 方法1: pandoc + wkhtmltopdf (HTML経由)
    temp_html = PDF_OUTPUT_DIR / f"temp_{student_name}.html"

    try:
        # MarkdownからHTMLに変換
        cmd1 = [
            'pandoc',
            str(markdown_file),
            '-o', str(temp_html),
            '--from', 'markdown',
            '--to', 'html',
            '--standalone',
            '--css', '/dev/null',
        ]
        result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=10)

        if result1.returncode != 0:
            return False

        # HTMLからPDFに変換
        cmd2 = [
            'wkhtmltopdf',
            '--quiet',
            '--margin-top', '15mm',
            '--margin-bottom', '15mm',
            '--margin-left', '15mm',
            '--margin-right', '15mm',
            '--encoding', 'UTF-8',
            str(temp_html),
            str(pdf_file),
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)

        if result2.returncode == 0:
            return True
        else:
            print(f"    wkhtmltopdf error: {result2.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    Timeout during conversion")
        return False
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        return False
    finally:
        # 临时HTMLファイルを削除
        temp_html.unlink(missing_ok=True)

def generate_pdfs_from_extended():
    """
    extended ファイルから各生徒のPDFを生成
    """
    print("📖 all_students_tasks_extended.md から生徒ごとのPDFを生成中...\n")

    with open(EXTENDED_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    for i, (student_name, school) in enumerate(STUDENTS, 1):
        print(f"  [{i:2d}/13] {student_name}（{school}）...", end="", flush=True)

        # 生徒セクションを抽出
        section = extract_student_markdown(content, student_name)

        if not section:
            print(f" ❌ セクション見つかりません")
            continue

        # PDF用のMarkdownを作成
        md_content = create_markdown_for_pdf(student_name, section)

        # 临时ファイルを保存
        temp_md = PDF_OUTPUT_DIR / f"temp_{i:02d}_{student_name}.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # PDFファイルパス
        pdf_filename = f"{i:02d}_{student_name}.pdf"
        pdf_path = PDF_OUTPUT_DIR / pdf_filename

        # PDFに変換
        if convert_markdown_to_pdf(temp_md, pdf_path, student_name):
            print(f" ✅")
        else:
            print(f" ⚠️  変換失敗")

        # 临时ファイルを削除
        temp_md.unlink(missing_ok=True)

def generate_inami_pdf():
    """
    稲見維真のPDFを生成
    """
    print("\n📖 inami_ishin_tasks.md からPDFを生成中...\n")

    with open(INAMI_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"  [14/14] 稲見維真...", end="", flush=True)

    # PDF用のMarkdownを作成
    md_content = content

    # 临时ファイルを保存
    temp_md = PDF_OUTPUT_DIR / "temp_14_inami.md"
    with open(temp_md, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # PDFファイルパス
    pdf_filename = "14_稲見維真.pdf"
    pdf_path = PDF_OUTPUT_DIR / pdf_filename

    # PDFに変換
    if convert_markdown_to_pdf(temp_md, pdf_path, "稲見維真"):
        print(f" ✅")
    else:
        print(f" ⚠️  変換失敗")

    # 临时ファイルを削除
    temp_md.unlink(missing_ok=True)

def main():
    print("=" * 60)
    print("中3弱点補強課題 - 個別PDF生成ツール")
    print("=" * 60 + "\n")

    # extended ファイルが存在するか確認
    if not EXTENDED_FILE.exists():
        print(f"❌ エラー: {EXTENDED_FILE} が見つかりません")
        print("   先に generate_remaining_tasks.py を実行してください")
        return

    generate_pdfs_from_extended()
    generate_inami_pdf()

    # 結果を表示
    pdf_files = sorted(PDF_OUTPUT_DIR.glob("*.pdf"))

    print("\n" + "=" * 60)
    if len(pdf_files) == 14:
        print(f"✅ 完成しました！全14個のPDFが生成されました。")
    else:
        print(f"⚠️  {len(pdf_files)}/14個のPDFが生成されました。")

    print(f"📁 出力ディレクトリ: {PDF_OUTPUT_DIR}")
    print("=" * 60)

    for pdf in pdf_files:
        size_kb = pdf.stat().st_size / 1024
        print(f"  • {pdf.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
