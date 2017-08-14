from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from playhouse.shortcuts import model_to_dict

from orm_alt_peewee import get_alt


class BaseModel(models.AbstractModel):
    """
    Model dasar untuk mempermudah operasi model odoo.
    """
    _name = "ss.model"

    # Memisahkan ids menjadi beberap list dengan panjang dari var ini (query lebih efisien)
    _query_chunk = 1000

    # Field state untuk di set default saat create (dari field ``_state_start``)
    # dan digunakan untuk nama field otomatis pada method ``_cstate``.
    _rec_state = "state"

    # State awal record ini. Dapat di isi dengan string atau dictionary.
    # Kalau di isi string, maka akan mengisikan string ini ke field yg di set di ``_rec_state``.
    # Kalau di isi dictionary, maka akan mengisikan value dictionary ke field yang di set sebagai key dictionary.
    # Value dapat berupa function tanpa parameter
    _state_start = False

    # Dictionary yang berisi nama field (key) & external ID (value) dari record ``ir.sequence``.
    # Digunakan untuk penomoran otomatis saat create
    # format: namamodul.idsequence
    _seq_id = False

    # Dictionary yang berisi nama field (key) & kode sequence (value) dari record ``ir.sequence``.
    # Digunakan untuk penomoran otomatis saat create
    # format: kodesequence
    _seq_code = False

    # Dictionary yg berisi nilai default untuk di isikan pada field yang di definisikan pada key nya.
    # Value dapat di isi dengan function yang tidak menerima parameter
    # menu: more --> Duplicate
    _copy_default = False

    # ada beberapa field nanti bisa di False dahulu supaya hasil dokumen yang di copy tidak sama dengan data yang asli
    # contoh : nomor ID dokumen, siapa nama orang yang sudah Dona
    # karena klo status sudah DONE dicopy yaa jadinya kan DRAFT lagi
    # Field active yang digunakan untuk di set False ketika unlink (dari ``_unlink_deactivate``)
    # Y# ada Hubungan sama _unlink_deactivate
    _rec_active = "active"

    # Set flag active menjadi False saat menjadi delete (field active dari _rec_active)
    # Set ke angka ``2`` kalau ingin record ttp bisa di delete
    # (delete pertama set active jadi False, delete ke 2 kali benar2 delete)
    # Y# contoh client tidak mau ada data di delete, nah dikasi boolean true apa false klo false tidak dibaca
    # False = delete ya ilang
    # 1 / True = delete cuma set _rec_active jadi False (Data masih tapi Hidden)
    # 2 = _rec_active sudah False trus di delete lagi jadi Permanen Hilang
    _unlink_deactivate = False

    # private method
    @api.model
    def _validate_vals(self, vals):
        """
        Periksa data pada vals. Untuk saat ini hanya periksa kalau ada key yg tidak terdaftar.

        :param vals: Nilai vals yg diperiksa.
        """
        field_list = set(self.fields_get_keys())
        bads = set(vals).difference(field_list)
        if bads:
            raise ValidationError(_("Unknown field(s): {fields}").format(fields=", ".join(bads)))

    @api.model
    def _validate_state(self, state, f_state=None):
        """
        Memeriksa, apakah state ini memang benar ada.

        :param state: State yang diperiksa
        :param f_state: Field state.
        """
        field = f_state or self._rec_state
        selection = dict(self.fields_get([field])[field]["selection"])
        if state not in selection:
            raise ValidationError(_("Unknown state: {state}").format(state=state))

    @api.multi
    def _balance_ids(self, ids=None, query_chunk=None):
        """
        Method untuk memisahkan list ids yang terlalu banyak, menjadi beberapa bagian,
        supaya query tidak menjadi terlalu berat.

        :param ids: ids lain kalau model ini dipakai oleh model lain yg tidak inherit
        :param query_chunk: Sebarapa banyak untuk split, digunakan untuk override setting model
        """
        ids = ids or self.ids
        query_chunk = query_chunk or self._query_chunk
        for i in xrange(0, len(ids), query_chunk):
            yield tuple(ids[i:i + query_chunk])

    @api.model
    def _auto_state(self, vals):
        """
        Method yg dipanggil untuk mengotomatiskan pengisian state. Method ini mengisikan dict ``vals``.

        Method ini mengandalkan field ``_state_start`` yang berisi dictionary nama field state dengan state awal.

        :param vals: vals dari method ``create``
        """
        data = self._state_start or {}
        if not isinstance(data, dict):
            data = {self._rec_state: data}

        for field, state in data.iteritems():
            if not vals.get(field, False):
                vals[field] = state() if callable(state) else state

    @api.model
    def _auto_sequence(self, vals):
        """
        Method yang di panggil untuk mengotomatiskan pengisian nomor dokumen. Method ini mengisikan dict ``vals``.

        Method ini mengandalkan field ``_seq_id`` yang berisi dictionary nama field state dengan external id sequence
        dan field ``_seq_code`` yang berisi dictionary nama field dengan kode sequence.

        :param vals: vals dari method ``create``
        """
        helper = self.env["ss.sequence"]

        for field, code in (self._seq_code.iteritems() if isinstance(self._seq_code, dict) else ()):
            if not vals.get(field, False):
                vals[field] = helper.next_by_code(code)

        for field, extid in (self._seq_id.iteritems() if isinstance(self._seq_id, dict) else ()):
            if not vals.get(field, False):
                vals[field] = helper.next_by_extid(extid)

    @api.model
    def _get_read_fields(self, field_list=None):
        """
        Method sama seperti ``fields_get``, tapi hanya field2 asli database, beserta keterangan secukupnya.

        :param field_list: List field yg diminta, kalau kosong, memberikan semua.
        :return: dictionary field beserta data nya.
        """
        result = {}
        for field, data in self.fields_get().iteritems():
            if not data.get("store", False):  # dari inherits atau compute yg tidak store
                continue
            if field_list and field not in field_list:  # hanya field yg diminta saja
                continue
            result[field] = {
                "type": data["type"]
            }

        return result

    @api.model
    def _fetch_gen_alt_orm(self, target):
        """
        Mendapatkan / Generate orm peewee berdasarkan ``target``.

        Bila cache tidak memiliki model ini, method ini akan generate Model Peewee lalu menyimpan nya di cache.
        Kalau model sudah ada di cache, method ini hanya mengembalikan model dari cache.

        :param target: Nama Model / Object odoo untuk di fetch / generate Model Peewee nya
        :return: Model Peewee
        """
        model, key = (self.env[target], target) if isinstance(target, basestring) else (target, target._name)

        if getattr(self.env, "_alt_orm", False):
            cache = self.env._alt_orm
        else:
            self.env._alt_orm = cache = {}

        if key in cache:
            return cache[key]

        cache[key] = Model = get_alt(model)

        return Model

    # RAW query method
    @api.model
    @api.returns("self", lambda value: value.id)
    def _ccreate(self, vals, auto_field=True):
        """
        Method create khusus, yang hanya melakukan query sql,
        sehingga dapat mengurangi overhead, tetapi tidak memeriksa security & constraint.

        PENTING: Field compute (dengan inverse) tidak dapat di isikan di sini!

        :param vals: Nilai baru yang akan di masukkan
        :param auto_field: Apakah juga mengisikan field ``write_uid`` & ``write_date`` sebagai history?
        """
        self._auto_state(vals)
        self._auto_sequence(vals)
        self._validate_vals(vals)
        if auto_field:
            current_dt = fields.Datetime.now()
            vals["create_uid"] = vals.get("create_uid", self.env.uid)
            vals["create_date"] = vals.get("create_date", current_dt)
            vals["write_uid"] = vals.get("write_uid", self.env.uid)
            vals["write_date"] = vals.get("write_date", current_dt)

        vals = self._add_missing_default_values(vals)

        ModelClass = self.alt_orm()
        obj = ModelClass.create(**vals)
        obj = self.browse(obj.id)
        obj._parent_store_compute()
        obj._cache.update(obj._convert_to_cache(vals))

        return obj

    @api.multi
    def _cwrite(self, vals, auto_field=False):
        """
        Method write khusus, yang hanya melakukan query sql,
        sehingga dapat mengurangi overhead, tetapi tidak memeriksa security & constraint.

        PENTING: Field compute (dengan inverse) tidak dapat di isikan di sini!
        jika auto_field=True --> diisikan secara otomatis

        :param vals: Nilai baru yang akan di masukkan
        :param auto_field: Apakah juga mengisikan field ``write_uid`` & ``write_date`` sebagai history?
        """
        self._check_concurrency()
        self._validate_vals(vals)

        if auto_field:
            current_dt = fields.Datetime.now()
            vals["write_uid"] = vals.get("write_uid", self.env.uid)
            vals["write_date"] = vals.get("write_date", current_dt)

        ModelClass = self.alt_orm()
        for ids in self._balance_ids():
            ModelClass.update(**vals).where(ModelClass.id.in_(ids)).execute()

        # trigger recompute parent left right
        self._parent_store_compute()

        # update cache
        for record in self:
            record._cache.update(record._convert_to_cache(vals, update=True))

        return True

    @api.multi
    def _cstate(self, new_state, f_uid=None, f_dt=None, vals=None, f_state=None, as_write=False):
        """
        Mengubah field state (dari variable ``REC_STATE``) otomatis.

        Optional: mengisikan field user & datetime sebagai history.

        :param new_state: State baru yang akan di set.
        :param f_uid: Field user id untuk history (bisa banyak dengan tuple/list)
        :param f_dt: Field datetime untuk history (bisa banyak dengan tuple/list)
        :param vals: Extra param untuk proses ``_cwrite``
        :param f_state: Field state custom
        :param as_write: Apakah mengisikan ``write_uid`` & ``write_date`` juga?
        """
        self._validate_state(new_state, f_state)
        vals = dict(vals) if vals else {}
        vals[f_state or self._rec_state] = new_state

        # field2 log
        if f_uid:
            if isinstance(f_uid, basestring):
                f_uid = (f_uid,)
            for uid in f_uid:
                vals[uid] = self.env.uid

        if f_dt:
            current_dt = fields.Datetime.now()
            if isinstance(f_dt, basestring):
                f_dt = (f_dt,)
            for dt in f_dt:
                vals[dt] = current_dt

        return self._cwrite(vals, as_write)

    @api.multi
    def _cread(self, field_list=None):
        """
        Method read yg dibuat ulang dengan query sql, dan benar2 menampilkan data nya (khusus nya many2one).

        - Untuk field2 _2M, compute (tidak store), inherits akan di skip.
        - Untuk Field2 Datetime & Date, di convert otomatis menjadi string

        :param field_list: List field apa saja yg ditampilkan. Kalau tidak di isi, menampilkan semua.
        :return: Tuple berisi dictionary data.
        """
        field_data = self._get_read_fields(field_list)
        ModelClass = self.alt_orm()
        selects = tuple(getattr(ModelClass, field) for field in field_data.keys())

        result = []
        for ids in self._balance_ids():
            for row in ModelClass.select(*selects).where(ModelClass.id.in_(ids)):
                result.append(model_to_dict(row, False, exclude=(ModelClass.id,)))

        return tuple(result)

    # public method
    @api.model
    def alt_orm(self, *target):
        """
        Generate Class ORM peewee dari object ini (kecuali ``target`` ditentukan).

        :param target: Target object ORM selain object ini.
        :return: Class Peewee hasil generate (mengembalikan tuple kalau target di isi lebih dari 1)
        """
        target = target or (self,)
        result = tuple(self._fetch_gen_alt_orm(model_target) for model_target in target)

        if len(result) == 1:
            return result[0]

        return result

    @api.model
    def get_field_string(self, field):
        """
        Mendapatkan string field.

        :param field: Nama field yang akan di dapatkan.
        :return: String field.
        """
        return self.fields_get([field])[field]["string"]

    # view
    def show_record(self, model, title, **kwargs):
        """
        Menampilkan tampilan model lain menggunakan format XML (Action).

        Nilai default nya adalah:

        - *type*: ``ir.actions.act_window``
        - *view_mode*: ``form``
        - *target*: ``current``

        :param model: Nama model yang akan di tampilkan.
        :type model: basestring
        :param title: Judul dari tampilan baru.
        :type title: basestring
        :param kwargs: Attribute2 lain untuk tampilan.
                       Attribute2 ini bisa digunakan untuk mengganti attribute default.
        :return: Dictionary untuk menampilkan act window.
        :rtype: dict
        """
        act = {
            "name": title,
            "type": "ir.actions.act_window",
            "res_model": model,
            "view_mode": "form",
            "target": "current",
        }
        act.update(kwargs)

        return act

    # override
    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        """
        Override method ``create`` untuk menambah fitur2.
        """
        self._auto_state(vals)
        self._auto_sequence(vals)

        return super(BaseModel, self).create(vals)

    @api.multi
    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """
        Override method ``copy`` untuk menambahkan fitur auto copy.

        Fitur auto copy ini menggunakan variable dictionary ``_copy_default``
        yg berisi nama field dengan nilai baru.
        """
        self.ensure_one()
        copy_default = {}
        for field, value in (self._copy_default.iteritems() if isinstance(self._copy_default, dict) else ()):
            copy_default[field] = value(self) if callable(value) else value

        default = dict(copy_default, **(default or {}))

        return super(BaseModel, self).copy(default)

    @api.multi
    def unlink(self):
        """
        Override method ``unlink``, supaya bisa hanya men deactivate record saja, tidak langsung delete.

        Field active untuk di set ``False`` di definisikan di ``_rec_active``.

        Field untuk set perlakuan ini, di definisikan di ``_unlink_deactivate``.
        """
        if self._unlink_deactivate:
            is_active = getattr(self, self._rec_active)
            if is_active:
                self.write({self._rec_active: False})
            elif not is_active and self._unlink_deactivate == 2:
                return super(BaseModel, self).unlink()

        return super(BaseModel, self).unlink()
