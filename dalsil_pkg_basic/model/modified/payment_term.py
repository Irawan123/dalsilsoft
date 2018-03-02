from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PaymentTerm(models.Model):
    """
    Account Invoice
    """
    _inherit = "account.payment.term"

    due_days = fields.Integer("Hari")