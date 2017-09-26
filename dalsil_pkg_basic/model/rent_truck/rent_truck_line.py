from odoo import models, fields, api


class RentTruckLine(models.Model):
    """
    Detil rent truck
    """
    _name = "dalsil.rent_truck.line"

    parent_id = fields.Many2one("dalsil.rent_truck.in", ondelete="CASCADE")
    product_id = fields.Many2one("product.product", "Product")
    uom_id = fields.Many2one("product.uom", "Unit of Measure", compute="_get_data_product", store=True)
    qty = fields.Float("Quantity", digits=(20,2))
    cost = fields.Float("Cost", digits=(20,2))
    sub_total = fields.Float("Sub Total", digits=(20,2), compute="_get_sub_total", store=True)

    @api.depends("qty", "cost")
    def _get_sub_total(self):
        """
        Menghitung Nilai Sub Total
        """
        for record in self:
            record.sub_total = record.qty * record.cost

    @api.depends("product_id")
    def _get_data_product(self):
        for record in self:
            record.uom_id = record.product_id.uom_id