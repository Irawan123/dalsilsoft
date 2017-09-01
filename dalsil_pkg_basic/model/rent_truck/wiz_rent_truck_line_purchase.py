from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date, time, timedelta

class WizRentTruckLinePurchase(models.TransientModel):
    """
    Wizard model untuk mengisikan data2 yang dibutuhkan untuk membuat account invoice
    """
    _name = "dalsil.wiz_rent_truck.line_pur"
    _inherit = "ss.wizard"
    _description = "Wizard Generate Account Invoice"

    parent_id = fields.Many2one("dalsil.wiz_rent_truck", "Wizard Rent Truck")
    product_id = fields.Many2one("product.product", "Product")
    uom_id = fields.Many2one("product.uom", "Unit of Measure", related="product_id.uom_id", readonly=True)
    qty = fields.Float("Quantity", digits=(20,2))
    unit_price = fields.Float("Unit Price", digits=(20,2))
    sub_total = fields.Float("Sub Total", digits=(20,2), compute="_get_sub_total")

    @api.depends("qty", "unit_price")
    def _get_sub_total(self):
        """
        Menghitung Nilai Sub Total
        """
        for record in self:
            record.sub_total = record.qty * record.unit_price