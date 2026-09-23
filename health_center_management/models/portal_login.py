# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class HealthPortalLoginWizard(models.TransientModel):
    _name = 'health.portal.login'
    _description = 'Portal Login / دخول البوابة'

    portal_type = fields.Selection(
        selection=[
            ('employee', 'Employee Portal / بوابة الموظف'),
            ('doctor', 'Doctor Portal / بوابة الطبيب'),
        ],
        string='Portal Type / نوع البوابة', required=True,
    )
    password = fields.Char(string='Password / كلمة المرور', required=True)
    doctor_id = fields.Many2one('health.doctor', string='Doctor Name / اسم الطبيب',
        domain=[('active', '=', True)])
    employee_id = fields.Many2one('health.employee', string='Employee Name / اسم الموظف',
        domain=[('active', '=', True)],
        help='اختياري: اختر اسمك إذا كان لك كلمة مرور فردية.')

    def action_verify(self):
        self.ensure_one()

        if self.portal_type == 'employee':
            access_ok = False
            if self.employee_id:
                access_ok = self.employee_id.verify_password(self.password)
            if not access_ok:
                config = self.env['health.portal.config'].get_config()
                access_ok = config.verify_employee_password(self.password)
            if not access_ok:
                raise UserError(
                    'كلمة المرور غير صحيحة. تم رفض الدخول.\nIncorrect password.')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Employee Portal / بوابة الموظف',
                'res_model': 'health.employee.hub',
                'view_mode': 'form',
                'target': 'current',
                'context': {'create': False, 'delete': False},
            }

        elif self.portal_type == 'doctor':
            if not self.doctor_id:
                raise UserError(
                    'يرجى اختيار اسمك أولاً.\nPlease select your name first.')
            if not self.doctor_id.verify_password(self.password):
                raise UserError(
                    'كلمة المرور غير صحيحة. تم رفض الدخول.\nIncorrect password.')
            hub = self.env['health.doctor.hub'].create({
                'doctor_id': self.doctor_id.id,
                'clinic_id': self.doctor_id.clinic_id.id,
            })
            return {
                'type': 'ir.actions.act_window',
                'name': f'Dr. {self.doctor_id.name} — Portal',
                'res_model': 'health.doctor.hub',
                'res_id': hub.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {'create': False, 'delete': False},
            }

        raise UserError('Unknown portal type.')
