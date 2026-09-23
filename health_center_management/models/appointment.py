from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime


class HealthAppointment(models.Model):
    _name = 'health.appointment'
    _description = 'Appointment / موعد'
    _rec_name = 'slot_label'
    _order = 'appointment_date asc, appointment_time asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Appointment Number', copy=False, default='/', readonly=True)
    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة', required=True,
        ondelete='cascade', tracking=True)
    doctor_id = fields.Many2one(
        'health.doctor', string='Doctor / الطبيب', ondelete='set null', tracking=True,
        domain="[('clinic_id', '=', clinic_id), ('active', '=', True)]")
    appointment_type = fields.Selection(
        selection=[
            ('consultation', 'Consultation / استشارة'),
            ('followup', 'Follow-Up / متابعة'),
            ('emergency', 'Emergency / طوارئ'),
        ],
        string='Appointment Type / نوع الموعد', default='consultation', required=True, tracking=True)
    appointment_date = fields.Date(
        string='Appointment Date / تاريخ الموعد', required=True,
        default=fields.Date.today, tracking=True)
    appointment_time = fields.Selection(
        selection=[
            ('07:00', '07:00 AM'), ('07:30', '07:30 AM'), ('08:00', '08:00 AM'),
            ('08:30', '08:30 AM'), ('09:00', '09:00 AM'), ('09:30', '09:30 AM'),
            ('10:00', '10:00 AM'), ('10:30', '10:30 AM'), ('11:00', '11:00 AM'),
            ('11:30', '11:30 AM'), ('12:00', '12:00 PM'), ('12:30', '12:30 PM'),
            ('13:00', '01:00 PM'), ('13:30', '01:30 PM'), ('14:00', '02:00 PM'),
            ('14:30', '02:30 PM'), ('15:00', '03:00 PM'), ('15:30', '03:30 PM'),
            ('16:00', '04:00 PM'), ('16:30', '04:30 PM'), ('17:00', '05:00 PM'),
            ('17:30', '05:30 PM'), ('18:00', '06:00 PM'), ('18:30', '06:30 PM'),
            ('19:00', '07:00 PM'), ('19:30', '07:30 PM'), ('20:00', '08:00 PM'),
        ],
        string='Time / الوقت', required=True, tracking=True)
    duration = fields.Float(string='Duration (min) / المدة', default=30.0)
    is_available = fields.Boolean(string='Available / متاح', default=True, tracking=True)
    state = fields.Selection(
        selection=[
            ('available', 'Available / متاح'),
            ('booked', 'Booked / محجوز'),
            ('done', 'Done / منتهى'),
            ('no_show', 'No Show / لم يحضر'),
            ('cancelled', 'Cancelled / ملغى'),
        ],
        string='Status', default='available', tracking=True)
    patient_id = fields.Many2one(
        'health.patient', string='Booked Patient / المريض', ondelete='set null', tracking=True)
    booking_ids = fields.One2many('health.booking', 'appointment_id', string='Bookings / الحجوزات')
    examination_fees = fields.Float(
        string='Consultation Fee / رسوم الكشف', digits=(16, 2), default=0.0, tracking=True)
    notes = fields.Text(string='Notes / ملاحظات')
    slot_label = fields.Char(string='Appointment Slot', compute='_compute_slot_label', store=True)
    start_datetime = fields.Datetime(string='Start', compute='_compute_datetimes', store=True)
    stop_datetime = fields.Datetime(string='End', compute='_compute_datetimes', store=True)

    _sql_constraints = [(
        'unique_clinic_doctor_date_time',
        'UNIQUE(clinic_id, doctor_id, appointment_date, appointment_time)',
        'This doctor already has a slot at this date and time.',
    )]

    @api.depends('appointment_date', 'appointment_time', 'clinic_id', 'doctor_id')
    def _compute_slot_label(self):
        for rec in self:
            clinic = rec.clinic_id.name or ''
            doctor = f' — Dr. {rec.doctor_id.name}' if rec.doctor_id else ''
            time = rec.appointment_time or ''
            rec.slot_label = f"{rec.appointment_date} {time} ({clinic}{doctor})"

    @api.depends('appointment_date', 'appointment_time', 'duration')
    def _compute_datetimes(self):
        for rec in self:
            if rec.appointment_date and rec.appointment_time:
                h, m = map(int, rec.appointment_time.split(':'))
                start = datetime.datetime.combine(rec.appointment_date, datetime.time(h, m))
                rec.start_datetime = start
                rec.stop_datetime = start + datetime.timedelta(minutes=rec.duration or 30)
            else:
                rec.start_datetime = False
                rec.stop_datetime = False

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        if self.doctor_id and self.doctor_id.consultation_fee:
            self.examination_fees = self.doctor_id.consultation_fee

    @api.constrains('appointment_date')
    def _check_future_date(self):
        today = fields.Date.today()
        for rec in self:
            if rec.appointment_date and rec.appointment_date < today and rec.state == 'available':
                raise ValidationError('Appointment date cannot be in the past.\nلا يمكن أن يكون تاريخ الموعد في الماضي.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.appointment') or '/'
        return super().create(vals_list)

    def action_mark_done(self):
        self.write({'state': 'done', 'is_available': False})

    def action_mark_no_show(self):
        self.write({'state': 'no_show', 'is_available': False})

    def action_cancel(self):
        self.write({'state': 'cancelled', 'is_available': False})

    def action_reset(self):
        self.write({'state': 'available', 'is_available': True, 'patient_id': False})
