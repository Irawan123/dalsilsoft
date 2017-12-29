from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, time, timedelta
import xlwt

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

STATE = (
    ("draft", _("Draft")),
    ("open", _("Open")),
    ("paid", _("Paid")),
    ("cancel", _("Cancel"))
)

JENIS_INVOICE = (
    ("sangu", _("Sangu")),
    ("rent", _("Rent"))
)

class GenPaymentInvoice(models.Model):
    """
    Generate Payment Invoice
    """
    _name = "dalsil.gen_pay_inv"
    _inherit = "ss.model"
    _state_start = STATE[0][0]
    _seq_code = {"name": "dalsil_gen_pay_inv"}

    name = fields.Char("Name")
    jenis_inv = fields.Selection(JENIS_INVOICE, "Jenis Invoice", default=JENIS_INVOICE[0][0])
    partner_id = fields.Many2one("res.partner", "Partner", domain="[('active', '=', True)]")
    invoice_ids = fields.Many2many("account.invoice", "dalsil_pay_inv_gen_rel", string="Payment Invoice",
        domain="[('state', '=', 'open'), ('jenis_inv', '=', jenis_inv), ('partner_id', '=', partner_id)]")
    journal_id = fields.Many2one('account.journal', string='Journal')
    note = fields.Text("Note")
    state = fields.Selection(STATE, "State")
    total_pay_invoice = fields.Float("Total Payment Invoice", digits=(20,2), compute="_get_total", store=True)

    @api.depends("invoice_ids", "invoice_ids.amount_total")
    def _get_total(self):
        for record in self:
            record.total_pay_invoice = sum(record.invoice_ids.mapped("amount_total"))

    @api.onchange("jenis_inv", "partner_id")
    def _onchange_sales(self):
        self.invoice_ids = [(5, 0)]
        inv_ids = self.env["account.invoice"].suspend_security().search([
            ("partner_id", "=", self.partner_id.id),
            ("state", "=", 'open'),
            ("jenis_inv", "=", self.jenis_inv),
            ("is_generated_pay_inv", "=", False)
        ])
        self.invoice_ids = inv_ids
        ret = {'domain': {'partner_id': [('active', '=', True)]}}
        if self.jenis_inv == 'sangu':
            ret = {'domain': {'partner_id': [('active', '=', True), ("is_driver", "=", True)]}}
        elif self.jenis_inv == 'rent':
            ret = {'domain': {'partner_id': [('active', '=', True), ("customer", "=", True)]}}
        return ret

    @api.multi
    def to_open(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[0][0]:
                continue
            for invoice_id in record.invoice_ids:
                if invoice_id.is_generated_pay_inv == True:
                    raise ValidationError("Payment Invoice no {} sudah digenerate. Untuk melanjutkan harap hapus payment invoice tersebut.".format(invoice_id.number))
                if invoice_id.state != 'open':
                    raise ValidationError("Invoice no {} tidak berstatus open.".format(invoice_id.number))
            record.invoice_ids.write({
                "is_generated_pay_inv": True
            })
            record._cstate(STATE[1][0])

    @api.multi
    def to_paid(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[1][0]:
                continue
            for invoice_id in record.invoice_ids:
                invoice_id.pay_and_reconcile(record.journal_id)
            record._cstate(STATE[2][0])

    @api.multi
    def to_cancel(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[0][0]:
                continue
            record.invoice_ids.write({
                "is_generated_pay_inv": False
            })
            record._cstate(STATE[3][0])

    @api.multi
    def to_print(self):
        self.ensure_one()
        style_header = xlwt.easyxf('font: height 240, bold on')
        style_bold = xlwt.easyxf('font: bold on; align: horz center; '
                                 'borders: left thin, top thin, bottom thin, right thin')
        style_table = xlwt.easyxf('borders: left thin, bottom thin, right thin')

        wb = xlwt.Workbook("UTF-8")
        ws = wb.add_sheet('Payment Invoice')

        y = 0
        x = 0

        ws.col(x).width = 4200
        ws.col(x+1).width = 4200
        ws.col(x+2).width = 4200

        ws.write(y, x, 'LAPORAN Payment Invoice', style=style_header)
        y += 1
        ws.write(y, x, 'Tanggal Print {}'.format(fields.Date.today()), style=xlwt.easyxf('font: bold on'))
        y += 1
        ws.write(y, x, 'Partner: {}'.format(self.partner_id.name), style=style_header)
        y += 2

        ws.write(y, x, "Tanggal Invoice", style=style_bold)
        ws.write(y, x+1, "Document Invoice", style=style_bold)
        ws.write(y, x+2, "Keterangan", style=style_bold)
        ws.write(y, x+3, "Tanggal Pembayaran", style=style_bold)
        ws.write(y, x+4, "Subtotal", style=style_bold)
        y += 1
        grand_total_fee = 0
        for inv_id in self.invoice_ids:
            keterangan = ""
            for line_id in inv_id.invoice_line_ids:
                keterangan += "{},".format(line_id.name)
            grand_total_fee += inv_id.amount_total
            ws.write(y, x, inv_id.date_invoice, style=style_table)
            ws.write(y, x+1, inv_id.number, style=style_table)
            ws.write(y, x+2, keterangan, style=style_table)
            ws.write(y, x+3, inv_id.dt_full_paid, style=style_table)
            ws.write(y, x+4, inv_id.amount_total, style=style_table)
            y += 1
        ws.write(y, x+3, "Total Payment Invoice:", style=style_table)
        ws.write(y, x+4, grand_total_fee, style=style_table)
        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        return self.env["ss.download"].download(
            "Laporan_{}_Inv_Payment_{}_{}.xls".format(self.jenis_inv, self.partner_id.name, datetime.today().strftime("%d%m%Y")),
            data
        )