from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    """
    Res Partner
    """
    _inherit = "res.partner"

    """
        Menambahkan field untuk "alamat" dan tipe transaksi
    """
    block = fields.Char('Blok')
    number = fields.Char('Number')
    rt = fields.Char('RT')
    rw = fields.Char('RW')
    kelurahan = fields.Char('Kelurahan')
    kecamatan = fields.Char('Kecamatan')

    plafon = fields.Float("Plafon", digits=(20,2))

    is_driver = fields.Boolean("Is a Driver", default=False)
    is_sales = fields.Boolean("Is a Sales", default=False)

    @api.model
    @api.returns("self", lambda x: x.id)
    def create(self, vals):
        if vals.get("rw", False):
            if not vals['rw'].isdigit():
                raise ValidationError(_("RW harus angka"))
            vals['rw'] = "%03d" % (int(vals['rw'])) if vals['rw'] else vals['rw']

        if vals.get("rt", False):
            if not vals['rt'].isdigit():
                raise ValidationError(_("RT harus angka"))
            vals['rt'] = "%03d" % (int(vals['rt'])) if vals['rt'] else vals['rt']

        if vals.get("number", False) and vals['number'].isdigit():
            vals['number'] = "%03d" % (int(vals['number'])) if vals['number'] else vals['number']

        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Override biar "nomor, rt, rw" bisa 3 digit (tp kl di isi > 3digit, masi boleh)
        """
        if vals.get("rw", False) and not vals['rw'].isdigit():
            raise ValidationError(_("RW harus angka"))

        if vals.get("rt", False) and not vals['rt'].isdigit():
            raise ValidationError(_("RT harus angka"))

        if vals.get("number", False) and vals['number'].isdigit():
            vals['number'] = "%03d" % (int(vals['number'])) if vals['number'] else vals['number']

        return super(ResPartner, self).write(vals)
