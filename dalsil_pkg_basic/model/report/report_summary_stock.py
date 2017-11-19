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

class ReportSummaryStock(models.TransientModel):
    """
    Wizard model untuk membuat laporan stock summary
    """
    _name = "dalsil.wiz_report_stock_summary"
    _description = "Wizard Generate Report Stock Summary"

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

        ws.write(y, x, 'LAPORAN SUMMARY STOCK', style=style_header)
        y += 1
        ws.write(y, x, '{} {}'.format(DICT_MONTH[self.month], self.year), style=style_header)
        y += 2

        ws.write(y, x, "Location", style=style_bold)
        ws.write(y, x+1, "Product", style=style_bold)
        ws.write(y, x+2, "Stock", style=style_bold)
        ws.write(y, x+3, "Inventory Value", style=style_bold)
        y += 1

        now = fields.Datetime.from_string(fields.Datetime.now())
        cur_month = int(now.strftime("%m"))
        cur_year = int(now.strftime("%Y"))
        if cur_month == int(self.month) and cur_year == int(self.year):
            location_ids = self.env["stock.location"].sudo().search([
                ("usage", "=", 'internal'),
                ("active", "=", True)
            ])
            for location_id in location_ids:
                quant_ids = self.env["stock.quant"].sudo().search([
                    ("location_id", "=", location_id.id)
                ])
                dict_quant = {}
                for quant_id in quant_ids:
                    key = quant_id.product_id
                    if key in dict_quant:
                        dict_quant[key]['qty'] += quant_id.qty
                        dict_quant[key]['cost'] += quant_id.cost
                    else:
                        dict_quant[key] = {
                            'qty': quant_id.qty,
                            'cost': quant_id.cost
                        }
                for key, quant in dict_quant.iteritems():
                    ws.write(y, x, location_id.name, style=style_table)
                    ws.write(y, x+1, key.name, style=style_table)
                    ws.write(y, x+2, quant['qty'], style=style_table)
                    ws.write(y, x+3, quant['cost'], style=style_table)
                    y += 1
        else:
            year = int(self.year)
            month = int(self.month) + 1
            if month == 13:
                month = 1
                year += 1
            start_stock_id = self.env["dalsil.start_stock"].sudo().search([
                ("month", "=", str(month)),
                ("year", "=", str(year))
            ], limit=1)
            if not start_stock_id:
                raise ValidationError("Stock awal bulan {} {} tidak ditemukan".format(DICT_MONTH[str(month)], year))
        
            for line_id in start_stock_id.line_ids:
                ws.write(y, x, line_id.location_id.name, style=style_table)
                ws.write(y, x+1, line_id.product_id.name, style=style_table)
                ws.write(y, x+2, line_id.stock, style=style_table)
                ws.write(y, x+3, line_id.inventory_value, style=style_table)
                y += 1

        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        
        return self.env["ss.download"].download(
            "Laporan_Summary_Stock_{}.xls".format(datetime.today().strftime("%d%m%Y_%H %M")),
            data
        )