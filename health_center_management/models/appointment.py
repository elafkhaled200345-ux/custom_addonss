from odoo import models, fields, api


class HealthAppointment(models.Model):
    _name = 'health.appointment'
    _description = 'Appointment'
    _rec_name = 'slot_label'
    _order = 'appointment_date asc, appointment_time asc'

    sequence = fields.Integer(string='Sequence', default=10)
    clinic_id = fields.Many2one(
        'health.clinic',
        string='Clinic',
        required=True,
        ondelete='cascade',
    )
    appointment_date = fields.Date(
        string='Appointment Date',
        required=True,
        default=fields.Date.today,
    )
    appointment_time = fields.Selection(
        selection=[
            ('08:00', '08:00 AM'),
            ('08:30', '08:30 AM'),
            ('09:00', '09:00 AM'),
            ('09:30', '09:30 AM'),
            ('10:00', '10:00 AM'),
            ('10:30', '10:30 AM'),
            ('11:00', '11:00 AM'),
            ('11:30', '11:30 AM'),
            ('12:00', '12:00 PM'),
            ('12:30', '12:30 PM'),
            ('13:00', '01:00 PM'),
            ('13:30', '01:30 PM'),
            ('14:00', '02:00 PM'),
            ('14:30', '02:30 PM'),
            ('15:00', '03:00 PM'),
            ('15:30', '03:30 PM'),
            ('16:00', '04:00 PM'),
        ],
        string='Appointment Time',
        required=True,
    )
    is_available = fields.Boolean(
        string='Available',
        default=True,
    )
    patient_id = fields.Many2one(
        'health.patient',
        string='Booked Patient',
    )
    slot_label = fields.Char(
        string='Appointment Slot',
        compute='_compute_slot_label',
        store=True,
    )

    @api.depends('appointment_date', 'appointment_time', 'clinic_id')
    def _compute_slot_label(self):
        for rec in self:
            clinic = rec.clinic_id.name_display or ''
            rec.slot_label = f"{rec.appointment_date} {rec.appointment_time} ({clinic})"

    def action_save_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Appointment data has been saved successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
