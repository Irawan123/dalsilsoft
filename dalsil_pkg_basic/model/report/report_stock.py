from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, time, timedelta
import xlwt

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

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

class ReportStock(models.TransientModel):
    """
    Wizard model untuk membuat laporan stock
    """
    _name = "dalsil.wiz_report_stock"
    # _inherit = "ss.wizard"
    _description = "Wizard Generate Report Stock"

    product_id = fields.Many2one("product.product", 'Product', domain=[('type', '=', 'product'), ('active', '=', True)])
    location_id = fields.Many2one("stock.location", 'Location', domain=[('usage','=','internal'), ('active', '=', True)])
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
        ws = wb.add_sheet('Laporan Stock')

        y = 0
        x = 0

        ws.col(x).width = 4200
        ws.col(x+1).width = 4200
        ws.col(x+2).width = 4200

        ws.write(y, x, 'LAPORAN STOCK', style=style_header)
        y += 1
        ws.write(y, x, '{} {}'.format(DICT_MONTH[self.month], self.year), style=style_header)
        y += 2

        ws.write(y, x, 'Product', style=xlwt.easyxf('font: bold on'))
        ws.write(y, x+1, str(self.product_id.name))
        y += 1
        ws.write(y, x, 'Location', style=xlwt.easyxf('font: bold on'))
        ws.write(y, x+1, str(self.location_id.name))
        y += 2

        ws.write(y, x, "Tanggal", style=style_bold)
        ws.write(y, x+1, "Perusahaan", style=style_bold)
        ws.write(y, x+2, "Keterangan", style=style_bold)
        ws.write(y, x+3, "Beli", style=style_bold)
        ws.write(y, x+4, "Jual", style=style_bold)
        ws.write(y, x+5, "Stock", style=style_bold)
        y += 1

        start_stock_id = self.env["dalsil.start_stock"].sudo().search([
            ("month", "=", self.month),
            ("year", "=", self.year)
        ], limit=1)
        if not start_stock_id:
            raise ValidationError("Stock awal bulan yang dipilih tidak ditemukan")
        start_stock_line_id = self.env["dalsil.start_stock.line"].sudo().search([
            ("parent_id", "=", start_stock_id.id),
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id)
        ], limit=1)
        stock_awal = start_stock_line_id.stock
        if not start_stock_line_id:
            raise ValidationError("Stock awal produk dan lokasi yang dipilih tidak ditemukan")
        ws.write(y, x, "{}-{}-{}".format(self.year, self.month.zfill(2), "01"), style=style_table)
        ws.write(y, x+1, "Sinar Rejeki Putra", style=style_table)
        ws.write(y, x+2, "Stock Awal Bulan", style=style_table)
        ws.write(y, x+3, "", style=style_table)
        ws.write(y, x+4, "", style=style_table)
        ws.write(y, x+5, stock_awal, style=style_table)
        y += 1

        year = int(self.year)
        month = int(self.month) + 1
        if month == 13:
            month = 1
            year += 1
        stock_move_ids = self.env["stock.move"].sudo().search([
            ("product_id", "=", self.product_id.id),
            ("date", ">=", "{}-{}-01 00:00:00".format(self.year, self.month.zfill(2))),
            ("date", "<", "{}-{}-01 00:00:00".format(year, str(month).zfill(2))),
            '|',
            ("location_dest_id", "=", self.location_id.id),
            ("location_id", "=", self.location_id.id)
        ], order="date ASC")
        for stock_move in stock_move_ids:
            beli = ""
            jual = ""
            if stock_move.location_id.id == self.location_id.id:
                jual = stock_move.product_uom_qty
                stock_awal -= jual
            else:
                beli = stock_move.product_uom_qty
                stock_awal += beli
            ws.write(y, x, stock_move.date, style=style_table)
            ws.write(y, x+1, stock_move.acc_inv_id.partner_id.name, style=style_table)
            ws.write(y, x+2, stock_move.acc_inv_id.number, style=style_table)
            ws.write(y, x+3, beli, style=style_table)
            ws.write(y, x+4, jual, style=style_table)
            ws.write(y, x+5, stock_awal, style=style_table)
            y += 1

        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        return self.env["ss.download"].download(
            "Laporan_Stock_{}.xls".format(datetime.today().strftime("%d%m%Y_%H %M")),
            data
        )