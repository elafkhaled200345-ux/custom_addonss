from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class HealthBooking(models.Model):
    _name = 'health.booking'
    _description = 'Booking / حجز'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Booking Number / رقم الحجز', copy=False, default='/', readonly=True)
    patient_id = fields.Many2one(
        'health.patient', string='Patient / المريض', required=True,
        ondelete='restrict', tracking=True, default=lambda self: self._default_patient())
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)

    visit_type = fields.Selection(
        selection=[('new', 'New / جديد'), ('followup', 'Follow-Up / متابعة')],
        string='Visit Type / نوع الزيارة', required=True, default='new', tracking=True)
    previous_booking_id = fields.Many2one(
        'health.booking', string='Previous Booking / الحجز السابق',
        ondelete='set null', domain="[('patient_id', '=', patient_id), ('id', '!=', id)]")

    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة', required=True,
        ondelete='restrict', tracking=True)
    appointment_id = fields.Many2one(
        'health.appointment', string='Appointment / الموعد', ondelete='set null', tracking=True,
        domain="[('clinic_id', '=', clinic_id)]")
    doctor_id = fields.Many2one(
        'health.doctor', string='Doctor / الطبيب', ondelete='set null', tracking=True,
        domain="[('clinic_id', '=', clinic_id), ('active', '=', True)]")

    booking_date = fields.Date(
        string='Booking Date / تاريخ الحجز', default=fields.Date.today, required=True)
    arrival_time = fields.Datetime(string='Arrival Time / وقت الوصول', tracking=True)
    check_in_time = fields.Datetime(string='Check-in Time / وقت التسجيل', tracking=True)
    queue_number = fields.Char(string='Queue Number / رقم الانتظار', copy=False, readonly=True)
    reception_employee_id = fields.Many2one(
        'health.employee', string='Reception Employee / موظف الاستقبال',
        ondelete='set null', default=lambda self: self._default_reception_employee())
    waiting_time = fields.Float(
        string='Waiting Time (min) / مدة الانتظار',
        compute='_compute_waiting_time', store=True, digits=(16, 2))

    state = fields.Selection(
        selection=[
            ('draft', 'Draft / مسودة'),
            ('confirmed', 'Confirmed / مؤكد'),
            ('checked_in', 'Checked In / تم التسجيل'),
            ('visited', 'Visited / منتهى'),
            ('cancelled', 'Cancelled / ملغى'),
        ],
        string='Status / الحالة', default='draft', tracking=True)

    medical_record_ids = fields.One2many(
        'health.medical.record', 'booking_id', string='Medical Records / السجلات الطبية')
    invoice_ids = fields.One2many(
        'health.invoice', 'booking_id', string='Invoices / الفواتير')
    medical_record_count = fields.Integer(compute='_compute_counts')
    invoice_count = fields.Integer(compute='_compute_counts')

    @api.model
    def _default_patient(self):
        patient = self.env['health.patient'].search([('user_id', '=', self.env.user.id)], limit=1)
        return patient.id or False

    @api.model
    def _default_reception_employee(self):
        employee = self.env['health.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee.id or False

    @api.depends('arrival_time', 'check_in_time')
    def _compute_waiting_time(self):
        for rec in self:
            if rec.arrival_time and rec.check_in_time:
                delta = rec.check_in_time - rec.arrival_time
                rec.waiting_time = max(delta.total_seconds() / 60.0, 0.0)
            else:
                rec.waiting_time = 0.0

    @api.depends('medical_record_ids', 'invoice_ids')
    def _compute_counts(self):
        for rec in self:
            rec.medical_record_count = len(rec.medical_record_ids)
            rec.invoice_count = len(rec.invoice_ids)

    @api.onchange('clinic_id')
    def _onchange_clinic_id(self):
        if self.appointment_id and self.appointment_id.clinic_id != self.clinic_id:
            self.appointment_id = False
        if self.doctor_id and self.doctor_id.clinic_id != self.clinic_id:
            self.doctor_id = False

    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.clinic_id = self.appointment_id.clinic_id
            self.doctor_id = self.appointment_id.doctor_id

    @api.onchange('visit_type')
    def _onchange_visit_type(self):
        if self.visit_type != 'followup':
            self.previous_booking_id = False

    @api.constrains('previous_booking_id', 'patient_id', 'visit_type')
    def _check_previous_booking(self):
        for rec in self:
            if rec.visit_type == 'followup' and rec.previous_booking_id:
                if rec.previous_booking_id.patient_id != rec.patient_id:
                    raise ValidationError('Previous booking must belong to the same patient.')

    @api.constrains('appointment_id', 'clinic_id', 'doctor_id')
    def _check_appointment_consistency(self):
        for rec in self:
            if not rec.appointment_id:
                continue
            if rec.appointment_id.clinic_id != rec.clinic_id:
                raise ValidationError('Appointment clinic does not match the booking clinic.')
            if rec.doctor_id and rec.appointment_id.doctor_id != rec.doctor_id:
                raise ValidationError('Appointment doctor does not match the booking doctor.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.booking') or '/'
            if not vals.get('queue_number') and vals.get('state') == 'checked_in':
                vals['queue_number'] = self.env['ir.sequence'].next_by_code('health.booking.queue') or '/'
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('Only draft bookings can be confirmed. / يمكن تأكيد المسودات فقط.')
            if rec.visit_type == 'followup' and not rec.previous_booking_id:
                raise UserError('Please select the previous booking for a follow-up visit.')

            if rec.appointment_id:
                appt = rec.appointment_id
                if not appt.is_available and appt.patient_id != rec.patient_id:
                    raise UserError('This appointment is no longer available. / الموعد لم يعد متاحاً.')
                appt.sudo().write({
                    'is_available': False,
                    'state': 'booked',
                    'patient_id': rec.patient_id.id,
                })
                rec.doctor_id = appt.doctor_id
                rec.clinic_id = appt.clinic_id

            rec.write({'state': 'confirmed'})

            if not rec.medical_record_ids:
                self.env['health.medical.record'].sudo().create({
                    'booking_id': rec.id,
                    'patient_id': rec.patient_id.id,
                    'clinic_id': rec.clinic_id.id,
                    'doctor_id': rec.doctor_id.id or False,
                    'create_date_manual': fields.Date.today(),
                })

            fee = rec.appointment_id.examination_fees if rec.appointment_id else 0.0
            if fee and not rec.invoice_ids:
                self.env['health.invoice'].sudo().create({
                    'booking_id': rec.id,
                    'patient_id': rec.patient_id.id,
                    'clinic_id': rec.clinic_id.id,
                    'appointment_id': rec.appointment_id.id,
                    'consultation_fee': fee,
                    'invoice_status': 'unpaid',
                    'invoice_date': fields.Date.today(),
                })

            rec.message_post(body=f'✔ Booking confirmed: {rec.name}', message_type='notification')
        return True

    def action_check_in(self):
        if not self.env.user.has_group('health_center_management.group_health_employee'):
            raise UserError('Only health center employees can check patients in.')
        now = fields.Datetime.now()
        for rec in self:
            if rec.state not in ('confirmed', 'checked_in'):
                raise UserError('Only confirmed bookings can be checked in.')
            vals = {
                'state': 'checked_in',
                'check_in_time': rec.check_in_time or now,
                'arrival_time': rec.arrival_time or now,
            }
            if not rec.queue_number:
                vals['queue_number'] = self.env['ir.sequence'].next_by_code('health.booking.queue') or '/'
            if not rec.reception_employee_id:
                vals['reception_employee_id'] = self._default_reception_employee()
            rec.write(vals)
        return True

    def action_mark_visited(self):
        if not self.env.user.has_group('health_center_management.group_health_employee'):
            raise UserError('Only health center employees can complete visits.')
        for rec in self:
            if rec.state not in ('confirmed', 'checked_in'):
                raise UserError('Only confirmed/checked-in bookings can be completed.')
            rec.write({'state': 'visited'})
            if rec.appointment_id:
                rec.appointment_id.sudo().write({'state': 'done', 'is_available': False})
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ('visited', 'cancelled'):
                raise UserError('Completed or cancelled bookings cannot be cancelled again.')
            if rec.appointment_id and rec.appointment_id.patient_id == rec.patient_id:
                rec.appointment_id.sudo().write({
                    'is_available': True,
                    'state': 'available',
                    'patient_id': False,
                })
            rec.write({'state': 'cancelled'})
        return True
