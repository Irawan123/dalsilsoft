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
    product_id = fields.Many2one("product.product", "Product", domain=[('type', '=', 'product'), ('active', '=', True)])
    uom_id = fields.Many2one("product.uom", "Unit of Measure", readonly=True)
    qty = fields.Float("Quantity", digits=(20,2))
    unit_price = fields.Float("Unit Price", digits=(20,2))
    invoice_line_tax_id = fields.Many2one('account.tax', string='Taxes', 
        domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)])
    sub_total = fields.Float("Sub Total", digits=(20,2), compute="_get_sub_total")
    account_id = fields.Many2one("account.account", "Account")
    
    @api.depends("qty", "unit_price", "invoice_line_tax_id")
    def _get_sub_total(self):
        """
        Menghitung Nilai Sub Total
        """
        for record in self:
            taxes = False
            if record.invoice_line_tax_id:
                taxes = record.invoice_line_tax_id.compute_all(record.unit_price, None, record.qty, product=record.product_id, partner=record.parent_id.rent_truck_id.customer_rent_id)
            record.sub_total = taxes['total_excluded'] if taxes else record.qty * record.unit_price
