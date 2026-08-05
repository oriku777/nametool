# 教材PDFマッピング設定ガイド

## 現在の状況
- **PDF ファイル数**: 21個
- **必要な教材数**: 46種類
- **対象生徒**: 13名

## するべき事

各PDFファイルが**どの教材に対応するか**を指定する必要があります。

### ステップ1: 各PDFの内容を確認

以下のファイル一覧から、各PDFの内容を確認してください：

```
教材ディレクトリ: teaching_materials/
```

各PDFを開いて、以下の情報を確認：
- 教材のタイトル（表紙、はじめに等）
- 主要な単元・内容
- ページ番号

### ステップ2: マッピング情報の入力

`material_pdf_mapping.json` ファイルの以下の形式で、各教材の情報を入力：

```json
{
  "教材名": {
    "pdf_file": "teaching_materials/ファイル名.pdf",
    "start_page": 1,
    "end_page": 20,
    "notes": "備考（任意）"
  }
}
```

### 例

```json
{
  "北辰テスト対応読解教材 - 文学的文章編": {
    "pdf_file": "teaching_materials/1e13943c-20260804222302260_part01_p0119.pdf",
    "start_page": 5,
    "end_page": 35,
    "notes": "P.5-20が文学的文章、P.28-35が情景理解"
  },
  "古典読解テキスト「基礎から応用へ」": {
    "pdf_file": "teaching_materials/0018affd-20260804224416182_part03_p4464.pdf",
    "start_page": 1,
    "end_page": 50,
    "notes": ""
  }
}
```

### ステップ3: マッピングファイルの作成

1. `material_pdf_mapping_template.json` をコピー
2. ファイル名を `material_pdf_mapping.json` に変更
3. 各教材のPDFファイルと ページ範囲を編集

### ステップ4: 実行

すべての教材がマッピングされたら、以下のコマンドを実行：

```bash
python3 extract_and_create_booklets.py
```

---

## テンプレート生成状況

✅ `material_pdf_mapping_template.json` - 生成済み（編集して `material_pdf_mapping.json` として保存）
✅ `student_materials_mapping.json` - 生徒別教材マッピング完成

---

## ご質問がある場合

各PDFの内容を確認した上で、以下の情報をお知らせください：

- **PDF ファイル名**: 
- **教材タイトル**:
- **含まれるページ範囲**: P.1-20 等
- **主要な内容**: （例：古典読解、文法など）

