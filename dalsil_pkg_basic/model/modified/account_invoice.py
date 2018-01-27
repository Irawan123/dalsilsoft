from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import xlwt
from datetime import datetime, date, time, timedelta
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

JENIS_INVOICE = (
    ("purchase", _("Purchase")),
    ("invoice", _("Invoice")),
    ("sangu", _("Sangu")),
    ("rent", _("Rent")),
    ("fee", _("Fee Sales"))
)

class AccountInvoice(models.Model):
    """
    Account Invoice
    """
    _inherit = "account.invoice"
    sales_id = fields.Many2one("res.partner", "Sales", domain="[('active', '=', True), ('is_sales', '=', True)]")
    jenis_inv = fields.Selection(JENIS_INVOICE, "Jenis Invoice", default=JENIS_INVOICE[0][0])
    picking_type_id = fields.Many2one("stock.picking.type", "Picking Type")
    location_id = fields.Many2one("stock.location", "Destination Location", domain=[('usage','=','internal'), ('active', '=', True)])
    is_allowed_plafon = fields.Boolean("Is Allowed Plafon", default=False)
    gen_fee_sales_id = fields.Many2one("dalsil.gen_fee_sales", "Source Document")
    dt_full_paid = fields.Datetime("Datetime Full Paid")
    is_generated_pay_inv = fields.Boolean("Is Generated Payment Invoice", default=False)

    @api.model
    def create(self, vals):
        """
        Mencegah user create kalo state != draft
        """
        acc_inv_id = super(AccountInvoice, self).create(vals)
        if acc_inv_id.jenis_inv == 'invoice':
            for line_id in acc_inv_id.invoice_line_ids:
                if acc_inv_id.sales_id:
                    fee = line_id.product_id.fee * line_id.quantity
                    self.env['dalsil.fee_sales'].create({
                        'sales_id': acc_inv_id.sales_id.id,
                        'invoice_id': acc_inv_id.id,
                        'invoice_line_id': line_id.id,
                        'due_date': acc_inv_id.date_due,
                        'fee_sales': fee,
                        'note': ""
                    })

        return acc_inv_id

    @api.multi
    def to_allowed_plafon(self):
        for record in self:
            record.is_allowed_plafon = True

    @api.multi
    def action_invoice_open(self):
        setting = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
        acc_inv = super(AccountInvoice, self).action_invoice_open()
        for record in self:
            if record.jenis_inv == 'purchase':
                for line_id in record.invoice_line_ids:
                    stock_move_data = {
                        "state": "assigned",

                        # "picking_type_id": record.picking_type_id.id,
                        "location_dest_id": record.location_id.id,
                        "location_id": record.partner_id.property_stock_supplier.id,

                        "partner_id": record.partner_id.id,
                        # "picking_id": stock_picking_id.id,
                        # "warehouse_id": record.picking_type_id.warehouse_id.id,

                        "name": line_id.product_id.name,
                        "product_id": line_id.product_id.id,
                        "product_uom_qty": line_id.quantity,
                        "product_uom": line_id.product_id.uom_id.id,
                        "product_uos_qty": line_id.quantity,
                        "product_uos": line_id.product_id.uom_id.id,

                        "date": fields.Date.today(),
                        "date_expected": fields.Date.today(),

                        "origin": "[PEMBELIAN]-{}".format(record.name),
                        "acc_inv_id": record.id,
                        "price_unit": line_id.price_unit
                    }
                    stock_move = self.env['stock.move'].suspend_security().create(stock_move_data)
                    stock_move.action_done()

                move_data = {
                    "journal_id": setting.purc_journal_id.id,
                    "ref": record.number,
                    "date": fields.Date.today(),
                    "state": "draft",
                    "line_ids": [(0, 0, {
                        "name": record.number,
                        "account_id": setting.purc_acc_debit_id.id,
                        "debit": record.amount_total,
                        "credit": 0.0,
                        "partner_id": record.partner_id.id
                    }), (0, 0, {
                        "name": record.number,
                        "account_id": setting.purc_acc_credit_id.id,
                        "credit": record.amount_total,
                        "debit": 0.0,
                        "partner_id": record.partner_id.id
                    })]
                }
                account_move = self.env['account.move'].create(move_data)
                account_move.post()
            elif record.jenis_inv == 'invoice':
                if not record.is_allowed_plafon:
                    inv_ids = self.env["account.invoice"].sudo().search([
                        ("state", "=", 'open'),
                        ("jenis_inv", "=", 'invoice')
                    ])
                    total_credit = sum(inv_ids.mapped("amount_total"))
                    if total_credit > record.partner_id.plafon:
                        raise ValidationError("Credit customer sudah melibihi batas plafon.")
                for line_id in record.invoice_line_ids:
                    stock_move_data = {
                        "state": "assigned",

                        # "picking_type_id": record.picking_type_id.id,
                        "location_id": line_id.location_id.id,
                        "location_dest_id": record.partner_id.property_stock_supplier.id,
                        # "picking_id": stock_picking_id.id,
                        # "warehouse_id": record.picking_type_id.warehouse_id.id,
                        "partner_id": record.partner_id.id,

                        "name": line_id.product_id.name,
                        "product_id": line_id.product_id.id,
                        "product_uom_qty": line_id.quantity,
                        "product_uom": line_id.product_id.uom_id.id,
                        "product_uos_qty": line_id.quantity,
                        "product_uos": line_id.product_id.uom_id.id,

                        "date": fields.Date.today(),
                        "date_expected": fields.Date.today(),

                        "origin": "[PEMBELIAN]-{}".format(record.name),
                        "acc_inv_id": record.id
                    }
                    stock_move = self.env['stock.move'].suspend_security().create(stock_move_data)
                    stock_move.action_done()

                move_data = {
                    "journal_id": setting.inv_journal_id.id,
                    "ref": record.number,
                    "date": fields.Date.today(),
                    "state": "draft",
                    "line_ids": [(0, 0, {
                        "name": record.number,
                        "account_id": setting.inv_acc_debit_id.id,
                        "debit": record.amount_total,
                        "credit": 0.0,
                        "partner_id": record.partner_id.id
                    }), (0, 0, {
                        "name": record.number,
                        "account_id": setting.inv_acc_credit_id.id,
                        "credit": record.amount_total,
                        "debit": 0.0,
                        "partner_id": record.partner_id.id
                    })]
                }
                account_move = self.env['account.move'].create(move_data)
                account_move.post()
            return acc_inv

    @api.multi
    def action_invoice_paid(self):
        acc_inv = super(AccountInvoice, self).action_invoice_paid()
        for record in self:
            record = record.suspend_security()
            record.dt_full_paid = fields.Datetime.now()
            if record.gen_fee_sales_id:
                record.gen_fee_sales_id.to_paid()
            if record.jenis_inv == 'invoice':
                fee_sales_ids = self.env["dalsil.fee_sales"].suspend_security().search([
                    ("invoice_line_id", "in", record.invoice_line_ids.ids)
                ])
                fee_sales_ids.to_open()
        return acc_inv

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        amount_tax = 0
        for line in self.invoice_line_ids:
            for tax in line.invoice_line_tax_ids:
                amount_tax += line.price_subtotal * tax.amount / 100.00
        self.amount_tax = amount_tax
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def generate_excel(self):
        """
        Membuatkan journal untuk pembayran expense
        """
        self.ensure_one()
        style_header = xlwt.easyxf('font: height 320, bold on')
        style_header = xlwt.easyxf('font: height 240, bold on')
        style_bold = xlwt.easyxf('font: bold on; align: horz center; '
                                 'borders: left thin, top thin, bottom thin, right thin')
        style_table = xlwt.easyxf('borders: left thin, bottom thin, right thin')

        wb = xlwt.Workbook("UTF-8")
        ws = wb.add_sheet('Invoice')
        title = ""

        if self.jenis_inv == 'purchase':
            title = 'Pembelian'
        elif self.jenis_inv == 'invoice':
            title = 'Faktur Penjualan'
        elif self.jenis_inv == 'sangu':
            title = 'Sangu'
        elif self.jenis_inv == 'rent':
            title = 'Rent'
        elif self.jenis_inv == 'fee':
            title = 'Fee Sales'

        y = 0
        x = 0

        ws.col(x).width = 500
        ws.col(x+1).width = 4200
        ws.col(x+2).width = 4200
        ws.col(x+3).width = 6000
        ws.col(x+4).width = 4200
        ws.col(x+5).width = 6000

        ws.write(y, x, "{} {}".format(title, self.number), style=style_header)
        y += 1
        ws.write(y, x, "Tanggal Invoice")
        ws.write(y, x+1, self.date_invoice)
        y += 1
        ws.write(y, x, "Customer")
        ws.write(y, x+1, self.partner_id.name)
        y += 1
        street_name = ""
        if self.partner_id.street:
            street_name = self.partner_id.street
        ws.write(y, x, "Alamat")
        ws.write(y, x+1, street_name)
        y += 2

        ws.write(y, x, "No", style=style_bold)
        ws.write(y, x+1, "Nama Barang", style=style_bold)
        ws.write(y, x+2, "QTY", style=style_bold)
        ws.write(y, x+3, "Harga/@", style=style_bold)
        ws.write(y, x+4, "Pajak", style=style_bold)
        ws.write(y, x+5, "Subtotal tanpa pajak", style=style_bold)
        y += 1

        idx = 0
        for inv_line_id in self.invoice_line_ids:
            idx += 1
            tax_name = ""
            for tax_id in inv_line_id.invoice_line_tax_ids:
                tax_name += tax_id.name
            ws.write(y, x, idx, style=style_table)
            ws.write(y, x+1, inv_line_id.product_id.name, style=style_table)
            ws.write(y, x+2, inv_line_id.quantity, style=style_table)
            ws.write(y, x+3, inv_line_id.price_unit, style=style_table)
            ws.write(y, x+4, tax_name, style=style_table)
            ws.write(y, x+5, inv_line_id.quantity * inv_line_id.price_unit, style=style_table)
            y += 1

        ws.write(y, x, "Pembayaran dgn cek/giro, dianggap sah jika telah diuangkan")
        ws.write(y, x+4, "Subtotal", style=style_table)
        ws.write(y, x+5, self.amount_untaxed, style=style_table)
        y += 1
        ws.write(y, x+4, "Taxes", style=style_table)
        ws.write(y, x+5, self.amount_tax, style=style_table)
        y += 1
        ws.write(y, x+4, "Total", style=style_table)
        ws.write(y, x+5, self.amount_total, style=style_table)
        y += 1
        ws.write(y, x+1, "Adm. Penjualan,")
        y += 3
        ws.write(y, x+1, "(______________)")

        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        return self.env["ss.download"].download(
            "Invoice_{}.xls".format(self.number),
            data
        )

    @api.multi
    def generate_excel_do(self):
        """
        Membuatkan journal untuk pembayran expense
        """
        self.ensure_one()
        style_header = xlwt.easyxf('font: height 320, bold on')
        style_header = xlwt.easyxf('font: height 240, bold on')
        style_bold = xlwt.easyxf('font: bold on; align: horz center; '
                                 'borders: left thin, top thin, bottom thin, right thin')
        style_table = xlwt.easyxf('borders: left thin, bottom thin, right thin')

        wb = xlwt.Workbook("UTF-8")
        ws = wb.add_sheet('Invoice')
        title = "D.O. GUDANG"

        y = 0
        x = 0

        ws.col(x).width = 5000
        ws.col(x + 1).width = 15000
        ws.col(x + 2).width = 6000
        # ws.col(x + 3).width = 4500
        # ws.col(x + 4).width = 6000

        ws.write(y, x, "{} {}".format(title, self.number), style=style_header)
        y += 1
        ws.write(y, x, "Tanggal Invoice")
        ws.write(y, x + 1, self.date_invoice)
        y += 1
        ws.write(y, x, "Customer")
        ws.write(y, x + 1, self.partner_id.name)
        y += 1
        street_name = ""
        if self.partner_id.street:
            street_name = self.partner_id.street
        ws.write(y, x, "Alamat")
        ws.write(y, x + 1, street_name)
        y += 2

        ws.write(y, x, "No", style=style_bold)
        ws.write(y, x + 1, "Nama Barang", style=style_bold)
        ws.write(y, x + 2, "QTY", style=style_bold)
        # ws.write(y, x + 3, "Harga/@", style=style_bold)
        # ws.write(y, x + 4, "Pajak", style=style_bold)
        # ws.write(y, x + 5, "Subtotal tanpa pajak", style=style_bold)
        y += 1

        idx = 0
        sum_qty = sum(self.invoice_line_ids.mapped("quantity"))
        for inv_line_id in self.invoice_line_ids:
            idx += 1
            tax_name = ""
            for tax_id in inv_line_id.invoice_line_tax_ids:
                tax_name += tax_id.name
            ws.write(y, x, idx, style=style_table)
            ws.write(y, x + 1, inv_line_id.product_id.name, style=style_table)
            ws.write(y, x + 2, inv_line_id.quantity, style=style_table)
            # ws.write(y, x + 3, inv_line_id.price_unit, style=style_table)
            # ws.write(y, x + 4, tax_name, style=style_table)
            # ws.write(y, x + 5, inv_line_id.quantity * inv_line_id.price_unit, style=style_table)
            y += 1

        ws.write(y, x + 1, "Jml. Qty:", style=xlwt.easyxf('align: horiz right'))
        ws.write(y, x + 2, sum_qty, style=style_table)
        y += 1
        ws.write(y, x, "Adm. Penjualan,         Pengambil               Mengetahui, ")
        y += 3
        ws.write(y, x, "(_____________)       (_____________)       (_____________)")

        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        return self.env["ss.download"].download(
            "Invoice_{}.xls".format(self.number),
            data
        )