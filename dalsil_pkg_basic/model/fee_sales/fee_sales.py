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
    _seq_code = ("name", "dalsil_fee_sales")

    name = fields.Char("Name")
    sales_id = fields.Many2one("res.partner", "Sales")
    invoice_id = fields.Many2one("account.invoice", "Invoice")
    due_date = fields.Date("Due Date")
    fee_sales = fields.Float("Fee Sales", digits=(20,2))
    note = fields.Text("Note")
    state = fields.Selection(STATE, "State")