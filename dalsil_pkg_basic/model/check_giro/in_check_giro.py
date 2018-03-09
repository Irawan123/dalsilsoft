from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

STATE = (
    ("draft", _("Draft")),
    ("open", _("Open")),
    ("withdraw", _("Withdrawn")),
    ("cancel", _("Cancelled")),
)
CHECK_GIRO = (
    ("check", _("Cek")),
    ("giro", _("Giro"))
)


class IngoingCheckGiro(models.Model):
    """
    Check Giro masuk
    """
    _name = "dalsil.check_giro.in"
    _inherit = "ss.model"
    _state_start = STATE[0][0]

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char("Cek / Giro No.", required=True)
    state = fields.Selection(STATE, "State")
    cg_type = fields.Selection(CHECK_GIRO, "Cek / Giro", required=True)

    journal_id = fields.Many2one("account.journal", "Cek Giro Journal", required=True)
    account_id = fields.Many2one("account.account", "Cek Giro Account", required=True)
    customer_id = fields.Many2one("res.partner", "Customer", domain=[("customer", "=", True)], required=True)
    due_date = fields.Date("Due Date", required=True)
    cg_amount = fields.Float("Cek Giro Amount", (15, 2), required=True)
    cg_curr_id = fields.Many2one("res.currency", default=_default_currency)

    wd_journal_id = fields.Many2one("account.journal", "Withdraw Journal")
    wd_account_id = fields.Many2one("account.account", "Withdraw Account")
    wd_date = fields.Date("Withdraw Date")
    wd_amount = fields.Float("Withdraw Amount", (15, 2), required=True)

    total_pay = fields.Float("Total Payment Amount", (15, 2), compute="_get_total_pay", store=True)
    memo = fields.Text("Memo")
    note = fields.Text("Note")

    line_ids = fields.One2many("dalsil.check_giro.in.line", "parent_id", "Transaction")

    # history account.move / journal entries
    je_ids = fields.Many2many("account.move", "isme_check_giro_in_je_rel")
    je_count = fields.Integer("Journal Entries", compute="_get_je_count")

    #################### Compute ####################
    @api.depends("line_ids", "line_ids.payment")
    def _get_total_pay(self):
        """
        Menghitung jumlah pembayaran
        """
        for record in self:
            record.total_pay = sum(record.line_ids.mapped("payment"))

    @api.depends("je_ids")
    def _get_je_count(self):
        """
        Menghitung jumlah journal entry yg dibuat.
        """
        for record in self:
            record.je_count = len(record.je_ids)

    #################### Private ####################
    @api.multi
    def _check_before_validate(self):
        """
        Method untuk periksa data, sebelum divalidasi
        """
        for record in self:
            if not record.line_ids:
                raise ValidationError(_("Please Add a Transaction first!"))
            if record.cg_amount != record.total_pay:
                msg = _(
                    "Ingoing Cek Giro Unbalanced!\n"
                    "Cek Giro Amount ({cg_amount}) != Total Payment Amount ({total_pay})"
                )
                raise ValidationError(msg.format(cg_amount=record.cg_amount, total_pay=record.total_pay))

    @api.model
    def _get_payment_method(self, invoice, wd_journal_id):
        """
        Mendapatkan payment method

        :param inv: Object invoice dari detil check giro masuk
        :param wd_journal_id: Object journal withdraw
        :return: payment method
        :raise: ``UserError`` kalau tidak deitemukan
        """
        # payment type ``inbound``
        if invoice.type in ("out_invoice", "in_refund"):
            payment_method = self.env.ref("account.account_payment_method_manual_in")
            if payment_method not in wd_journal_id.inbound_payment_method_ids:
                payment_method = False
        # payment type ``outbound``
        else:
            payment_method = self.env.ref("account.account_payment_method_manual_out")
            if payment_method not in wd_journal_id.outbound_payment_method_ids:
                payment_method = False
        if not payment_method:
            raise UserError(_("No appropriate payment method enabled on journal {journal}").format(wd_journal_id.name))

        return payment_method

    #################### Button ####################
    @api.multi
    def show_je(self):
        """
        Menampilkan data journal entry yg terbuat
        """
        self.ensure_one()

        return self.show_record(
            "account.move", _("Journal Entries"), view_mode="tree,form",
            domain=[("id", "in", self.je_ids.ids)]
        )

    #################### State ####################
    @api.multi
    def to_validate(self):
        """
        Ubah state menjadi open & generate account.move
        """
        self._check_before_validate()
        move_env = self.env["account.move"]
        for record in self:
            lines = [(0, 0, {
                "account_id": record.account_id.id,
                "partner_id": record.customer_id.id,
                "name": record.name,
                "credit": 0,
                "debit": record.cg_amount,
                "date_maturity": fields.Date.today()
            })]
            for line in record.line_ids:
                lines.append((0, 0, {
                    "account_id": line.invoice_id.account_id.id,
                    "partner_id": record.customer_id.id,
                    "name": line.invoice_id.number,
                    "credit": line.payment,
                    "debit": 0,
                    "date_maturity": fields.Date.today()
                }))
            move = move_env.create({
                "journal_id": record.journal_id.id,
                "date": fields.Date.today(),
                "line_ids": lines
            })
            move.post()
            record.je_ids = [(4, move.id)]

        self._cstate(STATE[1][0])

    @api.multi
    def to_withdraw(self):
        """
        Ubah state jadi withdraw &  buat account.payment
        """
        pay_env = self.env["account.payment"]
        MoveLine = self.alt_orm("account.move.line")
        for record in self:
            for line in record.line_ids:
                inv = line.invoice_id
                payment_method = self._get_payment_method(inv, record.wd_journal_id)

                comm = inv.reference if inv.type in ("in_invoice", "in_refund") else inv.number
                if inv.origin:
                    comm = "{} ({})".format(comm, inv.origin)

                acc_pay = pay_env.create({
                    "company_id": self.env.user.company_id.id,
                    "payment_type": "inbound",
                    "memo": inv.number,
                    "communication": comm,
                    "journal_id": record.wd_journal_id.id,
                    "amount": line.payment,
                    "payment_date": fields.Date.today(),
                    "check_giro_src": record.name,
                    "payment_method_id": payment_method.id,
                    "payment_difference_handling": "open",
                    "invoice_ids": [(6, 0, [inv.id])],
                    "partner_type": "customer" if inv.type in ("out_invoice", "out_refund") else "supplier",
                    "partner_id": inv.partner_id.id,
                })
                acc_pay.post()

                for move in acc_pay.move_line_ids:
                    if move.credit > 0.0:
                        MoveLine.update(account_id=record.account_id.id).where(MoveLine.id == move.id).execute()
                    elif move.debit > 0.0:
                        MoveLine.update(account_id=record.wd_journal_id.wd_account_id.id). \
                            where(MoveLine.id == move.id).execute()

                move_ids = acc_pay.move_line_ids.mapped("move_id").ids
                record.je_ids = list((4, move_id) for move_id in move_ids)

        self._cstate(STATE[2][0])

    @api.multi
    def to_cancel(self):
        """
        Ubah state jadi cancel
        """
        for record in self:
            if record.state == STATE[1][0]:
                # reverse journal
                for mv in record.je_ids:
                    mv_rev = mv.reverse_moves()
                    record.je_ids = [(4, move_id) for move_id in mv_rev]

        self._cstate(STATE[3][0])

    #################### Onchange ####################
    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        """
        default cek giro account
        """
        if self.journal_id:
            self.account_id = self.journal_id.default_debit_account_id

    @api.onchange("wd_journal_id")
    def _onchange_wd_journal_id(self):
        """
        default withdraw account
        """
        if self.wd_journal_id:
            if self.wd_journal_id.default_debit_account_id:
                self.wd_account_id = self.wd_journal_id.default_debit_account_id

    @api.onchange("due_date")
    def _onchange_due_date(self):
        """
        default withdraw date
        """
        if self.due_date:
            self.wd_date = self.due_date

    @api.onchange("cg_amount")
    def _onchange_cg_amount(self):
        """
        default withdraw amount
        """
        if self.cg_amount:
            self.wd_amount = self.cg_amount
