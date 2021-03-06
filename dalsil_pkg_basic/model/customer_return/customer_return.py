from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

STATE = (
    ("draft", _("Draft")),
    ("done", _("Done")),
    ("cancel", _("Cancelled")),
)

class CustomerReturn(models.Model):
    """
    Customer Return
    """
    _name = "dalsil.customer_return"
    _inherit = "ss.model"
    _state_start = STATE[0][0]
    _seq_code = {"name": "dalsil_customer_return"}

    name = fields.Char("Customer Return No.")
    state = fields.Selection(STATE, "State")
    acc_inv_id = fields.Many2one("account.invoice", "Customer Invoice", domain=[("jenis_inv", "=", "invoice"),("state", "=", "open")])
    partner_id = fields.Many2one("res.partner", "Vendor", compute="_get_data_invoice", store=True)
    picking_type_id = fields.Many2one("stock.picking.type", "Stock Picking Type", compute="_get_data_invoice", store=True)
    date_invoice = fields.Date("Bill Date", compute="_get_data_invoice", store=True)
    date_due = fields.Date("Due Date", compute="_get_data_invoice", store=True)
    location_id = fields.Many2one("stock.location", "Destination Location", compute="_get_data_invoice", store=True)
    line_ids = fields.One2many("dalsil.customer_return.line", "parent_id", string="Products")
    note = fields.Text("Internal Note")

    @api.depends("acc_inv_id")
    def _get_data_invoice(self):
        for record in self:
            record.partner_id = record.acc_inv_id.partner_id
            record.picking_type_id = record.acc_inv_id.picking_type_id
            record.date_invoice = record.acc_inv_id.date_invoice
            record.date_due = record.acc_inv_id.date_due
            record.location_id = record.acc_inv_id.location_id

    @api.model
    def create(self, vals):
        """
        Mencegah user create kalo state != draft
        """
        cust_ret_id = super(CustomerReturn, self).create(vals)
        line_ids = []
        for line_id in cust_ret_id.acc_inv_id.invoice_line_ids:
            line_ids.append([0, 0, {
                'product_id': line_id.product_id.id,
                'qty': line_id.quantity,
                'unit_price': line_id.price_unit,
                'invoice_line_tax_ids': [(6, 0, line_id.invoice_line_tax_ids.ids)],
                'account_id': line_id.account_id.id,
                'acc_inv_line_id': line_id.id
            }])
        cust_ret_id.line_ids = line_ids

        return cust_ret_id

    @api.multi
    def to_cancel(self):
        """
        Ubah state jadi cancel
        """
        self._cstate(STATE[2][0])

    @api.multi
    def to_done(self):
        for record in self:
            self._cstate(STATE[1][0])
            tax_line_ids = {}
            line_ids = []
            total_amount = 0.0
            
            for line_id in record.line_ids:
                line_id.acc_inv_line_id.qty_return += line_id.qty_return
                stock_move_data = {
                    "state": "assigned",

                    "location_dest_id": line_id.acc_inv_line_id.location_id.id,
                    "location_id": record.partner_id.property_stock_supplier.id,

                    "name": line_id.product_id.name,
                    "product_id": line_id.product_id.id,
                    "product_uom_qty": line_id.qty_return,
                    "product_uom": line_id.product_id.uom_id.id,
                    "product_uos_qty": line_id.qty_return,
                    "product_uos": line_id.product_id.uom_id.id,

                    "date": fields.Date.today(),
                    "date_expected": fields.Date.today(),

                    "origin": "[RETURN]-{}".format(record.name),
                    "acc_inv_id": record.acc_inv_id.id
                }
                stock_move = self.env['stock.move'].suspend_security().create(stock_move_data)
                stock_move.action_done()

                return_price = line_id.qty_return * line_id.unit_price
                if return_price > 0:
                    return_price_total_item = return_price
                    total_amount += return_price
                    line_ids.append([0, 0, {
                        "name": line_id.product_id.name,
                        "account_id": line_id.account_id.id,
                        "credit": 0.0,
                        "debit": return_price,
                        "partner_id": record.partner_id.id
                    }])
                    for tax_id in line_id.invoice_line_tax_ids:
                        key = (tax_id.name, tax_id.account_id.id)
                        tax_price = return_price * tax_id.amount / 100.00
                        return_price_total_item += tax_price
                        if key in tax_line_ids:
                            tax_line_ids[key] += tax_price
                        else:
                            tax_line_ids[key] = tax_price

            for key, value in tax_line_ids.items():
                tax_name = key[0]
                account_id = key[1]
                total_amount += value
                line_ids.append([0, 0, {
                    "name": tax_name,
                    "account_id": account_id,
                    "credit": 0.0,
                    "debit": value,
                    "partner_id": record.partner_id.id
                }])

            setting = self.env["ir.model.data"].xmlid_to_object("dalsil_pkg_basic.dalsil_config")
            move_data_stock = {
                "journal_id": setting.inv_journal_id.id,
                "ref": record.acc_inv_id.number,
                "date": fields.Date.today(),
                "state": "draft",
                "line_ids": [(0, 0, {
                    "name": record.acc_inv_id.number,
                    "account_id": setting.inv_acc_debit_id.id,
                    "credit": total_amount,
                    "debit": 0.0,
                    "partner_id": record.partner_id.id
                }), (0, 0, {
                    "name": record.acc_inv_id.number,
                    "account_id": setting.inv_acc_credit_id.id,
                    "debit": total_amount,
                    "credit": 0.0,
                    "partner_id": record.partner_id.id
                })]
            }
            account_move = self.env['account.move'].create(move_data_stock)
            account_move.post()


            line_ids.append([0, 0, {
                "name": "/",
                "account_id": record.partner_id.property_account_receivable_id.id,
                "credit": total_amount,
                "debit": 0.0,
                "partner_id": record.partner_id.id
            }])

            move_data = {
                "journal_id": record.acc_inv_id.journal_id.id,
                "ref": record.acc_inv_id.number,
                "date": fields.Date.today(),
                "state": "draft",
                "line_ids": line_ids
            }
            account_move = self.env['account.move'].create(move_data)
            account_move.post()
