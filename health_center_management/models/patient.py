from odoo import models, fields, api


class HealthPatient(models.Model):
    _name = 'health.patient'
    _description = 'Patient / مريض'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Patient is a master-data entity. Visit-specific data belongs to
    # appointment/booking/medical-record/invoice records, not here.
    user_id = fields.Many2one(
        'res.users', string='Portal User / مستخدم البوابة',
        ondelete='set null', copy=False,
        help='ربط المريض بحساب مستخدم Odoo لعرض بياناته في البوابة.',
    )

    name = fields.Char(string='Patient Name / اسم المريض', required=True, tracking=True)
    phone = fields.Char(string='Phone / هاتف', required=True)
    email = fields.Char(string='Email')
    birthdate = fields.Date(string='Date of Birth / تاريخ الميلاد', required=True)
    age = fields.Integer(string='Age / العمر', compute='_compute_age', store=True)
    gender = fields.Selection(
        selection=[('male', 'Male / ذكر'), ('female', 'Female / أنثى')],
        string='Gender / الجنس', required=True, tracking=True,
    )
    national_id = fields.Char(string='National ID / Iqama / الهوية', size=10)
    blood_type = fields.Selection(
        selection=[
            ('a+', 'A+'), ('a-', 'A−'), ('b+', 'B+'), ('b-', 'B−'),
            ('ab+', 'AB+'), ('ab-', 'AB−'), ('o+', 'O+'), ('o-', 'O−'),
        ],
        string='Blood Type / فصيلة الدم',
    )
    allergies = fields.Text(string='Allergies / الحساسية')
    notes = fields.Text(string='General Notes / ملاحظات عامة')
    photo = fields.Image(string='Photo / صورة', max_width=256, max_height=256)

    insurance_company = fields.Char(string='Insurance Company / شركة التأمين')
    insurance_number = fields.Char(string='Insurance Number / رقم التأمين')
    insurance_expiry = fields.Date(string='Insurance Expiry / انتهاء التأمين')

    emergency_contact = fields.Char(string='Emergency Contact Name / اسم جهة الطوارئ')
    emergency_phone = fields.Char(string='Emergency Phone / هاتف الطوارئ')
    emergency_relation = fields.Char(string='Relation / صلة القرابة')

    # Reverse relations only; these do not store a single visit on the patient.
    appointment_ids = fields.One2many(
        'health.appointment', 'patient_id', string='Appointments / المواعيد')
    booking_ids = fields.One2many(
        'health.booking', 'patient_id', string='Bookings / الحجوزات')
    medical_record_ids = fields.One2many(
        'health.medical.record', 'patient_id', string='Medical Records / السجلات الطبية')
    invoice_ids = fields.One2many(
        'health.invoice', 'patient_id', string='Invoices / الفواتير')

    appointment_count = fields.Integer(compute='_compute_counts', string='Appointments')
    booking_count = fields.Integer(compute='_compute_counts', string='Bookings')
    medical_record_count = fields.Integer(compute='_compute_counts', string='Medical Records')
    invoice_count = fields.Integer(compute='_compute_counts', string='Invoices')

    @api.depends('birthdate')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.birthdate:
                b = rec.birthdate
                rec.age = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
            else:
                rec.age = 0

    @api.depends('appointment_ids', 'booking_ids', 'medical_record_ids', 'invoice_ids')
    def _compute_counts(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)
            rec.booking_count = len(rec.booking_ids)
            rec.medical_record_count = len(rec.medical_record_ids)
            rec.invoice_count = len(rec.invoice_ids)

    def action_new_booking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Booking / حجز جديد',
            'res_model': 'health.booking',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_patient_id': self.id},
        }

    def _open_related(self, model, domain, name, context=None):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': model,
            'view_mode': 'list,form',
            'domain': domain,
            'context': context or {},
        }

    def action_view_bookings(self):
        return self._open_related(
            'health.booking', [('patient_id', '=', self.id)],
            'Bookings / الحجوزات', {'default_patient_id': self.id})

    def action_view_appointments(self):
        action = self._open_related(
            'health.appointment', [('patient_id', '=', self.id)],
            'Appointments / المواعيد')
        action['view_mode'] = 'calendar,list,form'
        return action

    def action_view_medical_records(self):
        return self._open_related(
            'health.medical.record', [('patient_id', '=', self.id)],
            'Medical Records / السجلات الطبية')

    def action_view_invoices(self):
        return self._open_related(
            'health.invoice', [('patient_id', '=', self.id)],
            'Invoices / الفواتير')
