from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"
HOST = "127.0.0.1"
PORT = 5000


def run_web_server(open_browser: bool = True) -> None:
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(BASE_DIR), **kwargs)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/index.html"
    print(f"BMM web server: {url}")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


class BMMDesktop(tk.Tk):
    """Small Tkinter CRUD client using the same JSON data model as the web UI."""

    def __init__(self):
        super().__init__()
        self.title("BMM - Business Manual Manager")
        self.geometry("1050x700")
        self.minsize(850, 560)
        self.lang = "ja"
        self.manuals: list[dict] = []
        self._build()
        self._load_sample()
        self._refresh()

    def _build(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        self.title_label = ttk.Label(top, text="BMM - Business Manual Manager",
                                     font=("Helvetica", 18, "bold"))
        self.title_label.pack(side="left")
        ttk.Button(top, text="日本語 / English", command=self.toggle_language).pack(side="right")

        toolbar = ttk.Frame(self, padding=(12, 0, 12, 8))
        toolbar.pack(fill="x")
        self.new_btn = ttk.Button(toolbar, command=self.new_manual)
        self.new_btn.pack(side="left", padx=(0, 6))
        self.edit_btn = ttk.Button(toolbar, command=self.edit_manual)
        self.edit_btn.pack(side="left", padx=6)
        self.delete_btn = ttk.Button(toolbar, command=self.delete_manual)
        self.delete_btn.pack(side="left", padx=6)
        self.view_btn = ttk.Button(toolbar, command=self.view_manual)
        self.view_btn.pack(side="left", padx=6)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = ttk.Frame(body, padding=8)
        right = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        body.add(right, weight=2)

        self.tree = ttk.Treeview(left, columns=("title", "category"), show="headings")
        self.tree.heading("title", text="Title")
        self.tree.heading("category", text="Category")
        self.tree.column("title", width=230)
        self.tree.column("category", width=120)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.view_manual())

        self.viewer = tk.Text(right, wrap="word", padx=14, pady=14, font=("Helvetica", 12))
        self.viewer.pack(fill="both", expand=True)
        self.viewer.configure(state="disabled")

    def _load_sample(self):
        self.manuals = [
            {"id": "demo-1", "title": "新入社員オンボーディング",
             "category": "人事", "body": "1. アカウントを作成\n2. 就業規則を確認\n3. チームへ挨拶",
             "updated": "2026-08-10"},
            {"id": "demo-2", "title": "Daily Opening Checklist",
             "category": "Operations", "body": "1. Check systems\n2. Review tasks\n3. Confirm safety",
             "updated": "2026-08-10"},
        ]

    def selected(self):
        item = self.tree.selection()
        if not item:
            return None
        idx = int(item[0])
        return self.manuals[idx]

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, manual in enumerate(self.manuals):
            self.tree.insert("", "end", iid=str(i),
                             values=(manual["title"], manual["category"]))
        if self.manuals:
            self.tree.selection_set("0")
            self.view_manual()

    def _dialog(self, manual=None):
        title = simpledialog.askstring("BMM", "Title:", initialvalue=(manual or {}).get("title", ""))
        if title is None:
            return None
        category = simpledialog.askstring("BMM", "Category:", initialvalue=(manual or {}).get("category", ""))
        if category is None:
            return None
        body = simpledialog.askstring("BMM", "Manual content:", initialvalue=(manual or {}).get("body", ""))
        if body is None:
            return None
        return {"title": title.strip(), "category": category.strip(),
                "body": body, "updated": "2026-08-10"}

    def new_manual(self):
        data = self._dialog()
        if data and data["title"]:
            data["id"] = f"desktop-{len(self.manuals)+1}"
            self.manuals.append(data)
            self._refresh()

    def edit_manual(self):
        manual = self.selected()
        if not manual:
            messagebox.showinfo("BMM", "Select a manual first.")
            return
        data = self._dialog(manual)
        if data:
            manual.update(data)
            self._refresh()

    def delete_manual(self):
        manual = self.selected()
        if not manual:
            return
        if messagebox.askyesno("BMM", f"Delete '{manual['title']}'?"):
            self.manuals.remove(manual)
            self._refresh()

    def view_manual(self):
        manual = self.selected()
        self.viewer.configure(state="normal")
        self.viewer.delete("1.0", "end")
        if manual:
            self.viewer.insert("end", f"{manual['title']}\n")
            self.viewer.insert("end", f"{manual['category']}  |  {manual['updated']}\n\n")
            self.viewer.insert("end", manual["body"])
        self.viewer.configure(state="disabled")

    def toggle_language(self):
        self.lang = "en" if self.lang == "ja" else "ja"
        labels = {
            "ja": ("新規作成", "編集", "削除", "参照"),
            "en": ("New", "Edit", "Delete", "View"),
        }[self.lang]
        self.new_btn.configure(text=labels[0])
        self.edit_btn.configure(text=labels[1])
        self.delete_btn.configure(text=labels[2])
        self.view_btn.configure(text=labels[3])


def main():
    parser = argparse.ArgumentParser(description="BMM - Business Manual Manager")
    parser.add_argument("--desktop", action="store_true", help="launch Tkinter desktop app")
    parser.add_argument("--no-browser", action="store_true", help="do not auto-open browser")
    args = parser.parse_args()
    if args.desktop:
        BMMDesktop().mainloop()
    else:
        run_web_server(open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
