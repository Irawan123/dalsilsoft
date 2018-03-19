from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, time, timedelta
import xlwt

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

JENIS_INVOICE = (
    ("purchase", _("Purchase")),
    ("invoice", _("Invoice"))
)

MONTH = (
    ("1", _("January")),
    ("2", _("February")),
    ("3", _("March")),
    ("4", _("April")),
    ("5", _("May")),
    ("6", _("June")),
    ("7", _("July")),
    ("8", _("August")),
    ("9", _("September")),
    ("10", _("October")),
    ("11", _("November")),
    ("12", _("December"))
)

DICT_MONTH = {
    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

class ReportInvoice(models.TransientModel):
    """
    Wizard model untuk membuat laporan stock
    """
    _name = "dalsil.wiz_report_invoice"
    # _inherit = "ss.wizard"
    _description = "Wizard Generate Report Stock"

    product_id = fields.Many2one("product.product", 'Product', domain=[('active', '=', True)])
    partner_id = fields.Many2one("res.partner", "Customer / Vendor", domain="[('active', '=', True), '|', ('customer', '=', True), ('supplier', '=', True)]")
    jenis_inv = fields.Selection(JENIS_INVOICE, "Jenis Invoice")
    month = fields.Selection(MONTH, "Bulan")
    year = fields.Char("Year", size=4)

    #################### Button ####################
    def generate_excel(self):
        """
        Membuatkan journal untuk pembayran expense
        """
        self.ensure_one()
        style_header = xlwt.easyxf('font: height 240, bold on')
        style_bold = xlwt.easyxf('font: bold on; align: horz center; '
                                 'borders: left thin, top thin, bottom thin, right thin')
        style_table = xlwt.easyxf('borders: left thin, bottom thin, right thin')

        wb = xlwt.Workbook("UTF-8")
        ws = wb.add_sheet('Laporan Invoice')

        y = 0
        x = 0

        ws.col(x).width = 800
        ws.col(x+1).width = 4200
        ws.col(x+2).width = 4200

        ws.write(y, x, 'LAPORAN INVOICE', style=style_header)
        y += 1
        ws.write(y, x, '{} {}'.format(DICT_MONTH[self.month], self.year), style=style_header)
        y += 2

        ws.write(y, x, 'Product', style=xlwt.easyxf('font: bold on'))
        ws.write(y, x+2, str(self.product_id.name))
        y += 1
        ws.write(y, x, 'Pembeli / Penjual', style=xlwt.easyxf('font: bold on'))
        ws.write(y, x+2, str(self.partner_id.name))
        y += 2

        ws.write(y, x, "No.", style=style_bold)
        ws.write(y, x+1, "No Dokumen", style=style_bold)
        ws.write(y, x+2, "Tanggal Invoice", style=style_bold)
        ws.write(y, x+3, "Status Dokumen", style=style_bold)
        ws.write(y, x+4, "Sales", style=style_bold)
        ws.write(y, x+5, "Qty", style=style_bold)
        ws.write(y, x+6, "Harga", style=style_bold)
        ws.write(y, x+7, "Subtotal", style=style_bold)
        y += 1

        year = int(self.year)
        month = int(self.month) + 1
        if month == 13:
            month = 1
            year += 1
        domain = [
            ("invoice_id.date_invoice", ">=", "{}-{}-01 00:00:00".format(self.year, self.month.zfill(2))),
            ("invoice_id.date_invoice", "<", "{}-{}-01 00:00:00".format(year, str(month).zfill(2))),
            ("invoice_id.state", "!=", "cancel")
        ]
        if self.product_id:
            domain.append(("product_id", "=", self.product_id.id))
        if self.partner_id:
            domain.append(("invoice_id.partner_id", "=", self.partner_id.id))
        if self.jenis_inv:
            domain.append(("invoice_id.jenis_inv", "=", self.jenis_inv))

        invoice_line_ids = self.env["account.invoice.line"].sudo().search(domain, order="create_date ASC")
        no_urut = 1
        grand_total = 0
        grand_qty = 0
        for invoice_line_id in invoice_line_ids:
            ws.write(y, x, no_urut, style=style_table)
            ws.write(y, x+1, invoice_line_id.invoice_id.nomor_urut, style=style_table)
            ws.write(y, x+2, invoice_line_id.invoice_id.date_invoice, style=style_table)
            ws.write(y, x+3, invoice_line_id.invoice_id.state, style=style_table)
            ws.write(y, x+4, invoice_line_id.invoice_id.sales_id.name, style=style_table)
            ws.write(y, x+5, invoice_line_id.quantity, style=style_table)
            ws.write(y, x+6, invoice_line_id.price_unit, style=style_table)
            ws.write(y, x+7, invoice_line_id.price_subtotal, style=style_table)
            grand_total += invoice_line_id.price_subtotal
            grand_qty += invoice_line_id.quantity
            no_urut += 1
            y += 1
        ws.write(y, x+4, "Total Jumlah", style=style_table)
        ws.write(y, x+5, grand_qty, style=style_table)
        ws.write(y, x+6, "Total", style=style_table)
        ws.write(y, x+7, grand_total, style=style_table)

        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        return self.env["ss.download"].download(
            "Laporan_Invoice_{}.xls".format(datetime.today().strftime("%d%m%Y_%H %M")),
            data
        )