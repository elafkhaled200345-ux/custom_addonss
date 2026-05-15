from odoo import models, fields, api


class HealthDoctor(models.Model):
    _name = 'health.doctor'
    _description = 'Doctor'
    _rec_name = 'name'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Doctor Name', required=True)
    clinic_id = fields.Many2one(
        'health.clinic',
        string='Clinic',
        required=True,
        ondelete='restrict',
    )
    clinic_name = fields.Char(
        related='clinic_id.name_display',
        string='Clinic Name',
        readonly=True,
    )
    password = fields.Char(
        string='Password',
        required=True,
        help='Doctor login password',
    )
    user_id = fields.Many2one(
        'res.users',
        string='System User',
        ondelete='set null',
    )
    active = fields.Boolean(string='Active', default=True)

    def verify_password(self, password):
        self.ensure_one()
        return self.password == password

    @api.model
    def authenticate_doctor(self, clinic_name, password):
        doctors = self.search([('clinic_id.name', '=', clinic_name)])
        for doctor in doctors:
            if doctor.verify_password(password):
                return doctor
        return False

    def action_save_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Doctor data has been saved successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
