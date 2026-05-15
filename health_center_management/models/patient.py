from odoo import models, fields, api
from odoo.exceptions import UserError


def _notify_success(title='✔ Saved Successfully', message='Data has been saved successfully.'):
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': title,
            'message': message,
            'type': 'success',
            'sticky': False,
        }
    }


class HealthPatient(models.Model):
    _name = 'health.patient'
    _description = 'Patient'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string='Patient Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    birthdate = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female')],
        string='Gender',
        required=True,
    )
    booking_type = fields.Selection(
        selection=[('new', 'New'), ('followup', 'Follow-Up')],
        string='Booking Type',
        required=True,
    )
    clinic_id = fields.Many2one(
        'health.clinic',
        string='Clinic',
        required=True,
        ondelete='restrict',
    )
    appointment_id = fields.Many2one(
        'health.appointment',
        string='Appointment Time',
        ondelete='set null',
    )
    booking_id = fields.Many2one(
        'health.booking',
        string='Booking',
        copy=False,
    )
    booking_number = fields.Char(
        related='booking_id.name',
        string='Booking Number',
        store=True,
    )
    followup_booking_number = fields.Char(
        string='Follow-Up Booking Number',
        help='Enter the previous booking number to retrieve its medical record',
    )
    medical_record_id = fields.Many2one(
        'health.medical.record',
        string='Medical Record',
    )
    followup_medical_record_id = fields.Many2one(
        'health.medical.record',
        string='Follow-Up Medical Record',
        compute='_compute_followup_record',
        store=False,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
    )

    @api.depends('followup_booking_number', 'booking_type')
    def _compute_followup_record(self):
        for rec in self:
            if rec.followup_booking_number and rec.booking_type == 'followup':
                booking = self.env['health.booking'].search(
                    [('name', '=', rec.followup_booking_number)], limit=1
                )
                if booking:
                    record = self.env['health.medical.record'].search(
                        [('booking_id', '=', booking.id)], limit=1
                    )
                    rec.followup_medical_record_id = record.id if record else False
                else:
                    rec.followup_medical_record_id = False
            else:
                rec.followup_medical_record_id = False

    @api.onchange('followup_booking_number')
    def _onchange_followup_booking_number(self):
        if self.followup_booking_number and self.booking_type == 'followup':
            booking = self.env['health.booking'].search(
                [('name', '=', self.followup_booking_number)], limit=1
            )
            if not booking:
                return {
                    'warning': {
                        'title': 'Not Found',
                        'message': f'Booking number "{self.followup_booking_number}" was not found.',
                    }
                }
            record = self.env['health.medical.record'].search(
                [('booking_id', '=', booking.id)], limit=1
            )
            if not record:
                return {
                    'warning': {
                        'title': 'No Medical Record',
                        'message': 'No medical record found for this booking number.',
                    }
                }

    @api.onchange('clinic_id')
    def _onchange_clinic_id(self):
        self.appointment_id = False

    def action_save_confirm(self):
        return _notify_success(
            title='✔ Saved Successfully',
            message='Patient data has been saved successfully.',
        )

    def action_confirm_booking(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('Only draft bookings can be confirmed.')
            booking = self.env['health.booking'].sudo().create({
                'patient_id': rec.id,
            })
            rec.sudo().write({'booking_id': booking.id})
            if rec.appointment_id:
                rec.appointment_id.sudo().write({
                    'is_available': False,
                    'patient_id': rec.id,
                })
            if rec.booking_type == 'new':
                medical_record = self.env['health.medical.record'].sudo().create({
                    'patient_id': rec.id,
                    'booking_id': booking.id,
                    'create_date_manual': fields.Date.today(),
                })
                rec.sudo().write({'medical_record_id': medical_record.id})
            rec.sudo().write({'state': 'confirmed'})
        return _notify_success(
            title='✔ Booking Confirmed',
            message=f'Booking confirmed successfully. Booking number: {self.booking_id.name}',
        )

    def action_cancel_booking(self):
        for rec in self:
            if rec.state == 'cancelled':
                raise UserError('This booking is already cancelled.')
            if rec.appointment_id:
                rec.appointment_id.sudo().write({
                    'is_available': True,
                    'patient_id': False,
                })
            if rec.booking_id:
                rec.booking_id.sudo().write({'state': 'cancelled'})
            rec.sudo().write({'state': 'cancelled'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✖ Booking Cancelled',
                'message': 'The booking has been cancelled successfully.',
                'type': 'warning',
                'sticky': False,
            }
        }
