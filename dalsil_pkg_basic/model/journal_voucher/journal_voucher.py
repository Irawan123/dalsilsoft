from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

STATE = (
    ("draft", _("Draft")),
    ("post", _("Posted")),
    ("cancel", _("Cancelled")),
)


class JournalVoucher(models.Model):
    """
    Bukti Journal Umum/ Journal Voucher
    """
    _name = "dalsil.journal_voucher"
    _inherit = "ss.model"
    _state_start = STATE[0][0]
    _seq_code = {"name": "dalsil.journal_voucher"}

    name = fields.Char('Voucher No.')
    date = fields.Date('Date', required=True, default=fields.Date.today())
    description = fields.Text('Description')
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    state = fields.Selection(STATE, 'State')

    line_ids = fields.One2many('dalsil.journal_voucher.line', 'parent_id', 'Items')
    total_debit = fields.Integer('Total Debit', store=True, compute='_get_total')
    total_credit = fields.Integer('Total Credit', store=True, compute='_get_total')
    move_id = fields.Many2one('account.move', 'Journal Entry', ondelete='restrict')

    @api.depends('line_ids', 'line_ids.debit', 'line_ids.credit')
    def _get_total(self):
        for record in self:
            record.total_debit = sum(l.debit for l in record.line_ids)
            record.total_credit = sum(l.credit for l in record.line_ids)

    @api.multi
    def to_post(self):
        """
        create journal & jadikan post
        """
        move_env = self.env["account.move"]
        for record in self:
            lines = []
            for line in record.line_ids:
                lines.append((0, 0, {
                    "name": "/",
                    "account_id": line.account_id.id,
                    "partner_id": line.partner_id.id,
                    "credit": line.credit,
                    "debit": line.debit,
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
