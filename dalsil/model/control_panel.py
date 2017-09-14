import re

from odoo import models, fields, api


class ISMEControlPanel(models.TransientModel):
    """
    Wizard control panel ismesoft
    """
    _inherit = "res.config.settings"
    _name = "isme.cp"

    # module on of
    module_l10n_dalsil = fields.Boolean("CoA DalSilSoft")

    # module paket
    module_dalsil_pkg_basic = fields.Boolean("Basic")

    @api.multi
    def change_email_odoo_to_isme(self):
        """
        debranding odoo di email
        """
        MTemplate = self.env["ss.model"].alt_orm("mail.template")
        query = MTemplate.select(MTemplate.id, MTemplate.name, MTemplate.subject, MTemplate.body_html)
        for template in tuple(query):
            vals = {}
            if template.name and re.search("odoo", template.name, re.IGNORECASE):
                vals["name"] = re.sub("odoo", "ISMESoft", template.name, flags=re.IGNORECASE)

            if template.subject and re.search("odoo", template.subject, re.IGNORECASE):
                vals["subject"] = re.sub("odoo", "ISMESoft", template.subject, flags=re.IGNORECASE)

            if template.body_html and re.search("odoo", template.body_html, re.IGNORECASE):  # ganti nama
                vals["body_html"] = re.sub("odoo", "ISMESoft", template.body_html, flags=re.IGNORECASE)

            body = vals.get("body_html", template.body_html)
            if body and re.search("logo\.png", body, re.IGNORECASE):  # ganti logo
                pattern = "\"/*(web/static/src/img/)*logo.png\""
                logo = "/dalsil/static/src/img/isme_soft_0X35.png"
                vals["body_html"] = re.sub(pattern, logo, template.body_html, flags=re.IGNORECASE)

            if vals:
                MTemplate.update(**vals).where(MTemplate.id == template.id).execute()
