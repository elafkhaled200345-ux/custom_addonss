import ast
from odoo import models, fields, api


class HealthPortalSection(models.Model):
    _name = 'health.portal.section'
    _description = 'Portal Section Menu'
    _rec_name = 'name'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Section Name', required=True)
    description = fields.Char(string='Description')
    icon = fields.Char(string='Icon', default='fa-folder')
    portal_type = fields.Selection(
        selection=[
            ('employee', 'Employee Portal'),
            ('doctor', 'Doctor Portal'),
        ],
        string='Portal Type',
        required=True,
    )
    action_xml_id = fields.Char(
        string='Action Reference',
        help='Full XML ID of the action to open.',
    )

    def action_open_section(self):
        self.ensure_one()
        if not self.action_xml_id:
            return {}

        action = self.env.ref(self.action_xml_id)

        # Server actions: run them directly — they return the final action dict
        if action._name == 'ir.actions.server':
            result = action.run()
            return result or {}

        # Window / client actions: read and return
        result = action.read()[0]

        # For doctor portal sections, apply clinic filter automatically
        if self.portal_type == 'doctor':
            clinic_id_str = self.env['ir.config_parameter'].sudo().get_param(
                'health_center.active_clinic_id'
            )
            if clinic_id_str:
                try:
                    clinic_id = int(clinic_id_str)
                    clinic_filter = [('clinic_id', '=', clinic_id)]
                    existing = result.get('domain') or '[]'
                    if isinstance(existing, str):
                        existing = ast.literal_eval(existing)
                    result['domain'] = clinic_filter + existing
                except (ValueError, TypeError):
                    pass

        return result
