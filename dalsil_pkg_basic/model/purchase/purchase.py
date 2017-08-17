__author__ = "Michael PW"

from odoo import models, fields, api
from odoo.exceptions import ValidationError

STATE = (
    ("draft", "Draft"),
    ("done", "Done"),
    ("cancel", "Cancel")
)

class Purchase(models.Model):
    _name = "dalsil.purchase"
    _inherit = "ss.model"
    _description = "Purchase"

    name = fields.Char("Purchase No")
    spj_no = fields.Char("SPJ No")
    tr_date = fields.Date("Transaction Date")
    supplier_id = fields.Many2one("res.partner", "Supplier")
    dest_loc_id = fields.Many2one("dalsil.location", "Lokasi Tujuan")
    line_ids = fields.One2many("dalsil.purchase.line", "parent_id", string="Product")
    stock_move_ids = fields.One2many("dalsil.stock_move", "purchase_id", string="Stock Move")
    total = fields.Float(digits=(20,2), string="Sub Total", compute="_get_total", store=True)
    note = fields.Text("Keterangan")
    state = fields.Selection(STATE, string="Status")

    @api.depends("line_ids", "line_ids.sub_total")
    def _get_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped("sub_total"))
            
    @api.multi
    def to_done(self):
        for record in self:
            record = record.suspend_security()
            if record.state != 'draft':
                continue
            stock_move = self.env['dalsil.stock_move'].suspend_security()
            stock_move_line_data = []
            for line_id in record.line_ids:
                stock_move_line_data.append([0, 0, {
                    "product_id": line_id.product_id.id,
                    "qty": line_id.qty
                }])
            stock_move.create({
                'dest_loc_id': record.dest_loc_id.id,
                'line_ids': stock_move_line_data,
                'purchase_id': record.id
            })
            stock_move.to_done()
            record.done_uid = record.env.uid
            record.dt_done = fields.Datetime.now()
            record.state = 'done'

    @api.multi
    def to_cancel(self, reason):
        for record in self:
            record = record.suspend_security()
            if record.state == 'done':
                if "done" in record.stock_move_ids.mapped("state"):
                    raise ValidationError("Harap cancel stock move terlebih dahulu")
            record.cancel_uid = record.env.uid
            record.dt_cancel = fields.Datetime.now()
            record.cancel_reason = reason
            record.state = 'cancel'

    @api.multi
    def to_cancel_rejector(self):
        return self.env["ss.rejector"].show(
            self, "to_cancel", "Cancel Stock Move",
            "Untuk mengcancel Stock Move `{}`, berikan alasan:".format(self.name)
        )