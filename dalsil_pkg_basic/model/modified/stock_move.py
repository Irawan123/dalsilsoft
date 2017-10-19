from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class StockMove(models.Model):
    """
    Stock Move
    """
    _inherit = "stock.move"

    acc_inv_id = fields.Many2one("account.invoice", "Invoice")
    partner_id = fields.Many2one("res.partner", "Partner")