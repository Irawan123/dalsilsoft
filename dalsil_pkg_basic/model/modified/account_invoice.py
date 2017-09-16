from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

JENIS_INVOICE = (
    ("purchase", _("Purchase")),
    ("invoice", _("Invoice")),
    ("sangu", _("Sangu")),
    ("rent", _("Rent")),
    ("fee", _("Fee Sales"))
)

class AccountInvoice(models.Model):
    """
    Account Invoice
    """
    _inherit = "account.invoice"
    sales_id = fields.Many2one("res.partner", "Sales")
    jenis_inv = fields.Selection(JENIS_INVOICE, "Jenis Invoice", default=JENIS_INVOICE[0][0])

    @api.model
    def create(self, vals):
        """
        Mencegah user create kalo state != draft
        """
        acc_inv_id = super(AccountInvoice, self).create(vals)
        if vals['jenis_inv'] == 'invoice':
            self.env['dalsil.fee_sales'].create({
                'sales_id': acc_inv_id.sales_id.id,
                'invoice_id': acc_inv_id.id,
                'due_date': fields.Date.today(),
                'fee_sales': 0,
                'note': ""
            })

        return acc_inv_id