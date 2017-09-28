from odoo import models, fields, api


class OtherDepositLine(models.Model):
    """
    Detil other deposit
    """
    _name = "dalsil.cash_bank.od.line"

    parent_id = fields.Many2one("dalsil.cash_banl.od", ondelete="CASCADE")
    account_id = fields.Many2one('account.account', 'Account Name', required=True,
                                 domain="[('user_type_id.type', 'in', ['receivable', 'other'])]")
    partner_id = fields.Many2one('res.partner', 'Partner', domain=['|', ('parent_id', '=', False),
                                                                   ('company_id', '=', True)])
    memo = fields.Char('Memo')
    amount = fields.Integer('Amount', default=0.0)
