from odoo import models, fields, api


class StartStockLine(models.Model):
    """
    Detil Start Stock Line
    """
    _name = "dalsil.start_stock.line"

    parent_id = fields.Many2one("dalsil.start_stock", ondelete="CASCADE")
    product_id = fields.Many2one("product.product", "Product", domain=[('type', '=', 'product'), ('active', '=', True)])
    uom_id = fields.Many2one("product.uom", "Unit of Measure", compute="_get_data_product", store=True)
    stock = fields.Float("Stock", digits=(20,2))
    location_id = fields.Many2one("stock.location", "Location", domain=[('usage','=','internal'), ('active', '=', True)])
    inventory_value = fields.Float("Inventory Value", digits=(20,2))

    @api.depends("product_id")
    def _get_data_product(self):
        for record in self:
            record.uom_id = record.product_id.uom_id