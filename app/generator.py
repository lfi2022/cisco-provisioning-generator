from pathlib import Path
import os, re
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from .options import EXPERIMENTAL_DEVICE_FIELDS

BASE = Path(__file__).resolve().parent
env = Environment(
    loader=FileSystemLoader(str(BASE / "templates")),
    undefined=StrictUndefined,
    # Form values must never be able to break the generated XML.  custom_xml is
    # intentionally marked safe by the template: it is the explicit expert
    # injection area documented in the UI.
    autoescape=select_autoescape(default=True),
    trim_blocks=True,
    lstrip_blocks=True,
)

def normalize_mac(mac: str) -> str:
    mac = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(mac) != 12:
        raise ValueError("La MAC doit contenir exactement 12 caractères hexadécimaux.")
    return mac

def xml_bool(value):
    return str(value).lower() in ("1", "true", "yes", "on")

env.filters["xml_bool"] = lambda v: "true" if xml_bool(v) else "false"

def render_phone(config: dict) -> tuple[str, str]:
    mac = normalize_mac(config["mac"])
    template = env.get_template("sep7841.xml.j2")
    xml = template.render(**config, experimental_device_fields=EXPERIMENTAL_DEVICE_FIELDS)
    return f"SEP{mac}.cnf.xml", xml

def write_phone(config: dict):
    filename, xml = render_phone(config)
    root = Path(os.getenv("TFTP_ROOT", "/srv/provisioning/tftp"))
    root.mkdir(parents=True, exist_ok=True)
    target = root / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(xml, encoding="utf-8")
    temporary.chmod(0o644)
    temporary.replace(target)
    target.chmod(0o644)
    return target

def write_dialplan(patterns=None):
    root = Path(os.getenv("TFTP_ROOT", "/srv/provisioning/tftp"))
    root.mkdir(parents=True, exist_ok=True)
    target = root / "dialplan.xml"
    patterns = patterns or [
        {"match": "*", "timeout": "5"},
    ]
    tmpl = env.get_template("dialplan.xml.j2")
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(tmpl.render(patterns=patterns), encoding="utf-8")
    temporary.chmod(0o644)
    temporary.replace(target)
    target.chmod(0o644)
    return target
