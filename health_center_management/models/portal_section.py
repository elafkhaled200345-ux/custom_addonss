from odoo import models, fields


class HealthPortalSection(models.Model):
    _name = 'health.portal.section'
    _description = 'Portal Section / قسم بوابة'
    _rec_name = 'name'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Section Name / اسم القسم', required=True)
    portal_type = fields.Selection(
        selection=[
            ('employee', 'Employee / موظف'),
            ('doctor', 'Doctor / طبيب'),
        ],
        string='Portal Type / نوع البوابة', required=True,
    )
    description = fields.Char(string='Description / الوصف')
    icon = fields.Char(string='Icon', help='FontAwesome icon class e.g. fa-user')
    active = fields.Boolean(string='Active', default=True)
