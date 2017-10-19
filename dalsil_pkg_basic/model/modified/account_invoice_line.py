from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

JENIS_INVOICE = (
    ("purchase", _("Purchase")),
    ("invoice", _("Invoice")),
    ("sangu", _("Sangu")),
    ("rent", _("Rent")),
    ("fee", _("Fee Sales"))
)

class AccountInvoiceLine(models.Model):
    """
    Account Invoice Line
    """
    _inherit = "account.invoice.line"

    location_id = fields.Many2one("stock.location", "Source Location", domain=[('usage','=','internal'), ('active', '=', True)])
    jenis_inv = fields.Selection(JENIS_INVOICE, "Jenis Invoice", compute="_get_jenis_inv")

    @api.depends("invoice_id")
    def _get_jenis_inv(self):
        for record in self:
            record.jenis_inv = record.invoice_id.jenis_inv