# -*- coding: utf-8 -*-
from odoo import models, fields, api
from werkzeug.security import generate_password_hash, check_password_hash


class HealthPortalConfig(models.Model):
    _name = 'health.portal.config'
    _description = 'Portal Access Configuration / إعدادات بوابة الدخول'

    name = fields.Char(string='Configuration Name', required=True, default='Portal Configuration')

    # ─── Employee Portal ────────────────────────────────────────
    employee_portal_password_hash = fields.Char(string='Employee Portal Password Hash', copy=False)
    employee_password_set = fields.Char(
        string='Employee Portal Password / كلمة مرور بوابة الموظفين',
        store=False, copy=False,
        help='كلمة مرور مشتركة لبوابة الموظفين.',
    )
    employee_password_status = fields.Char(
        string='Employee Password Status', compute='_compute_statuses', store=False)

    # ─── Reports Portal ─────────────────────────────────────────
    reports_portal_password_hash = fields.Char(string='Reports Portal Password Hash', copy=False)
    reports_password_set = fields.Char(
        string='Reports Portal Password / كلمة مرور بوابة التقارير',
        store=False, copy=False,
        help='كلمة المرور المستقلة للدخول إلى بوابة التقارير.',
    )
    reports_password_status = fields.Char(
        string='Reports Password Status', compute='_compute_statuses', store=False)

    @api.depends('employee_portal_password_hash', 'reports_portal_password_hash')
    def _compute_statuses(self):
        for rec in self:
            rec.employee_password_status = '✅ مُعيَّنة' if rec.employee_portal_password_hash else '❌ غير مُعيَّنة'
            rec.reports_password_status = '✅ مُعيَّنة' if rec.reports_portal_password_hash else '❌ غير مُعيَّنة'

    def verify_employee_password(self, plain_password):
        self.ensure_one()
        if not self.employee_portal_password_hash:
            return False
        return check_password_hash(self.employee_portal_password_hash, plain_password)

    def verify_reports_password(self, plain_password):
        self.ensure_one()
        if not self.reports_portal_password_hash:
            return False
        return check_password_hash(self.reports_portal_password_hash, plain_password)

    def write(self, vals):
        if plain := vals.pop('employee_password_set', None):
            vals['employee_portal_password_hash'] = generate_password_hash(plain)
        if plain := vals.pop('reports_password_set', None):
            vals['reports_portal_password_hash'] = generate_password_hash(plain)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if plain := vals.pop('employee_password_set', None):
                vals['employee_portal_password_hash'] = generate_password_hash(plain)
            if plain := vals.pop('reports_password_set', None):
                vals['reports_portal_password_hash'] = generate_password_hash(plain)
        return super().create(vals_list)

    @api.model
    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create({'name': 'Portal Configuration'})
        return config
