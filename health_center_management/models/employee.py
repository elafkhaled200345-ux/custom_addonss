# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from werkzeug.security import generate_password_hash, check_password_hash


class HealthEmployee(models.Model):
    _name = 'health.employee'
    _description = 'Employee / موظف'
    _rec_name = 'name'
    _order = 'sequence asc, name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Employee Name / اسم الموظف', required=True, tracking=True)
    job_title = fields.Char(string='Job Title / المسمى الوظيفي', tracking=True)
    role = fields.Selection(
        selection=[
            ('receptionist', 'Receptionist / استقبال'),
            ('nurse', 'Nurse / ممرض'),
            ('lab_tech', 'Lab Technician / فني مختبر'),
            ('pharmacist', 'Pharmacist / صيدلاني'),
            ('accountant', 'Accountant / محاسب'),
            ('admin', 'Administrator / مدير'),
            ('other', 'Other / أخرى'),
        ],
        string='Role / الدور', default='receptionist', tracking=True,
    )
    department = fields.Char(string='Department / القسم')
    hire_date = fields.Date(string='Hire Date / تاريخ التعيين')
    national_id = fields.Char(string='National ID / الهوية الوطنية')
    user_id = fields.Many2one(
        'res.users', string='System User / مستخدم النظام', ondelete='set null', copy=False)
    signature = fields.Image(string='Signature / التوقيع', max_width=512, max_height=256)
    phone = fields.Char(string='Phone / هاتف')
    email = fields.Char(string='Email')
    clinic_id = fields.Many2one('health.clinic', string='Clinic / العيادة', ondelete='set null')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    notes = fields.Text(string='Notes / ملاحظات')

    password_hash = fields.Char(string='Password Hash', copy=False,
        groups='health_center_management.group_health_manager')
    password_set = fields.Char(
        string='Set New Password / تعيين كلمة مرور جديدة',
        store=False, copy=False,
        groups='health_center_management.group_health_manager',
        help='اكتب كلمة مرور جديدة. اتركه فارغاً للإبقاء على الحالية.',
    )
    password_status = fields.Char(
        string='Password Status / حالة كلمة المرور',
        compute='_compute_password_status', store=False,
    )

    @api.depends('password_hash')
    def _compute_password_status(self):
        for rec in self:
            rec.password_status = '✅ مُعيَّنة' if rec.password_hash else '❌ لم تُعيَّن بعد'

    def verify_password(self, plain_password):
        self.ensure_one()
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, plain_password)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if plain := vals.pop('password_set', None):
                if len(plain) < 4:
                    raise UserError('Password must be at least 4 characters.')
                vals['password_hash'] = generate_password_hash(plain)
        return super().create(vals_list)

    def write(self, vals):
        if plain := vals.pop('password_set', None):
            if len(plain) < 4:
                raise UserError('Password must be at least 4 characters.')
            vals['password_hash'] = generate_password_hash(plain)
        return super().write(vals)
