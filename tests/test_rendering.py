"""Regression tests that do not need a PBX, TFTP daemon, or external services."""

import unittest
from starlette.requests import Request

from app.generator import render_phone
from app.main import OPTION_GROUPS, defaults, phone_context, templates


def request(path="/phone/new"):
    return Request({"type": "http", "method": "GET", "path": path, "query_string": b"", "headers": []})


class RenderingTests(unittest.TestCase):
    def test_new_phone_page_renders_without_jinja_global_list(self):
        html = templates.get_template("phone.html").render(
            **phone_context(request(), defaults(), None)
        )
        self.assertIn("Nouveau Cisco", html)
        self.assertIn(next(iter(OPTION_GROUPS)), html)

    def test_phone_xml_escapes_form_values_but_keeps_expert_xml(self):
        config = defaults()
        config["mac"] = "70:1F:53:4D:19:C8"
        config["phone_label"] = "Bureau & accueil"
        config["custom_xml"] = "<customOption>test</customOption>"

        filename, xml = render_phone(config)

        self.assertEqual(filename, "SEP701F534D19C8.cnf.xml")
        self.assertIn("Bureau &amp; accueil", xml)
        self.assertIn("<customOption>test</customOption>", xml)


if __name__ == "__main__":
    unittest.main()
