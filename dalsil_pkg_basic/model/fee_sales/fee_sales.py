from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

STATE = (
    ("draft", _("Draft")),
    ("open", _("Open")),
    ("paid", _("Paid")),
    ("expired", _("Expired"))
)

class FeeSales(models.Model):
    """
    Rent Truck
    """
    _name = "dalsil.fee_sales"
    _inherit = "ss.model"
    _state_start = STATE[0][0]
    _seq_code = {"name": "dalsil_fee_sales"}

    name = fields.Char("Name")
    sales_id = fields.Many2one("res.partner", "Sales")
    invoice_id = fields.Many2one("account.invoice", "Invoice")
    invoice_line_id = fields.Many2one("account.invoice.line", "Invoice Line")
    due_date = fields.Date("Due Date")
    fee_sales = fields.Float("Fee Sales", digits=(20,2))
    note = fields.Text("Note")
    state = fields.Selection(STATE, "State")
    is_created_invoice = fields.Boolean("Is Created Invoice", default=False)

    @api.multi
    def to_open(self):
        for record in self:
            record = record.suspend_security()
            if record.state not in [STATE[0][0], STATE[3][0]]:
                continue
            record._cstate(STATE[1][0])

    @api.multi
    def to_expired(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[0][0]:
                continue
            record._cstate(STATE[3][0])

    @api.multi
    def to_paid(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[1][0]:
                continue
            record._cstate(STATE[2][0])

    @api.model
    def cron_expired_fee_sales(self):
        fee_sales_ids = self.env["dalsil.fee_sales"].suspend_security().search([
            ("state", "=", 'draft'),
            ("due_date", "<", fields.Date.today())
        ])
        fee_sales_ids.to_expired()