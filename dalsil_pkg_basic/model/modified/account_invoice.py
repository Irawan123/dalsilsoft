from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

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
    sales_id = fields.Many2one("res.partner", "Sales")
    jenis_inv = fields.Selection(JENIS_INVOICE, "Jenis Invoice", default=JENIS_INVOICE[0][0])
    picking_type_id = fields.Many2one("stock.picking.type", "Picking Type")

    @api.model
    def create(self, vals):
        """
        Mencegah user create kalo state != draft
        """
        acc_inv_id = super(AccountInvoice, self).create(vals)
        if acc_inv_id.jenis_inv == 'invoice':
            fee = 0
            for line_id in acc_inv_id.invoice_line_ids:
                fee += line_id.product_id.fee * line_id.quantity
            self.env['dalsil.fee_sales'].create({
                'sales_id': acc_inv_id.sales_id.id,
                'invoice_id': acc_inv_id.id,
                'due_date': acc_inv_id.date_due,
                'fee_sales': fee,
                'note': ""
            })

        return acc_inv_id

    @api.multi
    def action_invoice_open(self):
        acc_inv = super(AccountInvoice, self).action_invoice_open()
        for record in self:
            if record.jenis_inv == 'purchase':
                for line_id in record.invoice_line_ids:
                    stock_move_data = {
                        "state": "assigned",

                        "picking_type_id": record.picking_type_id.id,
                        "location_dest_id": record.picking_type_id.default_location_dest_id.id,
                        "location_id": record.partner_id.property_stock_supplier.id,
                        # "picking_id": stock_picking_id.id,
                        "warehouse_id": record.picking_type_id.warehouse_id.id,

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
            elif record.jenis_inv == 'invoice':
                for line_id in record.invoice_line_ids:
                    stock_move_data = {
                        "state": "assigned",

                        "picking_type_id": record.picking_type_id.id,
                        "location_id": record.picking_type_id.default_location_dest_id.id,
                        "location_dest_id": record.partner_id.property_stock_supplier.id,
                        # "picking_id": stock_picking_id.id,
                        "warehouse_id": record.picking_type_id.warehouse_id.id,

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
            return acc_inv