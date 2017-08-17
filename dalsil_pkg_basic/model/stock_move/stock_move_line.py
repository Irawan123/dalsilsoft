__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMoveLine(models.Model):
    _name = "dalsil.stock_move.line"
    _inherit = "ss.model"
    _description = "Stock Move Line"

    parent_id = fields.Many2one("dalsil.stock_move", "Parent", ondelete="cascade")
    product_id = fields.Many2one("dalsil.product", "Barang")
    qty = fields.Float(digits=(10,2), string="Jumlah Barang")
