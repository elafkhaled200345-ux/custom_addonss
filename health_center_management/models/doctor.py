from odoo import models, fields, api
from odoo.exceptions import UserError
from werkzeug.security import generate_password_hash, check_password_hash


class HealthDoctor(models.Model):
    _name = 'health.doctor'
    _description = 'Doctor / طبيب'
    _rec_name = 'name'
    _order = 'sequence asc, name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Doctor Name / اسم الطبيب', required=True, tracking=True)
    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة',
        required=True, ondelete='restrict', tracking=True,
    )
    clinic_name = fields.Char(
        related='clinic_id.name', string='Clinic Name', readonly=True)
    speciality = fields.Char(
        string='Speciality / التخصص',
        help='Medical speciality (e.g. Cardiologist, Dentist…)',
        tracking=True,
    )
    phone = fields.Char(string='Phone / هاتف')
    email = fields.Char(string='Email')
    consultation_fee = fields.Float(
        string='Consultation Fee / رسوم الكشف',
        digits=(16, 2), default=0.0,
        tracking=True,
    )
    active = fields.Boolean(string='Active', default=True, tracking=True)

    # Hashed password — never stored as plain text
    password_hash = fields.Char(
        string='Password Hash',
        copy=False,
        groups='health_center_management.group_health_employee',
        help='Stored as bcrypt hash — never plain text',
    )
    # Write-only helper: set a new password through the UI
    password_set = fields.Char(
        string='Set New Password',
        store=False,
        copy=False,
        groups='health_center_management.group_health_employee',
        help='Type a new password here to update it. Leave blank to keep current.',
    )

    user_id = fields.Many2one('res.users', string='System User', ondelete='set null')

    appointment_count = fields.Integer(
        string='Appointments', compute='_compute_appointment_count')

    @api.depends('clinic_id')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['health.appointment'].search_count([
                ('doctor_id', '=', rec.id)])

    def set_password(self, plain_password):
        """Hash and store a new password."""
        self.ensure_one()
        if not plain_password or len(plain_password) < 4:
            raise UserError('Password must be at least 4 characters.')
        self.sudo().write({'password_hash': generate_password_hash(plain_password)})

    def verify_password(self, plain_password):
        """Return True if the plain password matches the stored hash."""
        self.ensure_one()
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, plain_password)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            plain = vals.pop('password_set', None)
            if plain:
                vals['password_hash'] = generate_password_hash(plain)
        return super().create(vals_list)

    def write(self, vals):
        plain = vals.pop('password_set', None)
        if plain:
            if len(plain) < 4:
                raise UserError('Password must be at least 4 characters.')
            vals['password_hash'] = generate_password_hash(plain)
        return super().write(vals)

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Appointments — Dr. {self.name}',
            'res_model': 'health.appointment',
            'view_mode': 'calendar,list,form',
            'domain': [('doctor_id', '=', self.id)],
            'context': {'default_doctor_id': self.id},
        }
