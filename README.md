# BMM（Business Manual Manager）
日本語 / English を切り替えられる業務マニュアル管理アプリです。
## 構成
```text
BMM_Business_Manual_Manager/
├── app.py
├── index.html
├── vercel.json
├── README.md
└── static/
```
## 採用技術
- Python 3
- Tkinter — デスクトップ版
- PyScript — ブラウザ上の Python 実行ポイント
- HTMX — HTML中心の拡張ポイント
- _hyperscript — 宣言的インタラクション
- Tailwind CSS — UI
- Alpine.js — CRUD状態管理
- Vue.js — Vueランタイムを利用可能にした構成
- TypeScript — 型定義リファレンス
- Vercel — 静的ホスティング

1. ローカル Web 版

```bash
cd /path/to/BMM_Business_Manual_Manager
python3 app.py
```
ブラウザで次を開きます。
```
http://127.0.0.1:5000/index.html
```
macOSで Port 5000 is in use が出る場合は、既存プロセスを停止してから再実行してください。

2. Tkinter版

```bash
python3 app.py --desktop
```
Tkinter版では新規作成・編集・削除・参照・日本語/英語切替を実装しています。

3. Vercel

このプロジェクトは index.html を静的ファイルとして配信する構成です。
vercel.json の rewrite により / を /index.html に接続します。
Vercel CLIを使う場合:
```bash
npm i -g vercel
cd /path/to/BMM_Business_Manual_Manager
vercel
```
Vercel Dashboardからデプロイする場合も、Gitリポジトリのルートにindex.html と vercel.json を置けば構成できます。
注意: Vercel上ではPythonのTkinter GUIは動きません。Tkinterはローカルデスクトップ版、index.htmlはブラウザ/Web版として分離しています。
Web版のCRUDデータはブラウザのlocalStorageに保存されるため、Vercelの静的配信でも新規作成・編集・削除・参照ができます。

4. データ保存

現在のWeb版は localStorage を使います。
本番で複数ユーザーが共有する業務マニュアルDBにする場合は、次の段階で
FastAPI / FlaskなどのPython APIとPostgreSQL等を追加してください。

5. CDN依存

index.html は以下をCDNから読み込みます。
- Tailwind CSS
- HTMX
- _hyperscript
- Alpine.js
- Vue.js
- PyScript
完全オフライン運用にする場合は、これらのアセットをローカル化してください。
