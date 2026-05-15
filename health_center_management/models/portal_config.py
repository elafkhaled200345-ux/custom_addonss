from odoo import models, fields, api


class HealthPortalConfig(models.Model):
    _name = 'health.portal.config'
    _description = 'Portal Access Configuration'

    name = fields.Char(
        string='Configuration Name',
        required=True,
        default='Portal Configuration',
    )
    employee_portal_password = fields.Char(
        string='Employee Portal Password',
        required=True,
        default='1234',
        help='Password required to access the Employee Portal',
    )
    manager_portal_password = fields.Char(
        string='Manager Portal Password',
        required=True,
        default='1234',
        help='Password required to access the Manager (Doctor) Portal',
    )

    @api.model
    def get_config(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create({
                'name': 'Portal Configuration',
                'employee_portal_password': '1234',
                'manager_portal_password': '1234',
            })
        return config
