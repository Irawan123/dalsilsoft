from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

STATE = (
    ("draft", _("Draft")),
    ("post", _("Posted")),
    ("cancel", _("Cancelled")),
)


class OtherPayment(models.Model):
    """
    Other Payment/ Pengeluaran cash bank
    """
    _name = "dalsil.cash_bank.op"
    _inherit = "ss.model"
    _state_start = STATE[0][0]
    _seq_code = {"name": "dalsil.cash_bank.op"}

    name = fields.Char('Voucher No.')
    date = fields.Date('Date', required=True, default=fields.Date.today())
    memo = fields.Text('Memo')
    amount = fields.Integer('Amount')
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    state = fields.Selection(STATE, 'State')

    account_id = fields.Many2one('account.account', 'Paid From', required=True,
                                 domain="[('user_type_id.type', 'in', ['liquidity'])]")

    line_ids = fields.One2many('dalsil.cash_bank.op.line', 'parent_id', 'Items')
    total_pay = fields.Integer('Total', store=True, compute='_get_total')
    move_id = fields.Many2one('account.move', 'Journal Entry', ondelete='restrict')

    @api.depends('line_ids', 'line_ids.amount')
    def _get_total(self):
        for record in self:
            record.total_pay = sum(l.amount for l in record.line_ids)

    @api.multi
    def to_post(self):
        """
        create journal & jadikan post
        """
        move_env = self.env["account.move"]
        for record in self:
            lines = [(0, 0, {
                "account_id": record.account_id.id,
                "name": "/",
                "credit": record.amount,
                "debit": 0,
                "date_maturity": record.date
            })]
            for line in record.line_ids:
                lines.append((0, 0, {
                    "name": "/",
                    "account_id": line.account_id.id,
                    "partner_id": line.partner_id.id,
                    "credit": 0,
                    "debit": line.amount,
                    "date_maturity": record.date
                }))
            move_id = move_env.create({
                "journal_id": record.journal_id.id,
                "date": record.date,
                "line_ids": lines,
                "ref": record.name
            })
            move_id.post()

            record.move_id = move_id

        return self._cstate(STATE[1][0])
