__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Stock(models.Model):
    _name = "dalsil.stock"
    _inherit = "ss.model"
    _description = "Stock"

    product_id = fields.Many2one("dalsil.product", "Barang", ondelete="cascade")
    qty = fields.Float(digits=(10,2), string="Jumlah Barang")
    location_id = fields.Many2one("dalsil.location", "Lokasi")

    @api.model
    def set_stock(self, product_id, location_id, qty):
        stock = self.env['dalsil.stock']
        if not isinstance(product_id, int):
            product_id = product_id.id
        if not isinstance(location_id, int):
            location_id = location_id.id
        stock = stock.search([
            ('product_id', '=', product_id),
            ('location_id', '=' location_id)
        ])
        if stock and stock.qty + qty >= 0:
            stock.qty += qty
        else:
            if qty >= 0:
                stock.create({
                    "product_id": product_id,
                    "qty": qty,
                    "location_id": location_id
                })
            else:
                raise ValidationError("Stock tidak mencukupi")
