from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

APP_ROOT = Path(__file__).resolve().parent
DATA_FILE = Path(os.getenv("HAT_MANUAL_DATA", APP_ROOT / "manuals.json"))
_lock = threading.Lock()

app = Flask(__name__, static_folder=None)

DEFAULT_MANUALS: list[dict[str, Any]] = [
    {
        "id": "welcome",
        "title": "はじめての業務マニュアル",
        "category": "基本",
        "body": "このマニュアルは、業務の目的・手順・注意点を整理するためのサンプルです。",
        "updated_at": "2026-08-10",
    },
    {
        "id": "safety",
        "title": "安全確認の基本手順",
        "category": "安全",
        "body": "1. 作業場所を確認する\\n2. 必要な備品を確認する\\n3. 不明点があれば責任者へ確認する",
        "updated_at": "2026-08-10",
    },
]


def _load_manuals() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return [dict(item) for item in DEFAULT_MANUALS]
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return [dict(item) for item in DEFAULT_MANUALS]


def _save_manuals(manuals: list[dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(manuals, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _json_error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status


@app.get("/")
def index():
    return send_from_directory(APP_ROOT, "index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True, "app": "Business Manual Manager"})


@app.get("/api/manuals")
def list_manuals():
    with _lock:
        manuals = _load_manuals()
    keyword = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip()

    if keyword:
        manuals = [
            m for m in manuals
            if keyword in m.get("title", "").lower()
            or keyword in m.get("body", "").lower()
        ]
    if category:
        manuals = [m for m in manuals if m.get("category") == category]

    return jsonify(manuals)


@app.get("/api/manuals/<manual_id>")
def get_manual(manual_id: str):
    with _lock:
        manual = next((m for m in _load_manuals() if m["id"] == manual_id), None)
    if manual is None:
        return _json_error("Manual not found.", 404)
    return jsonify(manual)


@app.post("/api/manuals")
def create_manual():
    payload = request.get_json(silent=True) or {}
    title = str(payload.get("title", "")).strip()
    category = str(payload.get("category", "基本")).strip() or "基本"
    body = str(payload.get("body", "")).strip()

    if not title:
        return _json_error("title is required.")

    manual = {
        "id": uuid.uuid4().hex,
        "title": title,
        "category": category,
        "body": body,
        "updated_at": __import__("datetime").date.today().isoformat(),
    }
    with _lock:
        manuals = _load_manuals()
        manuals.insert(0, manual)
        _save_manuals(manuals)
    return jsonify(manual), 201


@app.put("/api/manuals/<manual_id>")
def update_manual(manual_id: str):
    payload = request.get_json(silent=True) or {}
    with _lock:
        manuals = _load_manuals()
        manual = next((m for m in manuals if m["id"] == manual_id), None)
        if manual is None:
            return _json_error("Manual not found.", 404)

        title = str(payload.get("title", manual["title"])).strip()
        category = str(payload.get("category", manual["category"])).strip() or "基本"
        body = str(payload.get("body", manual["body"])).strip()
        if not title:
            return _json_error("title is required.")

        manual.update(
            title=title,
            category=category,
            body=body,
            updated_at=__import__("datetime").date.today().isoformat(),
        )
        _save_manuals(manuals)
    return jsonify(manual)


@app.delete("/api/manuals/<manual_id>")
def delete_manual(manual_id: str):
    with _lock:
        manuals = _load_manuals()
        new_manuals = [m for m in manuals if m["id"] != manual_id]
        if len(new_manuals) == len(manuals):
            return _json_error("Manual not found.", 404)
        _save_manuals(new_manuals)
    return jsonify({"ok": True, "id": manual_id})


# -----------------------------
# Tkinter desktop application
# -----------------------------
def run_tkinter() -> None:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk

    manuals = _load_manuals()
    root = tk.Tk()
    root.title("業務マニュアル Manager / Business Manual Manager")
    root.geometry("1100x700")

    left = ttk.Frame(root, padding=12)
    left.pack(side="left", fill="y")
    right = ttk.Frame(root, padding=12)
    right.pack(side="right", fill="both", expand=True)

    ttk.Label(left, text="業務マニュアル", font=("", 16, "bold")).pack(anchor="w")
    listbox = tk.Listbox(left, width=35, height=30)
    listbox.pack(fill="y", expand=True, pady=10)

    title_var = tk.StringVar()
    category_var = tk.StringVar(value="基本")
    ttk.Label(right, text="タイトル").pack(anchor="w")
    ttk.Entry(right, textvariable=title_var).pack(fill="x", pady=(0, 10))
    ttk.Label(right, text="カテゴリ").pack(anchor="w")
    ttk.Entry(right, textvariable=category_var).pack(fill="x", pady=(0, 10))
    ttk.Label(right, text="本文").pack(anchor="w")
    body = tk.Text(right, wrap="word")
    body.pack(fill="both", expand=True)

    def refresh():
        listbox.delete(0, "end")
        for m in manuals:
            listbox.insert("end", f'{m["title"]} [{m["category"]}]')

    def load_selected(_event=None):
        selection = listbox.curselection()
        if not selection:
            return
        m = manuals[selection[0]]
        title_var.set(m["title"])
        category_var.set(m["category"])
        body.delete("1.0", "end")
        body.insert("1.0", m["body"])

    def save():
        selection = listbox.curselection()
        if selection:
            m = manuals[selection[0]]
        else:
            m = {"id": uuid.uuid4().hex}
            manuals.insert(0, m)

        m["title"] = title_var.get().strip()
        m["category"] = category_var.get().strip() or "基本"
        m["body"] = body.get("1.0", "end").strip()
        m["updated_at"] = __import__("datetime").date.today().isoformat()
        _save_manuals(manuals)
        refresh()

    def delete():
        selection = listbox.curselection()
        if not selection:
            return
        if messagebox.askyesno("確認", "このマニュアルを削除しますか？"):
            manuals.pop(selection[0])
            _save_manuals(manuals)
            refresh()
            title_var.set("")
            category_var.set("基本")
            body.delete("1.0", "end")

    buttons = ttk.Frame(right)
    buttons.pack(fill="x", pady=10)
    ttk.Button(buttons, text="新規/保存", command=save).pack(side="left", padx=(0, 8))
    ttk.Button(buttons, text="削除", command=delete).pack(side="left")
    ttk.Button(buttons, text="終了", command=root.destroy).pack(side="right")

    listbox.bind("<<ListboxSelect>>", load_selected)
    refresh()
    root.mainloop()


if __name__ == "__main__":
    if os.getenv("HAT_DESKTOP") == "1" or "--desktop" in os.sys.argv:
        run_tkinter()
    else:
        app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
