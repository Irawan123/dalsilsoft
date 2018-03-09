from odoo import models, fields, api


class OutgoingCheckGiroLine(models.Model):
    """
    Detil check giro keluar
    """
    _name = "dalsil.check_giro.out.line"

    parent_id = fields.Many2one("dalsil.check_giro.out", ondelete="CASCADE")
    vendor_id = fields.Many2one("res.partner", related="parent_id.vendor_id")

    invoice_id = fields.Many2one(
        "account.invoice", "Number",
        domain="[('state', '=', 'open'), ('partner_id', '=', vendor_id), ('type', 'in', ('in_invoice', 'in_refund'))]"
    )
    bill_date = fields.Date("Bill Date", compute="_get_inv_data", store=True)
    due_date = fields.Date("Due Date", compute="_get_inv_data", store=True)
    source_doc = fields.Char("Source Document", compute="_get_inv_data", store=True)
    total = fields.Float("Total", (15, 2), compute="_get_inv_data", store=True)
    to_pay = fields.Float("To Pay", (15, 2), compute="_get_inv_data", store=True)

    payment = fields.Float("Payment Amount", (15, 2), required=True)

    @api.depends("invoice_id")
    def _get_inv_data(self):
        """
        Mengambil data invoice
        """
        for record in self:
            record.bill_date = record.invoice_id.date_invoice
            record.due_date = record.invoice_id.date_due
            record.source_doc = record.invoice_id.origin
            record.total = record.invoice_id.amount_total_signed
            record.to_pay = record.invoice_id.residual_signed

    @api.onchange("invoice_id")
    def _onchange_to_pay(self):
        """
        Mengisikan nilai default payment amount
        """
        self.payment = self.to_pay
