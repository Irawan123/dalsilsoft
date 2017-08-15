__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Stock(models.Model):
    _name = "dalsil.stock"
    _inherit = "ss.model"
    _description = "Stock"

    product_id = fields.Many2one("dalsil.product", "Barang")
    qty = fields.Float(digits=(10,2), string="Jumlah Barang")
    location_id = fields.Many2one("dalsil.location", "Lokasi")

    @api.model
    def add_stock(self, product_id, location_id, qty):
        stock = self.env['dalsil.stock']
        if not isinstance(product_id, int):
            product_id = product_id.id
        if not isinstance(location_id, int):
            location_id = location_id.id
        stock = stock.search([
            ('product_id', '=', product_id),
            ('location_id', '=' location_id)
        ])
        if stock:
            stock.qty += qty
        else:
            stock.create({
                "product_id": product_id,
                "qty": qty,
                "location_id": location_id
            })

    @api.model
    def sub_stock(self, product_id, location_id, qty):
        stock = self.env['dalsil.stock']
        if not isinstance(product_id, int):
            product_id = product_id.id
        if not isinstance(location_id, int):
            location_id = location_id.id
        stock = stock.search([
            ('product_id', '=', product_id),
            ('location_id', '=' location_id)
        ])
        if not stock or stock.qty - qty < 0:
            raise ValidationError("Stock tidak mencukupi")
        stock.qty += qty