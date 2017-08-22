from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizConfig(models.TransientModel):
    """
    Model untuk setting Config
    """
    _name = "dalsil.wiz_config"
    _inherit = "res.config.settings"

    def_sangu = fields.Float("Default Sangu Sopir", digits=(20,2))

    @api.multi
    def set_setting(self):
        config = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
        config.write({
            "def_sangu": self.def_sangu
        })

    @api.multi
    def get_default_setting(self):
        config = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")

        return {
            "def_sangu": config.def_sangu.id
        }
        