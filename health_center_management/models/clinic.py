from odoo import models, fields, api


class HealthClinic(models.Model):
    _name = 'health.clinic'
    _description = 'Clinic / عيادة'
    _rec_name = 'name'
    _order = 'sequence asc, name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(string='Sequence', default=10)

    name = fields.Char(
        string='Clinic Name / اسم العيادة',
        required=True,
        tracking=True,
    )
    specialty = fields.Char(
        string='Specialty / التخصص',
        help='Medical specialty (e.g. Cardiology, Dentistry…)',
        tracking=True,
    )
    phone = fields.Char(string='Phone / هاتف')
    email = fields.Char(string='Email')
    location = fields.Char(string='Location / الموقع', help='Floor / room number')
    active = fields.Boolean(string='Active', default=True, tracking=True)

    appointment_ids = fields.One2many(
        'health.appointment', 'clinic_id', string='Appointments')
    doctor_ids = fields.One2many(
        'health.doctor', 'clinic_id', string='Doctors')

    appointment_count = fields.Integer(
        string='Appointments', compute='_compute_counts')
    doctor_count = fields.Integer(
        string='Doctors', compute='_compute_counts')
    patient_count = fields.Integer(
        string='Patients Today', compute='_compute_counts')

    status = fields.Boolean(
        string='Available Today',
        compute='_compute_status',
        store=False,
    )
    status_label = fields.Char(
        string='Status',
        compute='_compute_status',
        store=False,
    )

    @api.depends('appointment_ids', 'appointment_ids.is_available',
                 'appointment_ids.appointment_date')
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            available = any(
                a.appointment_date == today and a.is_available
                for a in rec.appointment_ids
            )
            rec.status = available
            rec.status_label = 'Available / متاحة' if available else 'Not Available / غير متاحة'

    @api.depends('appointment_ids', 'doctor_ids')
    def _compute_counts(self):
        today = fields.Date.today()
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)
            rec.doctor_count = len(rec.doctor_ids)
            bookings = self.env['health.booking'].search([
                ('clinic_id', '=', rec.id),
                ('booking_date', '=', today),
                ('state', 'in', ['confirmed', 'checked_in', 'visited']),
            ])
            rec.patient_count = len(set(bookings.mapped('patient_id').ids))

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Appointments — {self.name}',
            'res_model': 'health.appointment',
            'view_mode': 'calendar,list,form',
            'domain': [('clinic_id', '=', self.id)],
            'context': {'default_clinic_id': self.id},
        }

    def action_view_doctors(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Doctors — {self.name}',
            'res_model': 'health.doctor',
            'view_mode': 'list,form',
            'domain': [('clinic_id', '=', self.id)],
            'context': {'default_clinic_id': self.id},
        }
