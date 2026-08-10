# BMM (Business Manual Manager)

日本語 / English を切り替えられる業務マニュアル管理アプリです。

## Stack

- Python / Flask — Web API とページ配信
- Tkinter — デスクトップ版
- PyScript — ブラウザ上の Python 拡張用
- HTMX — HTML中心の非同期UI
- _hyperscript — 軽量なUIインタラクション
- Tailwind CSS — UIスタイリング
- Alpine.js — フォーム・CRUD状態管理
- Vue.js — Vueシェル
- TypeScript — 将来の型付きフロントエンドロジックを追加可能な構成
- Vercel — Web版のデプロイ

## Files

```text
.
├── app.py
├── index.html
├── requirements.txt
├── vercel.json
└── README.md
```

## Web版をローカルで起動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

ブラウザで `http://127.0.0.1:5000` を開きます。

## Tkinter版を起動

```bash
python app.py --desktop
```

または macOS / Linux などで:

```bash
HAT_DESKTOP=1 python app.py
```

Web版とTkinter版は同じ `manuals.json` をローカルでは共有します。

## CRUD

API:

```text
GET    /api/manuals
GET    /api/manuals/<id>
POST   /api/manuals
PUT    /api/manuals/<id>
DELETE /api/manuals/<id>
```

検索:

```text
/api/manuals?q=安全
/api/manuals?category=安全
```

## 日本語 / English

右上の `日本語` / `English` ボタンでUI言語を切り替えます。
選択言語はブラウザの `localStorage` に保存します。

## Vercel

このプロジェクトでは `app.py` を Vercel Python Runtime として扱います。

```json
{
  "builds": [
    { "src": "app.py", "use": "@vercel/python" }
  ]
}
```

`index.html` は `app.py` から `/` で配信しています。
そのため、Vercelで `index.html` を別の静的Functionとして動かす必要はありません。

### 重要: データ永続化

Vercel Functions のローカルファイルは永続DBとして利用できません。
このサンプルの `manuals.json` はローカル開発・デモ用です。

本番でCRUDデータを永続化する場合は、PostgreSQL / Vercel Postgres相当の外部DB、またはVercel対応のストレージへ移行してください。

## Vercel CLI

```bash
npm install -g vercel
vercel login
vercel
vercel --prod
```

## Vercel Dashboard の Framework Preset について

ユーザーインターフェース上で「Flask」「Other」のような選択肢が表示される場合でも、`vercel.json` が個別ファイルに「Flask / Other」を割り当てる仕組みではありません。

この構成では Python Function は `@vercel/python` で明示し、`index.html` は Flask が配信します。

## 次の拡張候補

1. PostgreSQLによる永続化
2. Markdown対応
3. 画像・PDF添付
4. マニュアル版管理
5. ロール別アクセス制御
6. ログイン / 認証
7. カテゴリ管理
8. 印刷・PDF出力
9. TypeScriptを独立 `src/*.ts` に分離
10. Vue.jsをCRUD画面の主要UIへ昇格
