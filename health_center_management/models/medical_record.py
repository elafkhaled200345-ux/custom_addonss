from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HealthMedicalRecord(models.Model):
    _name = 'health.medical.record'
    _description = 'Medical Record / السجل الطبي'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Record Number / رقم السجل', copy=False, default='/', readonly=True)
    patient_id = fields.Many2one(
        'health.patient', string='Patient / المريض', required=True,
        ondelete='restrict', tracking=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    booking_id = fields.Many2one(
        'health.booking', string='Booking / الحجز', ondelete='restrict', tracking=True)
    booking_number = fields.Char(related='booking_id.name', string='Booking Number', store=True)
    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة', required=True,
        ondelete='restrict', tracking=True)
    doctor_id = fields.Many2one(
        'health.doctor', string='Doctor / الطبيب', ondelete='set null', tracking=True)
    create_date_manual = fields.Date(
        string='Visit Date / تاريخ الزيارة', default=fields.Date.today, tracking=True)
    follow_up_date = fields.Date(string='Follow-Up Date / موعد المتابعة', tracking=True)

    chief_complaint = fields.Char(string='Chief Complaint / الشكوى الرئيسية', tracking=True)
    bp = fields.Char(string='Blood Pressure / ضغط الدم', help='e.g. 120/80')
    hr = fields.Integer(string='Heart Rate / النبض', help='bpm')
    temperature = fields.Float(string='Temperature / الحرارة', digits=(4, 1), help='°C')
    o2_sat = fields.Integer(string='O2 Saturation / تشبع الأكسجين', help='%')
    weight = fields.Float(string='Weight / الوزن', digits=(5, 1), help='kg')
    height = fields.Float(string='Height / الطول', digits=(5, 1), help='cm')
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True, digits=(4, 1))

    clinical_notes = fields.Text(string='Clinical Findings / الفحص السريري')
    diagnosis = fields.Text(string='Diagnosis / التشخيص', tracking=True)
    diagnosis_code = fields.Char(
        string='Diagnosis Code (ICD-10) / رمز التشخيص',
        help='ICD-10 diagnosis code, e.g. J06.9')
    report = fields.Text(string='Medical Report / التقرير الطبي')

    examination_ids = fields.One2many(
        'health.examination', 'medical_record_id', string='Examinations / الفحوصات')
    lab_request_ids = fields.One2many(
        'health.lab.request', 'medical_record_id', string='Lab Requests / طلبات المختبر')
    prescription_ids = fields.One2many(
        'health.prescription', 'medical_record_id', string='Prescriptions / الوصفات الطبية')

    examination_count = fields.Integer(string='Examinations', compute='_compute_counts')
    lab_request_count = fields.Integer(string='Lab Requests', compute='_compute_counts')
    prescription_count = fields.Integer(string='Prescriptions', compute='_compute_counts')

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for rec in self:
            if rec.weight and rec.height:
                h_m = rec.height / 100.0
                rec.bmi = round(rec.weight / (h_m * h_m), 1)
            else:
                rec.bmi = 0.0

    @api.depends('examination_ids', 'lab_request_ids', 'prescription_ids')
    def _compute_counts(self):
        for rec in self:
            rec.examination_count = len(rec.examination_ids)
            rec.lab_request_count = len(rec.lab_request_ids)
            rec.prescription_count = len(rec.prescription_ids)

    @api.onchange('booking_id')
    def _onchange_booking_id(self):
        if self.booking_id:
            self.patient_id = self.booking_id.patient_id
            self.clinic_id = self.booking_id.clinic_id
            self.doctor_id = self.booking_id.doctor_id

    @api.constrains('booking_id', 'patient_id', 'clinic_id', 'doctor_id')
    def _check_booking_consistency(self):
        for rec in self:
            if not rec.booking_id:
                continue
            if rec.patient_id != rec.booking_id.patient_id or rec.clinic_id != rec.booking_id.clinic_id:
                raise ValidationError('Medical record patient/clinic must match the selected booking.')
            if rec.doctor_id and rec.booking_id.doctor_id and rec.doctor_id != rec.booking_id.doctor_id:
                raise ValidationError('Medical record doctor must match the selected booking.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            booking = self.env['health.booking'].browse(vals.get('booking_id')).exists()
            if booking:
                vals.setdefault('patient_id', booking.patient_id.id)
                vals.setdefault('clinic_id', booking.clinic_id.id)
                vals.setdefault('doctor_id', booking.doctor_id.id or False)
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.medical.record') or '/'
        return super().create(vals_list)

    def action_create_followup_appointment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Follow-Up Booking / حجز متابعة',
            'res_model': 'health.booking',
            'view_mode': 'form',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_visit_type': 'followup',
                'default_previous_booking_id': self.booking_id.id,
                'default_clinic_id': self.clinic_id.id,
                'default_doctor_id': self.doctor_id.id,
            },
        }

    def action_view_examinations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': 'Examinations / الفحوصات',
            'res_model': 'health.examination', 'view_mode': 'list,form',
            'domain': [('medical_record_id', '=', self.id)],
            'context': {'default_medical_record_id': self.id},
        }

    def action_view_lab_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': 'Lab Requests / طلبات المختبر',
            'res_model': 'health.lab.request', 'view_mode': 'list,form',
            'domain': [('medical_record_id', '=', self.id)],
            'context': {
                'default_medical_record_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'default_clinic_id': self.clinic_id.id,
            },
        }

    def action_view_prescriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': 'Prescriptions / الوصفات الطبية',
            'res_model': 'health.prescription', 'view_mode': 'list,form',
            'domain': [('medical_record_id', '=', self.id)],
            'context': {'default_medical_record_id': self.id},
        }
