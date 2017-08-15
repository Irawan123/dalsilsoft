__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Product(models.Model):
    _name = "dalsil.product"
    _inherit = "ss.model"
    _description = "Product"

    name = fields.Char("Nama Barang", required=True)
    uom_id = fields.Many2one("dalsil.uom", "Satuan Barang", required=True)
    stock_ids = fields.One2many("dalsil.stock", "product_id", string="Stok Barang")
    total_qty = fields.Float(digits=(10,2), string="Total Jumlah Barang", compute="_get_total_qty", store=True)
    active = fields.Boolean("Is Active ?", default=True)

    @api.depends("stock_ids", "stock_ids.qty")
    def _get_total_qty(self):
        for record in self:
            if len(record.stock_ids) > 0:
                record.total_qty = sum(record.stock_ids.mapped("qty"))
            else:
                record.total_qty = 0.0