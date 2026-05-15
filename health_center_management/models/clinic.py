from odoo import models, fields, api


CLINIC_NAMES = [
    ('dentistry', 'Dentistry'),
    ('internal_medicine', 'Internal Medicine'),
    ('cardiology', 'Cardiology'),
    ('surgery', 'Surgery'),
    ('pediatrics', 'Pediatrics'),
    ('nephrology', 'Nephrology'),
    ('ophthalmology', 'Ophthalmology'),
]


class HealthClinic(models.Model):
    _name = 'health.clinic'
    _description = 'Clinic'
    _rec_name = 'name_display'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Selection(
        selection=CLINIC_NAMES,
        string='Clinic',
        required=True,
    )
    name_display = fields.Char(
        string='Clinic Name',
        compute='_compute_name_display',
        store=True,
    )
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
    appointment_ids = fields.One2many(
        'health.appointment', 'clinic_id',
        string='Appointments',
    )
    doctor_ids = fields.One2many(
        'health.doctor', 'clinic_id',
        string='Doctors',
    )

    @api.depends('name')
    def _compute_name_display(self):
        mapping = dict(CLINIC_NAMES)
        for rec in self:
            rec.name_display = mapping.get(rec.name, rec.name or '')

    @api.depends('appointment_ids', 'appointment_ids.is_available', 'appointment_ids.appointment_date')
    def _compute_status(self):
        today = fields.Date.today()
        for rec in self:
            available = any(
                a.appointment_date == today and a.is_available
                for a in rec.appointment_ids
            )
            rec.status = available
            rec.status_label = 'Available' if available else 'Not Available'

    def action_save_confirm(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Clinic data has been saved successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
