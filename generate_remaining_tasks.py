#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
残りの10名（4-13番目）の詳細課題を生成するスクリプト
"""

import json
from pathlib import Path

# 各生徒のデータ
STUDENTS_DATA = {
    "濱尾紗那": {
        "school": "勝瀬",
        "hokusin_score": 195,
        "hokusin_deviation": 56.1,
        "score_3subjects": 112,
        "deviation_3subjects": 53.6,
        "japanese": 63,
        "japanese_dev": 57,
        "math": 48,
        "math_dev": 48,
        "english": 39,
        "english_dev": 44,
    },
    "渡邉裕莉": {
        "school": "勝瀬",
        "hokusin_score": 190,
        "hokusin_deviation": 54.7,
        "score_3subjects": 104,
        "deviation_3subjects": 50.3,
        "japanese": 44,
        "japanese_dev": 42,
        "math": 60,
        "math_dev": 57,
        "english": 49,
        "english_dev": 49,
    },
    "大和田悠月": {
        "school": "勝瀬",
        "hokusin_score": 165,
        "hokusin_deviation": 51.0,
        "score_3subjects": 92,
        "deviation_3subjects": 46.8,
        "japanese": 43,
        "japanese_dev": 41,
        "math": 35,
        "math_dev": 38,
        "english": 51,
        "english_dev": 51,
    },
    "田野史陽": {
        "school": "富士見台",
        "hokusin_score": 160,
        "hokusin_deviation": 49.4,
        "score_3subjects": 88,
        "deviation_3subjects": 44.7,
        "japanese": 62,
        "japanese_dev": 55,
        "math": 53,
        "math_dev": 53,
        "english": 35,
        "english_dev": 40,
    },
    "富樫菜々美": {
        "school": "富士見東",
        "hokusin_score": 150,
        "hokusin_deviation": 49.0,
        "score_3subjects": 87,
        "deviation_3subjects": 44.5,
        "japanese": 66,
        "japanese_dev": 58,
        "math": 38,
        "math_dev": 41,
        "english": 35,
        "english_dev": 40,
    },
    "斉藤栞": {
        "school": "勝瀬",
        "hokusin_score": 175,
        "hokusin_deviation": 46.5,
        "score_3subjects": 78,
        "deviation_3subjects": 39.9,
        "japanese": 59,
        "japanese_dev": 53,
        "math": 25,
        "math_dev": 28,
        "english": 32,
        "english_dev": 38,
    },
    "榎本大雅": {
        "school": "富士見台",
        "hokusin_score": 125,
        "hokusin_deviation": 43.8,
        "score_3subjects": 73,
        "deviation_3subjects": 37.4,
        "japanese": 44,
        "japanese_dev": 42,
        "math": 30,
        "math_dev": 33,
        "english": 30,
        "english_dev": 35,
    },
    "吉田蒼": {
        "school": "富士見台",
        "hokusin_score": 115,
        "hokusin_deviation": 43.1,
        "score_3subjects": 64,
        "deviation_3subjects": 32.7,
        "japanese": 38,
        "japanese_dev": 36,
        "math": 68,
        "math_dev": 65,
        "english": 25,
        "english_dev": 29,
    },
    "紫関啓文": {
        "school": "富士見東",
        "hokusin_score": 120,
        "hokusin_deviation": 42.1,
        "score_3subjects": 70,
        "deviation_3subjects": 35.8,
        "japanese": 56,
        "japanese_dev": 51,
        "math": 48,
        "math_dev": 48,
        "english": 22,
        "english_dev": 26,
    },
    "浦部莉乃": {
        "school": "勝瀬",
        "hokusin_score": 100,
        "hokusin_deviation": 35.5,
        "score_3subjects": 40,
        "deviation_3subjects": 20.5,
        "japanese": 49,
        "japanese_dev": 45,
        "math": 16,
        "math_dev": 18,
        "english": 18,
        "english_dev": 21,
    },
}

# テンプレート
TASK_TEMPLATE = """## 【{name}（{school}）】

**基本情報：**
- 総合点：{hokusin_score}点 / 偏差値{hokusin_deviation}
- 3教科：{score_3subjects}点 / 偏差値{deviation_3subjects}
- 国語：{japanese}点 / 偏差値{japanese_dev}
- 数学：{math}点 / 偏差値{math_dev}
- 英語：{english}点 / 偏差値{english_dev}

**【最優先の改善ポイント】**

{priority_text}

#### 【国語】

{japanese_tasks}

#### 【数学】

{math_tasks}

#### 【英語】

{english_tasks}

**【次回北辰までの目標】**
- 総合点：{hokusin_score} → {target_total}点以上
- 国語：{japanese} → {target_japanese}点以上
- 数学：{math} → {target_math}点以上
- 英語：{english} → {target_english}点以上

---
"""

def generate_priority_text(name):
    """各生徒の最優先改善ポイントのテキストを生成"""
    priority_data = {
        "濱尾紗那": "数学の一次関数と確率が課題。国語のインタビュー問題（全体88%本人×）を落としている。特に数学基礎の定着が重要。次回で195点以上を目指す。",
        "渡邉裕莉": "国語44点が最大課題。説明文読解と多項式の利用が課題。基礎的な読解力と数学の計算スキルを同時に改善が必要。次回で190点以上を目指す。",
        "大和田悠月": "数学35点が最大課題。因数分解（全体86%本人×）と連立方程式（全体81%本人×）が落としている。国語の説明文読解も課題。次回で165点以上を目指す。",
        "田野史陽": "英語35点が最大課題。説明文読解適語補充（全体72%本人×）と一次方程式利用（全体62%本人×）が落としている。英語基礎と数学応用の両面改善が必要。次回で160点以上を目指す。",
        "富樫菜々美": "数学38点が最大課題。心情把握（全体81%本人×）と多項式（全体58%本人×）が落としている。特に数学の基本計算と国語読解の並行改善が必要。次回で150点以上を目指す。",
        "斉藤栞": "数学25点が最大課題で全般的に低い。説明文読解（全体76%/68%本人×）が落としている。全教科の基礎学力の底上げが最優先。計算スキルの完全定着が鍵。次回で175点以上を目指す。",
        "榎本大雅": "全教科全般的に底上げが必要。数学30点と英語30点の両方が課題。文学内容（全体91%本人×）とインタビュー問題（全体88%本人×）が落としている。基礎的な学力全般の強化が必須。次回で125点以上を目指す。",
        "吉田蒼": "英語25点が最大課題。説明文読解適語句補充（全体66%本人×）が落としている。数学は計算力が高いため、英語の集中強化が必要。次回で115点以上を目指す。",
        "紫関啓文": "英語22点が最大課題。リスニング（全体65%本人×）が落としている。国語の読解力は高いため、英語基礎文法とリスニング強化が重点。次回で120点以上を目指す。",
        "浦部莉乃": "全教科全般的に底上げが必要。数学16点、英語18点の底上げが最優先。ただし読解力と計算力は相対的に高いため、基礎語彙と基本計算の定着で大幅改善が可能。次回で100点以上（基礎学力の定着）を目指す。",
    }
    return priority_data.get(name, "基礎学力の定着を最優先に、個別課題に取り組みます。")

def generate_japanese_tasks(name, score):
    """国語課題を生成"""
    if score >= 60:
        return """**必達課題：**
- 教材名：北辰テスト対応読解教材 - 説明的文章編
- 内容：筆者の主張の理解、段落構成の把握
- ページ/問題形式：P.10-25 説明文読解問題 8問
- 取り組み方：各段落の役割（導入・理由説明・結論）をマーク。筆者の言いたいことを1文で要約
- 合格基準：8問中6問以上正答

**必達課題（敬語・文法）：**
- 教材名：敬語・文法テキスト
- 内容：敬語の使い分け、文法基本
- ページ/問題形式：P.1-15 敬語・文法問題 20問
- 取り組み方：敬語の3種類（敬語・謙譲語・丁寧語）を区別する練習
- 合格基準：20問中16問以上正答

**必達課題（漢字）：**
- 教材名：漢字読み取り・書き取りテキスト
- 内容：読み取り・書き取り・識別
- ページ/問題形式：P.1-15 読み取り10問 + 書き取り10問 + 識別10問
- 取り組み方：毎日10問ずつ。間違えた漢字は5回書く
- 合格基準：合計30問中24問以上正答

**余裕があれば課題：**
- 教材名：古典読解テキスト「基礎から応用へ」
- ページ/問題形式：P.1-12 短編2作品の読解"""
    elif score >= 50:
        return """**必達課題：**
- 教材名：北辰テスト対応読解教材 - 説明的文章編
- 内容：基本的な内容把握、段落構成の理解
- ページ/問題形式：P.5-20 説明文読解問題 6問
- 取り組み方：設問の根拠を本文から探す。線引きしながら読む
- 合格基準：6問中4問以上正答

**必達課題（漢字）：**
- 教材名：中学国語漢字テキスト「中学必須漢字」
- 内容：読み取り・書き取り・識別
- ページ/問題形式：P.1-20 読み取り15問 + 書き取り15問
- 取り組み方：毎日10問ずつ。意味を理解してから覚える
- 合格基準：合計30問中24問以上正答

**必達課題（文法基礎）：**
- 教材名：文法テキスト「中学国語の基本」
- 内容：品詞分類、敬語の基本
- ページ/問題形式：P.1-12 基本問題 15問
- 取り組み方：各文法項目を例文とともに理解
- 合格基準：15問中12問以上正答

**余裕があれば課題：**
- 教材名：短編読解テキスト
- ページ/問題形式：P.20-28 短編1編 + 問題3問"""
    else:
        return """**必達課題：**
- 教材名：北辰テスト対応読解教材 - 基礎編
- 内容：基本的な意味把握、簡単な内容理解
- ページ/問題形式：P.1-15 基礎読解問題 5問
- 取り組み方：わかりやすい文から始める。線引きしながら読む。設問の答えを本文から探す
- 合格基準：5問中3問以上正答

**必達課題（漢字：最重要）：**
- 教材名：中学必須漢字「基本200字」
- 内容：中学で必ず出る200字の読み取り・書き取り
- ページ/問題形式：P.1-25 毎日8字ずつ、25日で完成
- 取り組み方：毎日8字を読む→意味確認→書く→5回繰り返す
- 合格基準：200字中160字以上を正確に読み書きできる

**必達課題（基礎文法）：**
- 教材名：文法の基礎テキスト「わかりやすい国語」
- 内容：品詞、敬語、基本的な文法ルール
- ページ/問題形式：P.1-10 品詞の分類 - 10問
- 取り組み方：各問について、なぜそうなるのかを考える。何度も繰り返す
- 合格基準：10問中8問以上正答"""

def generate_math_tasks(name, score):
    """数学課題を生成"""
    if score >= 60:
        return """**必達課題（一次関数）：**
- 教材名：「校舎対抗バトル大勉強大会テキスト3年数学」
- 内容：一次関数の基本と応用
- ページ/問題形式：第30回～第37回（各25問、計200問）
- 取り組み方：グラフの描き方を意識しながら解く。式とグラフの関係を理解
- 合格基準：各回85%以上の正答率

**必達課題（確率）：**
- 教材名：北辰対応確率テキスト
- 内容：確率の計算、樹形図
- ページ/問題形式：P.5-18 確率問題 12問
- 取り組み方：樹形図を正確に描く練習を優先
- 合格基準：12問中9問以上正答

**必達課題（多項式）：**
- 教材名：高校入試数学「絶対暗記事項」
- 内容：多項式の計算と展開
- ページ/問題形式：P.3-10 解説 + P.11-18 練習問題 15問
- 取り組み方：各ステップを丁寧に書く。計算ミスを減らすことが重点
- 合格基準：15問中12問以上正答

**余裕があれば課題：**
- 教材名：応用問題集
- ページ/問題形式：P.25-32 融合問題"""
    elif score >= 45:
        return """**必達課題（一次関数）：**
- 教材名：「校舎対抗バトル大勉強大会テキスト3年数学」
- 内容：一次関数の基本
- ページ/問題形式：第30回～第35回（計150問）
- 取り組み方：グラフを丁寧に描く。基本的なパターンを何度も繰り返す
- 合格基準：各回80%以上の正答率

**必達課題（計算基礎）：**
- 教材名：式の計算テキスト
- 内容：因数分解、連立方程式などの基本計算
- ページ/問題形式：P.1-15 基本計算問題 40問
- 取り組み方：ステップごとに計算をチェック。計算ミスをなくす
- 合格基準：40問中32問以上正答

**必達課題（確率）：**
- 教材名：確率基礎テキスト
- 内容：確率の意味と樹形図
- ページ/問題形式：P.1-10 基礎問題 8問
- 取り組み方：樹形図をしっかり描く。全体と部分の関係を理解
- 合格基準：8問中6問以上正答

**余裕があれば課題：**
- 教材名：確認テキスト
- ページ/問題形式：P.15-22 応用問題 5問"""
    else:
        return """**必達課題（計算基礎：最重要）：**
- 教材名：「校舎対抗バトル大勉強大会テキスト3年数学」第1～15回
- 内容：正負の数、式の計算、一次方程式、連立方程式
- ページ/問題形式：第1～15回（各25問、計375問）
- 取り組み方：毎日1回分（25問）を15分で解く。全問完答を目指す
- 合格基準：各回75%以上の正答率。4週間で完成

**必達課題（因数分解）：**
- 教材名：因数分解基礎テキスト
- 内容：簡単な因数分解の基本
- ページ/問題形式：P.1-12 基本問題 20問
- 取り組み方：パターンを覚える。同じパターンを何度も繰り返す
- 合格基準：20問中16問以上正答

**必達課題（確率：基礎）：**
- 教材名：確率はじめてテキスト
- 内容：確率の意味、樹形図の描き方
- ページ/問題形式：P.1-8 基礎問題 6問
- 取り組み方：樹形図を丁寧に描く。全パターンを列挙する
- 合格基準：6問中4問以上正答"""

def generate_english_tasks(name, score):
    """英語課題を生成"""
    if score >= 45:
        return """**必達課題：**
- 教材名：英語会話文読解テキスト
- 内容：会話文の流れを理解し、適切な選択肢を入れる
- ページ/問題形式：P.3-15 会話文読解の適語補充 8問
- 取り組み方：会話の流れ全体を把握してから選択肢を検討
- 合格基準：8問中6問以上正答

**必達課題（単語）：**
- 教材名：高校入試英語「頻出単語150」
- 内容：北辰テストに頻出の単語
- ページ/問題形式：P.1-10 単語リスト + テスト 100問
- 取り組み方：毎日10語ずつ、英文の中で覚える
- 合格基準：テストで80問以上正答

**必達課題（文法）：**
- 教材名：英文法テキスト「基本文法完全マスター」
- 内容：時制、助動詞、受動態
- ページ/問題形式：P.5-18 文法問題 15問
- 取り組み方：各文法項目について、なぜその形になるのかを理解
- 合格基準：15問中12問以上正答

**余裕があれば課題：**
- 教材名：英語読解テキスト
- ページ/問題形式：P.25-32 短編1題"""
    elif score >= 35:
        return """**必達課題（基本文法）：**
- 教材名：英文法入門テキスト「中学英文法の基礎」
- 内容：be動詞、一般動詞、基本時制
- ページ/問題形式：P.1-20 基本文法問題 30問
- 取り組み方：文法ルールの解説を読む→例文を音読→問題を解く
- 合格基準：30問中24問以上正答

**必達課題（単語：最重要）：**
- 教材名：中学英語基本単語「必須100語」
- 内容：中学で必ず出る基本単語100語
- ページ/問題形式：P.1-15 毎日5語ずつ、20日で完成
- 取り組み方：毎日5語を読む→意味確認→例文を音読→書く
- 合格基準：100語中80語以上を正確に読み書きできる

**必達課題（リスニング）：**
- 教材名：英語リスニング基礎テキスト
- 内容：基本的なリスニング
- ページ/問題形式：トラック01～10（各2分）+ 問題 10問
- 取り組み方：何度も繰り返し聞く。スクリプトを確認してから再度聞く
- 合格基準：10問中7問以上正答

**余裕があれば課題：**
- 教材名：簡単な読解テキスト
- ページ/問題形式：P.5-12 短い文章 2編"""
    else:
        return """**必達課題（基本文法：最重要）：**
- 教材名：英文法はじめてテキスト「わかる英文法」
- 内容：be動詞と一般動詞の基本
- ページ/問題形式：P.1-15 基本文法 25問
- 取り組み方：解説を読む→例文を3回音読→問題を解く→間違えた問題を繰り返す
- 合格基準：25問中20問以上正答

**必達課題（単語：緊急重要）：**
- 教材名：中学英語必須単語「基本50語」
- 内容：中学英語で最初に習う50語
- ページ/問題形式：P.1-10 毎日5語ずつ、10日で完成
- 取り組み方：毎日5語を読む→意味確認→書く→5回繰り返す
- 合格基準：50語を完璧に読み書きできる

**必達課題（リスニング基礎）：**
- 教材名：リスニングはじめてテキスト
- 内容：英語を聞く習慣づけ
- ページ/問題形式：トラック01～08（各1分）+ スクリプト
- 取り組み方：スクリプトなしで聞く→スクリプトで確認→もう一度聞く
- 合格基準：内容をおおよそ理解できる"""

def generate_targets(name, score):
    """次回目標を生成"""
    targets = {
        "濱尾紗那": (195, 74, 62, 60),
        "渡邉裕莉": (190, 64, 70, 56),
        "大和田悠月": (165, 63, 55, 60),
        "田野史陽": (160, 72, 62, 48),
        "富樫菜々美": (150, 75, 52, 48),
        "斉藤栞": (175, 70, 45, 50),
        "榎本大雅": (125, 60, 50, 50),
        "吉田蒼": (115, 55, 80, 40),
        "紫関啓文": (120, 65, 60, 38),
        "浦部莉乃": (100, 60, 45, 40),
    }
    if name in targets:
        return targets[name]
    return (score + 20, score + 10, score + 10, score + 10)

def generate_student_task(name, data):
    """生徒の詳細課題を生成"""
    target_total, target_jp, target_math, target_eng = generate_targets(name, data["hokusin_score"])

    return TASK_TEMPLATE.format(
        name=name,
        school=data["school"],
        hokusin_score=data["hokusin_score"],
        hokusin_deviation=data["hokusin_deviation"],
        score_3subjects=data["score_3subjects"],
        deviation_3subjects=data["deviation_3subjects"],
        japanese=data["japanese"],
        japanese_dev=data["japanese_dev"],
        math=data["math"],
        math_dev=data["math_dev"],
        english=data["english"],
        english_dev=data["english_dev"],
        priority_text=generate_priority_text(name),
        japanese_tasks=generate_japanese_tasks(name, data["japanese"]),
        math_tasks=generate_math_tasks(name, data["math"]),
        english_tasks=generate_english_tasks(name, data["english"]),
        target_total=target_total,
        target_japanese=target_jp,
        target_math=target_math,
        target_english=target_eng,
    )

def main():
    print("=" * 60)
    print("残りの10名分の詳細課題を生成中...")
    print("=" * 60 + "\n")

    repo_path = Path(__file__).parent
    output_file = repo_path / "all_students_tasks_extended.md"

    # Part1のヘッダーを読み込む
    part1_file = repo_path / "all_students_tasks_part1.md"
    with open(part1_file, 'r', encoding='utf-8') as f:
        part1_content = f.read()

    # ヘッダーを抽出
    header_match = part1_content.split("## 【")[0]

    # 新しいファイルを作成
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header_match)
        f.write("\n")

        # Part1の3名を追加
        f.write("## 【陳一嘉（富士見台）】\n\n")
        f.write(part1_content.split("## 【陳一嘉（富士見台）】")[1].split("## 【")[0].strip())
        f.write("\n\n---\n\n")

        f.write("## 【小暮理奈葉（勝瀬）】\n\n")
        f.write(part1_content.split("## 【小暮理奈葉（勝瀬）】")[1].split("## 【")[0].strip())
        f.write("\n\n---\n\n")

        f.write("## 【井上結寿（勝瀬）】\n\n")
        f.write(part1_content.split("## 【井上結寿（勝瀬）】")[1].strip())
        f.write("\n\n---\n\n")

        # 残りの10名を追加
        for i, (name, data) in enumerate(STUDENTS_DATA.items(), 1):
            print(f"  [{i:2d}/10] {name}（{data['school']}）を生成中...")
            task = generate_student_task(name, data)
            f.write(task)

    print(f"\n✅ 完成しました！")
    print(f"📁 出力ファイル: {output_file}")
    print(f"📊 全13名分の詳細課題が含まれています")

if __name__ == "__main__":
    main()
