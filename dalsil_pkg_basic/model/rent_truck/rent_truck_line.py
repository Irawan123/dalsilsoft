from odoo import models, fields, api


class RentTruckLine(models.Model):
    """
    Detil rent truck
    """
    _name = "dalsil.rent_truck.line"

    parent_id = fields.Many2one("dalsil.rent_truck.in", required=True, ondelete="CASCADE")
    product_id = fields.Many2one("product.product", "Product")
    uom_id = fields.Many2one("product.uom", "Unit of Measure", related="product_id.uom_id", readonly=True)
    qty = fields.Many2one("Quantity", digits=(20,2))
    cost = fields.Many2one("Cost", digits=(20,2))
    sub_total = fields.Integer("Sub Total", compute="_get_sub_total", store=True)

    @api.depends("qty", "cost")
    def _get_sub_total(self):
        """
        Menghitung Nilai Sub Total
        """
        for record in self:
            record.sub_total = record.qty * record.cost