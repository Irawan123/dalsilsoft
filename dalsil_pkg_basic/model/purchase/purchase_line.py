__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PurchaseLine(models.Model):
    _name = "dalsil.purchase.line"
    _inherit = "ss.model"
    _description = "Purchase Line"

    parent_id = fields.Many2one("dalsil.purchase", "Parent", ondelete="cascade")
    product_id = fields.Many2one("dalsil.product", "Barang")
    qty = fields.Float(digits=(10,2), string="Jumlah Barang")
    unit_price = fields.Float(digits=(20,2), string="Harga Barang")
    sub_total = fields.Float(digits=(20,2), string="Sub Total", compute="_get_sub_total", store=True)

    @api.depends("qty", "unit_price")
    def _get_sub_total(self):
        for record in self:
            record.sub_total = record.qty * record.unit_price