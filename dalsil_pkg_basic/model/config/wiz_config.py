from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizConfig(models.TransientModel):
    """
    Model untuk setting Config
    """
    _name = "dalsil.wiz_config"
    _inherit = "res.config.settings"

    def_sangu = fields.Float("Default Sangu Sopir", digits=(20,2))
    product_sangu = fields.Many2one("product.product", "Product Sangu")
    product_rent = fields.Many2one("product.product", "Product Rent Truck")

    @api.multi
    def set_setting(self):
        config = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
        config.write({
            "def_sangu": self.def_sangu,
            "product_sangu": self.product_sangu.id,
            "product_rent": self.product_rent.id
        })

    @api.multi
    def get_default_setting(self, context):
        config = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")

        return {
            "def_sangu": config.def_sangu,
            "product_sangu": config.product_sangu.id,
            "product_rent": config.product_rent.id
        }
        