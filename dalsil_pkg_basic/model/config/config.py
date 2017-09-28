from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Config(models.Model):
    """
    Model untuk config
    """
    _name = "dalsil.config"

    def_sangu = fields.Float("Default Sangu Sopir", digits=(20,2))
    product_sangu = fields.Many2one("product.product", "Product Sangu")
    product_rent = fields.Many2one("product.product", "Product Rent Truck")
    sangu_acc_id = fields.Many2one("account.account", "Account Sangu")
    rent_acc_id = fields.Many2one("account.account", "Account Rent")

    purc_acc_credit_id = fields.Many2one("account.account", "Account Credit Purchase")
    purc_acc_debit_id = fields.Many2one("account.account", "Account Debit Purchase")
    inv_acc_credit_id = fields.Many2one("account.account", "Account Credit Invoice")
    inv_acc_debit_id = fields.Many2one("account.account", "Account Debit Invoice")