import os, json, sqlite3
from urllib.parse import urlencode
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .db import init_db, connect
from .generator import render_phone, write_phone, write_dialplan, normalize_mac
from .options import OPTION_GROUPS, BUTTON_TYPES, EXPERIMENTAL_FIELDS, PHONE_MODELS

app = FastAPI(title="LFINFO Cisco Provisioning Generator")
BASE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE / "templates"))

@app.on_event("startup")
def startup():
    init_db()

def defaults():
    d = {}
    for group in OPTION_GROUPS.values():
        for field in group["fields"]:
            d[field[0]] = field[3]
    d.update({
        "name": "",
        "mac": "",
        "model": "CP-7841",
        "buttons": [
            {
                "button": 1, "type": "line", "line_index": "1",
                "label": "Maison", "extension": "603", "display_name": "Maison",
                "contact": "603", "proxy": "USECALLMANAGER", "port": "5060",
                "auth_name": "603", "auth_password": "", "auto_answer": "2",
                "call_waiting": "3", "shared_line": "false",
                "mwi_lamp_policy": "3", "mwi_amwi": "1", "messages_number": "*98",
                "ring_idle": "4", "ring_active": "5", "max_calls": "4", "busy_trigger": "2",
                "target": "", "feature_option_mask": "1"
            },
            {"button": 2, "type": "blf", "line_index": "", "label": "LFINFO", "extension": "", "display_name": "", "contact": "", "proxy": "", "port": "", "auth_name": "", "auth_password": "", "auto_answer": "", "call_waiting": "", "shared_line": "", "mwi_lamp_policy": "", "mwi_amwi": "", "messages_number": "", "ring_idle": "", "ring_active": "", "max_calls": "", "busy_trigger": "", "target": "604", "feature_option_mask": "1"},
            {"button": 3, "type": "blf", "line_index": "", "label": "Florian", "extension": "", "display_name": "", "contact": "", "proxy": "", "port": "", "auth_name": "", "auth_password": "", "auto_answer": "", "call_waiting": "", "shared_line": "", "mwi_lamp_policy": "", "mwi_amwi": "", "messages_number": "", "ring_idle": "", "ring_active": "", "max_calls": "", "busy_trigger": "", "target": "1001", "feature_option_mask": "1"},
            {"button": 4, "type": "blf", "line_index": "", "label": "Chambre", "extension": "", "display_name": "", "contact": "", "proxy": "", "port": "", "auth_name": "", "auth_password": "", "auto_answer": "", "call_waiting": "", "shared_line": "", "mwi_lamp_policy": "", "mwi_amwi": "", "messages_number": "", "ring_idle": "", "ring_active": "", "max_calls": "", "busy_trigger": "", "target": "605", "feature_option_mask": "1"},
        ],
        "experimental": {k: "" for k in EXPERIMENTAL_FIELDS},
        "custom_xml": "",
    })
    return d

def phone_context(request: Request, cfg: dict, phone_id: int | None):
    return {
        "request": request, "cfg": cfg, "phone_id": phone_id,
        "groups": OPTION_GROUPS, "button_types": BUTTON_TYPES,
        "experimental_fields": EXPERIMENTAL_FIELDS, "phone_models": PHONE_MODELS,
        "default_tab": next(iter(OPTION_GROUPS)),
    }

def config_from_row(row) -> dict:
    """Merge saved configurations with new defaults as the UI grows."""
    cfg = defaults()
    saved = json.loads(row["config_json"])
    if not isinstance(saved, dict):
        raise ValueError("La configuration stockée n'est pas un objet JSON.")
    cfg.update(saved)
    saved_experimental = saved.get("experimental", {})
    if not isinstance(saved_experimental, dict):
        saved_experimental = {}
    cfg["experimental"] = {**defaults()["experimental"], **saved_experimental}
    saved_buttons = saved.get("buttons", [])
    if not isinstance(saved_buttons, list):
        saved_buttons = []
    default_buttons = defaults()["buttons"]
    cfg["buttons"] = [
        {**default_button, **(saved_buttons[index] if index < len(saved_buttons) and isinstance(saved_buttons[index], dict) else {})}
        for index, default_button in enumerate(default_buttons)
    ]
    return cfg

def error_redirect(path: str, message: str):
    return RedirectResponse(f"{path}?{urlencode({'error': message})}", status_code=303)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with connect() as con:
        phones = con.execute("SELECT * FROM phones ORDER BY name").fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "phones": phones})

@app.get("/phone/new", response_class=HTMLResponse)
def new_phone(request: Request):
    return templates.TemplateResponse("phone.html", phone_context(request, defaults(), None))

@app.get("/phone/{phone_id}", response_class=HTMLResponse)
def edit_phone(phone_id: int, request: Request):
    with connect() as con:
        row = con.execute("SELECT * FROM phones WHERE id=?", (phone_id,)).fetchone()
    if not row:
        raise HTTPException(404)
    return templates.TemplateResponse("phone.html", phone_context(request, config_from_row(row), phone_id))

def form_to_config(form):
    cfg = defaults()
    for group in OPTION_GROUPS.values():
        for field in group["fields"]:
            cfg[field[0]] = form.get(field[0], "")
    cfg["name"] = form.get("name", "")
    cfg["mac"] = normalize_mac(form.get("mac", ""))
    cfg["model"] = form.get("model", "CP-7841")
    if cfg["model"] not in PHONE_MODELS:
        raise ValueError("Modèle de téléphone non pris en charge.")
    cfg["name"] = cfg["name"].strip()
    if not cfg["name"]:
        raise ValueError("Le nom interne est obligatoire.")
    cfg["custom_xml"] = form.get("custom_xml", "")
    cfg["experimental"] = {k: form.get("exp__" + k, "") for k in EXPERIMENTAL_FIELDS}

    buttons = []
    for i in range(1, 5):
        b = {
            "button": i,
            "type": form.get(f"b{i}_type", "unused"),
            "line_index": form.get(f"b{i}_line_index", ""),
            "label": form.get(f"b{i}_label", ""),
            "extension": form.get(f"b{i}_extension", ""),
            "display_name": form.get(f"b{i}_display_name", ""),
            "contact": form.get(f"b{i}_contact", ""),
            "proxy": form.get(f"b{i}_proxy", ""),
            "port": form.get(f"b{i}_port", ""),
            "auth_name": form.get(f"b{i}_auth_name", ""),
            "auth_password": form.get(f"b{i}_auth_password", ""),
            "auto_answer": form.get(f"b{i}_auto_answer", ""),
            "call_waiting": form.get(f"b{i}_call_waiting", ""),
            "shared_line": form.get(f"b{i}_shared_line", ""),
            "mwi_lamp_policy": form.get(f"b{i}_mwi_lamp_policy", ""),
            "mwi_amwi": form.get(f"b{i}_mwi_amwi", ""),
            "messages_number": form.get(f"b{i}_messages_number", ""),
            "ring_idle": form.get(f"b{i}_ring_idle", ""),
            "ring_active": form.get(f"b{i}_ring_active", ""),
            "max_calls": form.get(f"b{i}_max_calls", ""),
            "busy_trigger": form.get(f"b{i}_busy_trigger", ""),
            "target": form.get(f"b{i}_target", ""),
            "feature_option_mask": form.get(f"b{i}_feature_option_mask", "1"),
        }
        buttons.append(b)
    cfg["buttons"] = buttons
    return cfg

@app.post("/phone/save")
async def save_phone(request: Request):
    form = await request.form()
    phone_id = form.get("phone_id") or None
    return_path = f"/phone/{phone_id}" if phone_id else "/phone/new"
    try:
        cfg = form_to_config(form)
    except ValueError as exc:
        return error_redirect(return_path, str(exc))
    payload = json.dumps(cfg, ensure_ascii=False)

    try:
        with connect() as con:
            if phone_id:
                cur = con.execute(
                    "UPDATE phones SET name=?, mac=?, model=?, config_json=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (cfg["name"], cfg["mac"], cfg["model"], payload, int(phone_id))
                )
                if cur.rowcount != 1:
                    raise ValueError("Identifiant de téléphone invalide.")
                pid = int(phone_id)
            else:
                cur = con.execute(
                    "INSERT INTO phones(name, mac, model, config_json) VALUES(?,?,?,?)",
                    (cfg["name"], cfg["mac"], cfg["model"], payload)
                )
                pid = cur.lastrowid
            con.commit()
    except (sqlite3.IntegrityError, ValueError) as exc:
        return error_redirect(return_path, "Cette adresse MAC existe déjà." if isinstance(exc, sqlite3.IntegrityError) else "Identifiant de téléphone invalide.")

    if form.get("action") == "generate":
        write_phone(cfg)
        write_dialplan()

    return RedirectResponse(f"/phone/{pid}", status_code=303)

@app.get("/phone/{phone_id}/xml", response_class=PlainTextResponse)
def preview_xml(phone_id: int):
    with connect() as con:
        row = con.execute("SELECT * FROM phones WHERE id=?", (phone_id,)).fetchone()
    if not row:
        raise HTTPException(404)
    cfg = config_from_row(row)
    _, xml = render_phone(cfg)
    return xml

@app.post("/phone/{phone_id}/generate")
def generate(phone_id: int):
    with connect() as con:
        row = con.execute("SELECT * FROM phones WHERE id=?", (phone_id,)).fetchone()
    if not row:
        raise HTTPException(404)
    cfg = config_from_row(row)
    write_phone(cfg)
    write_dialplan()
    return RedirectResponse(f"/phone/{phone_id}", status_code=303)
