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