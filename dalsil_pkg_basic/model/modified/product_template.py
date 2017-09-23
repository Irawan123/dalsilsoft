from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

# class ProductTemplateFeeSales(models.Model):
#     """
#     Product Fee Sales
#     """
#     _name = "product.template.fee_sales"

#     parent_id = fields.Many2one("product.template", "Product")
#     minimal = fields.Float("Minimal", digits=(20,2))
#     maximal = fields.Float("Maximal", digits=(20,2))
    # fee = fields.Float("Fee per barang", digits=(20,2))

class ProductTemplate(models.Model):
    """
    Product
    """
    _inherit = "product.template"

    # fee_ids = fields.One2many("product.template.fee_sales", "parent_id")
    fee = fields.Float("Fee per barang", digits=(20,2))