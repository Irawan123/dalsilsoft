__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Purchase(models.Model):
    _name = "dalsil.purchase"
    _inherit = "ss.model"
    _description = "Purchase"

    parent_id = fields.Many2one("dalsil.stock_move", "Parent", ondelete="cascade")
    product_id = fields.Many2one("dalsil.product", "Barang")
    qty = fields.Float(digits=(10,2), string="Jumlah Barang")
