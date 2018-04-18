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

class GenFeeSales(models.Model):
    """
    Generate Fee Sales
    """
    _name = "dalsil.gen_fee_sales"
    _inherit = "ss.model"
    _state_start = STATE[0][0]
    _seq_code = {"name": "dalsil_gen_fee_sales"}

    name = fields.Char("Name")
    sales_id = fields.Many2one("res.partner", "Sales", domain="[('active', '=', True), ('is_sales', '=', True)]")
    fee_ids = fields.Many2many("dalsil.fee_sales", "dalsil_fee_sales_gen_rel", string="Fee Sales",
        domain="[('sales_id', '=', sales_id), ('state', '=', 'open'), ('is_created_invoice', '=', False)]")
    fee_sales_ids = fields.One2many("dalsil.fee_sales", "gen_fee_sales_id", string="Fee Sales", compute="_get_fee_sales", store=True)
    fee_payment_term_id = fields.Many2one('account.payment.term', string='Fee Payment Terms')
    # fee_invoice_id = fields.Many2one("account.invoice", "Invoice Fee Sales", readonly="1")
    note = fields.Text("Note")
    state = fields.Selection(STATE, "State")
    total_fee_sales = fields.Float("Total Fee Sales", digits=(20,2), compute="_get_total", store=True)

    @api.depends("fee_sales_ids", "fee_sales_ids.fee_sales")
    def _get_total(self):
        for record in self:
            record.total_fee_sales = sum(record.fee_sales_ids.mapped("fee_sales"))

    @api.depends("sales_id")
    def _get_fee_sales(self):
        # self.fee_sales_ids.write({'gen_fee_sales_id': False})
        self.fee_sales_ids = self.env["dalsil.fee_sales"].suspend_security().search([
            ("sales_id", "=", self.sales_id.id),
            ("state", "=", 'open'),
            ("is_created_invoice", "=", False)
        ])
        # if len(fee_sales_ids) > 0:
        #     fee_sales_ids.write({'gen_fee_sales_id': self.id})
        #     import pdb;pdb.set_trace()

    @api.multi
    def to_open(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[0][0]:
                continue
            for fee_id in record.fee_sales_ids:
                if fee_id.is_created_invoice == True:
                    raise ValidationError("Fee Sales no {} sudah mempunyai account invoice.".format(fee_id.name))
            record.fee_sales_ids.write({
                "is_created_invoice": True
            })

            setting = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
            vals = {
                'jenis_inv': "fee",
                'partner_id': record.sales_id.id,
                'origin': record.name,
                'type': 'in_invoice',
                'payment_term_id': record.fee_payment_term_id.id,
                'gen_fee_sales_id': record.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': setting.product_fee.id,
                    'name': 'Fee Sales No ({})'.format(record.name),
                    'quantity': 1.0,
                    'price_unit': sum(record.fee_sales_ids.mapped("fee_sales")),
                    'account_id': setting.fee_acc_id.id
                })]
            }
            self.env['account.invoice'].sudo().create(vals)

            record._cstate(STATE[1][0])

    @api.multi
    def to_paid(self):
        for record in self:
            record = record.suspend_security()
            if record.state != STATE[1][0]:
                continue
            record.fee_sales_ids.to_paid()
            record._cstate(STATE[2][0])

    @api.multi
    def to_print(self):
        self.ensure_one()
        style_header = xlwt.easyxf('font: height 240, bold on')
        style_bold = xlwt.easyxf('font: bold on; align: horz center; '
                                 'borders: left thin, top thin, bottom thin, right thin')
        style_table = xlwt.easyxf('borders: left thin, bottom thin, right thin')

        wb = xlwt.Workbook("UTF-8")
        ws = wb.add_sheet('Fee Sales')

        y = 0
        x = 0

        ws.col(x).width = 4200
        ws.col(x+1).width = 4200
        ws.col(x+2).width = 4200

        ws.write(y, x, 'LAPORAN FEE SALES', style=style_header)
        y += 1
        ws.write(y, x, 'Tanggal Print {}'.format(fields.Date.today()), style=xlwt.easyxf('font: bold on'))
        y += 1
        ws.write(y, x, 'Sales: {}'.format(self.sales_id.name), style=style_header)
        y += 2

        ws.write(y, x, "Tanggal Invoice", style=style_bold)
        ws.write(y, x+1, "Document Invoice", style=style_bold)
        ws.write(y, x+2, "Tanggal Jatuh Tempo", style=style_bold)
        ws.write(y, x+3, "Tanggal Pembayaran", style=style_bold)        
        ws.write(y, x+4, "Barang", style=style_bold)
        ws.write(y, x+5, "Jumlah", style=style_bold)
        ws.write(y, x+6, "Fee Per Barang", style=style_bold)
        ws.write(y, x+7, "Subtotal Fee", style=style_bold)
        y += 1
        grand_total_fee = 0
        for fee_id in self.fee_sales_ids:
            grand_total_fee += fee_id.fee_sales
            ws.write(y, x, fee_id.invoice_id.date_invoice, style=style_table)
            ws.write(y, x+1, fee_id.invoice_id.number, style=style_table)
            ws.write(y, x+2, fee_id.due_date, style=style_table)
            ws.write(y, x+3, fee_id.invoice_id.dt_full_paid, style=style_table)
            ws.write(y, x+4, fee_id.invoice_line_id.product_id.name, style=style_table)
            ws.write(y, x+5, fee_id.invoice_line_id.quantity, style=style_table)
            ws.write(y, x+6, fee_id.fee_sales / fee_id.invoice_line_id.quantity, style=style_table)
            ws.write(y, x+7, fee_id.fee_sales, style=style_table)
            y += 1
        ws.write(y, x+6, "Total Fee Sales:", style=style_table)
        ws.write(y, x+7, grand_total_fee, style=style_table)
        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        return self.env["ss.download"].download(
            "Laporan_Fee_Sales_{}_{}.xls".format(self.sales_id.name, datetime.today().strftime("%d%m%Y")),
            data
        )