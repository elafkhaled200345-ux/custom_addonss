import ast
from odoo import models, fields, api
from odoo.exceptions import UserError


class HealthPortalLoginWizard(models.TransientModel):
    _name = 'health.portal.login'
    _description = 'Portal Login'

    portal_type = fields.Selection(
        selection=[
            ('employee', 'Employee Portal'),
            ('doctor', 'Doctor Portal'),
        ],
        string='Portal Type',
        required=True,
    )
    password = fields.Char(
        string='Password',
        required=True,
    )
    # Doctor-specific: which doctor is logging in
    doctor_id = fields.Many2one(
        'health.doctor',
        string='Doctor Name',
        domain=[('active', '=', True)],
        help='Select your name, then enter your personal password.',
    )

    def action_verify(self):
        self.ensure_one()

        if self.portal_type == 'employee':
            config = self.env['health.portal.config'].get_config()
            if self.password != config.employee_portal_password:
                raise UserError(
                    'Incorrect password. Access to the Employee Portal has been denied.'
                )
            return {
                'type': 'ir.actions.act_window',
                'name': 'Employee Portal',
                'res_model': 'health.portal.section',
                'view_mode': 'list',
                'views': [(
                    self.env.ref(
                        'health_center_management.view_health_portal_section_employee_list'
                    ).id,
                    'list',
                )],
                'domain': [('portal_type', '=', 'employee')],
                'context': {'create': False},
                'target': 'current',
            }

        elif self.portal_type == 'doctor':
            if not self.doctor_id:
                raise UserError('Please select your name before entering your password.')

            doctor = self.doctor_id
            if not doctor.password or doctor.password != self.password:
                raise UserError(
                    'Incorrect password. Access to the Doctor Portal has been denied.'
                )

            # Store the logged-in doctor's clinic so portal sections can filter by it
            self.env['ir.config_parameter'].sudo().set_param(
                'health_center.active_doctor_id', str(doctor.id)
            )
            self.env['ir.config_parameter'].sudo().set_param(
                'health_center.active_clinic_id', str(doctor.clinic_id.id)
            )

            return {
                'type': 'ir.actions.act_window',
                'name': f'Doctor Portal — {doctor.name} ({doctor.clinic_id.name_display})',
                'res_model': 'health.portal.section',
                'view_mode': 'list',
                'views': [(
                    self.env.ref(
                        'health_center_management.view_health_portal_section_doctor_list'
                    ).id,
                    'list',
                )],
                'domain': [('portal_type', '=', 'doctor')],
                'context': {'create': False},
                'target': 'current',
            }

        raise UserError('Unknown portal type.')
