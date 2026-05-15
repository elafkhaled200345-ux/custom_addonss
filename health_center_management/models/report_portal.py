from odoo import models, fields, api
from odoo.exceptions import UserError


class HealthReportPortalLogin(models.TransientModel):
    _name = 'health.report.portal.login'
    _description = 'Reports Portal Login'

    portal_type = fields.Selection(
        selection=[
            ('employee', 'Employee Portal'),
            ('doctor', 'Doctor Portal'),
        ],
        string='Login As',
        required=True,
        default='employee',
    )
    password = fields.Char(string='Password', required=True)

    def action_login(self):
        self.ensure_one()
        config = self.env['health.portal.config'].get_config()
        if self.portal_type == 'employee':
            if self.password != config.employee_portal_password:
                raise UserError('Incorrect password. Access denied.')
        else:
            if self.password != config.manager_portal_password:
                raise UserError('Incorrect password. Access denied.')
        hub = self.env['health.report.hub'].create({})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports Portal',
            'res_model': 'health.report.hub',
            'res_id': hub.id,
            'view_mode': 'form',
            'view_id': self.env.ref(
                'health_center_management.view_health_report_hub_form'
            ).id,
            'target': 'current',
        }


class HealthReportHub(models.TransientModel):
    _name = 'health.report.hub'
    _description = 'Reports Hub'

    def _report_action(self, xml_id, model, domain=None):
        records = self.env[model].search(domain or [])
        return self.env.ref(xml_id).report_action(records)

    def action_print_patient_list(self):
        return self._report_action(
            'health_center_management.report_health_patient_list',
            'health.patient',
        )

    def action_print_doctor_list(self):
        return self._report_action(
            'health_center_management.report_health_doctor_list',
            'health.doctor',
        )

    def action_print_clinic_schedule(self):
        return self._report_action(
            'health_center_management.report_health_clinic',
            'health.clinic',
        )

    def action_print_booking_list(self):
        return self._report_action(
            'health_center_management.report_health_booking_list',
            'health.booking',
        )

    def action_print_appointment_schedule(self):
        return self._report_action(
            'health_center_management.report_health_appointment',
            'health.appointment',
        )

    def action_print_medical_records(self):
        return self._report_action(
            'health_center_management.report_health_medical_record',
            'health.medical.record',
        )

    def action_print_examination_list(self):
        return self._report_action(
            'health_center_management.report_health_examination_list',
            'health.examination',
        )
