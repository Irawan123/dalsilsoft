from datetime import datetime

from odoo import models, fields, api
from pytz import UTC, timezone


class DateTimeHelper(models.AbstractModel):
    """
    Model bantuan untuk operasi datetime beserta timezone nya.
    """
    _name = "ss.dt"

    # dapatkan data timezone local
    @api.model
    def get_local_tz(self, user=None):
        """
        Mendapatkan local timezone user

        :param user: Object/ID User yang akan di ambil data tz nya.
        :return: string timezone user yg login saat ini / dari uid yang di tentukan
        """
        user = self.env["res.users"].suspend_security().browse(user) if isinstance(user, int) else user
        user = user or self.env.user

        return user.tz or "UTC"

    @api.model
    def get_admin_tz(self):
        """
        Mendapatkan timezone dari admin. Setting timezone dari admin dibuat sebagai standar timezone server

        :return: string timezone admin
        """
        return self.sudo().get_local_tz()

    # timezone convertion
    @api.model
    def local2utc(self, dt, string=False, tz=False):
        """
        Mengubah data datetime dari timezone local ke UTC.

        Timezone local dapat di setting dari parameter ``tz``:

        1. Kalau di set ``False``, maka akan menggunakan timezone user local sekarang
        2. Kalau di set ``True``, maka akan menggunakan timezone user admin
        3. Kalau di set dengan timezone custom (string), maka akan menggunakan timezone itu

        :param dt: Data datetime
        :param string: Return hasil konversi sebagai string
        :param tz: Setting Timezone local
        :return: Data datetime setelah di konversi
        """
        dt = dt if isinstance(dt, datetime) else fields.Datetime.from_string(dt)
        if isinstance(tz, bool):
            tz = self.get_admin_tz() if tz else self.get_local_tz()

        result = timezone(tz).localize(dt).astimezone(UTC).replace(tzinfo=None)

        return fields.Datetime.to_string(result) if string else result

    @api.model
    def utc2local(self, dt, string=False, tz=False):
        """
        Mengubah data datetime dari timezone UTC ke UTC.

        Timezone local dapat di setting dari parameter ``tz``:

        1. Kalau di set ``False``, maka akan menggunakan timezone user login sekarang
        2. Kalau di set ``True``, maka akan menggunakan timezone user admin
        3. Kalau di set dengan timezone custom (string), maka akan menggunakan timezone itu

        :param dt: Data datetime
        :param string: Return hasil konversi sebagai string
        :param tz: Setting Timezone local
        :return: Data datetime setelah di konversi
        """
        dt = dt if isinstance(dt, datetime) else fields.Datetime.from_string(dt)
        if isinstance(tz, bool):
            tz = self.get_admin_tz() if tz else self.get_local_tz()

        result = UTC.localize(dt).astimezone(timezone(tz)).replace(tzinfo=None)

        return fields.Datetime.to_string(result) if string else result

    # Data type conversion dengan perhitungan timezone
    @api.model
    def datetime2date(self, dt=None, string=False, tz=False):
        """
        Mengubah Data datetime menjadi date.
        Tanggal yang digunakan menyesuaikan dari posisi tanggal pada timezone yang ditentukan.

         Timezone dapat di setting dari parameter ``tz``:

        1. Kalau di set ``False``, maka akan menggunakan timezone user login sekarang
        2. Kalau di set ``True``, maka akan menggunakan timezone user admin
        3. Kalau di set dengan timezone custom (string), maka akan menggunakan timezone itu

        :param dt: Data datetime. Bila tidak di isi, menggunakan datetime saat ini.
        :param string: Return hasil konversi sebagai string
        :param tz: Setting Timezone local
        :return: Data date setelah di konversi
        """
        dt = dt or fields.Datetime.now()
        result = self.utc2local(dt, tz=tz).date()

        return fields.Date.to_string(result) if string else result
