from odoo import models, fields, api


class JournalVoucherLine(models.Model):
    """
    Detil other deposit
    """
    _name = "dalsil.journal_voucher.line"

    parent_id = fields.Many2one("dalsil.journal_voucher", ondelete="CASCADE")
    account_id = fields.Many2one('account.account', 'Account Name', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner', domain=['|', ('parent_id', '=', False),
                                                                   ('company_id', '=', True)])
    memo = fields.Char('Memo')
    debit = fields.Integer('Debit', default=0.0)
    credit = fields.Integer('Credit', default=0.0)
