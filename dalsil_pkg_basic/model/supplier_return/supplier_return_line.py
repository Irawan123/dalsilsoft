from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SupllierReturnLine(models.Model):
    """
    Supplier Return Line
    """
    _name = "dalsil.supplier_return.line"
    _inherit = "ss.model"

    parent_id = fields.Many2one("dalsil.supplier_return", "Supplier Return")
    product_id = fields.Many2one("product.product", "Product", domain=[('type', '=', 'product'), ('active', '=', True)])
    qty = fields.Float("Quantity Purchase", digits=(20,2))
    qty_return = fields.Float("Quantity Return", digits=(20,2))
    unit_price = fields.Float("Unit Price", digits=(20,2))
    invoice_line_tax_ids = fields.Many2many('account.tax', 'dalsil_sup_ret_tax_rel',string='Taxes')
    sub_total = fields.Float("Sub Total", digits=(20,2), compute="_get_sub_total")
    account_id = fields.Many2one("account.account", "Account")

    @api.depends("qty_return", "unit_price", "invoice_line_tax_ids")
    def _get_sub_total(self):
        """
        Menghitung Nilai Sub Total
        """
        for record in self:
            taxes = False
            if record.invoice_line_tax_ids:
                taxes = record.invoice_line_tax_ids.compute_all(record.unit_price, None, record.qty_return, product=record.product_id, partner=record.parent_id.partner_id)
            record.sub_total = taxes['total_excluded'] if taxes else record.qty_return * record.unit_price