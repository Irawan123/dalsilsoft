from odoo import models, fields, api


class OtherPaymentLine(models.Model):
    """
    Detil other deposit
    """
    _name = "dalsil.cash_bank.op.line"

    parent_id = fields.Many2one("dalsil.cash_bank.op", ondelete="CASCADE")
    account_id = fields.Many2one('account.account', 'Account Name', required=True,
                                 domain="[('user_type_id.type', 'in', ['payable', 'other'])]")
    partner_id = fields.Many2one('res.partner', 'Partner', domain=['|', ('parent_id', '=', False),
                                                                   ('company_id', '=', True)])
    memo = fields.Char('Memo')
    amount = fields.Integer('Amount', default=0.0)
