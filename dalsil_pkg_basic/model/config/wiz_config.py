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
    product_fee = fields.Many2one("product.product", "Product Fee Sales")
    sangu_acc_id = fields.Many2one("account.account", "Account Sangu")
    rent_acc_id = fields.Many2one("account.account", "Account Rent")
    fee_acc_id = fields.Many2one("account.account", "Account Fee Sales")
    
    purc_acc_credit_id = fields.Many2one("account.account", "Account Credit Purchase")
    purc_acc_debit_id = fields.Many2one("account.account", "Account Debit Purchase")
    inv_acc_credit_id = fields.Many2one("account.account", "Account Credit Invoice")
    inv_acc_debit_id = fields.Many2one("account.account", "Account Debit Invoice")

    @api.multi
    def set_setting(self):
        config = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
        config.write({
            "def_sangu": self.def_sangu,
            "product_sangu": self.product_sangu.id,
            "product_rent": self.product_rent.id,
            "product_fee": self.product_fee.id,
            "sangu_acc_id": self.sangu_acc_id.id,
            "rent_acc_id": self.rent_acc_id.id,
            "fee_acc_id": self.fee_acc_id.id,
            "purc_acc_credit_id": self.purc_acc_credit_id.id,
            "purc_acc_debit_id": self.purc_acc_debit_id.id,
            "inv_acc_credit_id": self.inv_acc_credit_id.id,
            "inv_acc_debit_id": self.inv_acc_debit_id.id
        })

    @api.multi
    def get_default_setting(self, context):
        config = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")

        return {
            "def_sangu": config.def_sangu,
            "product_sangu": config.product_sangu.id,
            "product_rent": config.product_rent.id,
            "product_fee": config.product_fee.id,
            "sangu_acc_id": config.sangu_acc_id.id,
            "rent_acc_id": config.rent_acc_id.id,
            "fee_acc_id": config.fee_acc_id.id,
            "purc_acc_credit_id": config.purc_acc_credit_id.id,
            "purc_acc_debit_id": config.purc_acc_debit_id.id,
            "inv_acc_credit_id": config.inv_acc_credit_id.id,
            "inv_acc_debit_id": config.inv_acc_debit_id.id
        }
        