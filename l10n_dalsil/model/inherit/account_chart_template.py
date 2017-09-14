from odoo import models, api
from peewee import DoesNotExist


class AccountChartTemplateIsme(models.Model):
    """
    hapus account yang di paksa odoo untuk dibuat, dan ganti dengan account isme
    """
    _inherit = "account.chart.template"

    @api.model
    def isme_fix_journal_account(self):
        """
        Hapus account tambahan, ganti ke account milik sendiri
        """
        J = self.env["ss.model"].alt_orm("account.journal")
        A = self.env["ss.model"].alt_orm("account.account")

        try:
            cash_acc = A.select(A.id).where(A.code == "110").get().id
        except DoesNotExist:  # tidak ada data karena hasil upgrade / isntall l10n lain sebelum nya
            return  # bailout

        try:
            cash_acc_bad = A.select(A.id).where(A.code == "1101").get().id
        except DoesNotExist:
            pass
        else:
            J.update(default_debit_account_id=cash_acc, default_credit_account_id=cash_acc). \
                where(J.default_debit_account_id == cash_acc_bad).execute()
            A.delete().where(A.id == cash_acc_bad).execute()

        bank_acc = A.select(A.id).where(A.code == "120").get().id
        try:
            bank_acc_bad = A.select(A.id).where(A.code == "1201").get().id
        except DoesNotExist:
            pass
        else:
            J.update(default_debit_account_id=bank_acc, default_credit_account_id=bank_acc). \
                where(J.default_debit_account_id == bank_acc_bad).execute()
            A.delete().where(A.id == bank_acc_bad).execute()

    @api.model
    def isme_fix_setting_tax(self):
        """
        mengosongkan Default Sale Tax dan Default Purchase Tax
        """
        val_env = self.env["ir.values"]
        val_env.search([
            ("model", "=", "product.template"), ("name", "=", "taxes_id")
        ]).write({"value_unpickle": "False"})
        val_env.search([
            ("model", "=", "product.template"), ("name", "=", "supplier_taxes_id")
        ]).write({"value_unpickle": "False"})

    @api.model
    def isme_fix(self):
        """
        main model untuk memanggil model lain
        """
        self.isme_fix_journal_account()
        self.isme_fix_setting_tax()
