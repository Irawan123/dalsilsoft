from peewee import IntegerField, FloatField, CharField, DateField, DateTimeField, BooleanField, BlobField, TextField
from peewee import Model, PostgresqlDatabase


class CustomCursor(object):
    """
    Wrapper dari cursor psycopg2, digunakan untuk mengimitasi cursor psycopg & memberikan nama
    """
    name = "custom_cursor"

    def __init__(self, cr):
        """
        Inisiasi wrapper cursor & simpan object cursor
        :param cr:
        """
        self.cr = cr

    def __getattr__(self, item):
        """
        Semua attr adalah milik cr, kecuali ``name``
        """
        return getattr(self.cr, item)


class OdooDatabase(PostgresqlDatabase):
    """
    Modifikasi class untuk postgre db, disesuaikan untuk odoo.

    Ketika inisiasi, gunakan object ``cr`` dari ``self.env.cr``
    """

    def _connect(self, database, encoding=None, **kwargs):
        """
        Override method connect, supaya mengembalikan object connection nya odoo saja
        """
        return database._cnx

    def get_cursor(self):
        """
        Override method get_cursor, supaya mengembalikan wrapper cursor.

        Warpper cursor custom digunakan karena untuk mencegah cursor di close (untuk client cursor).
        Odoo akan mengalami error kalau cursor nya di tutup di tengah jalan & cursor psycopg adalah object readonly.
        """
        return CustomCursor(self.database._obj)


def get_peewee_field(field_name, field_info):
    """
    Generate field peewee berdasarkan tipe datanya

    :param field_name: Nama field database
    :param data_type: Tipe Data
    :return: Object Field peewee hasil generate
    """
    data_type = field_info["type"]

    if data_type in ("integer", "many2one"):
        return IntegerField(db_column=field_name)

    if data_type in ("float", "monetary"):
        return FloatField(db_column=field_name)

    if data_type in ("char", "selection"):
        return CharField(db_column=field_name)

    if data_type in ("text", "html"):
        return TextField(db_column=field_name)

    if data_type == "date":
        return DateField(db_column=field_name)

    if data_type == "datetime":
        return DateTimeField(db_column=field_name)

    if data_type == "boolean":
        return BooleanField(db_column=field_name)

    if data_type == "binary":
        return BlobField(db_column=field_name)

    return None


def get_alt(odoo_obj):
    """
    Method untuk generate class peewee dari object odoo.

    :param odoo_obj: Object odoo
    :return: Class ORM peewee dari object odoo
    """

    class PeeweeModel(Model):
        """
        Class untuk di generate
        """

        class Meta:
            database = OdooDatabase(odoo_obj.env.cr, autocommit=False)
            db_table = odoo_obj._table

    # Implements fields
    for field_name, data in odoo_obj.fields_get().iteritems():
        if not data.get("store", False):
            continue

        field = get_peewee_field(field_name, data)
        if field:
            field.add_to_class(PeeweeModel, field_name)

    return PeeweeModel
