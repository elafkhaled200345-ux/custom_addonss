from odoo import models, fields, api


class HealthBooking(models.Model):
    _name = 'health.booking'
    _description = 'Booking'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(
        string='Booking Number',
        copy=False,
        default='/',
    )
    patient_id = fields.Many2one(
        'health.patient',
        string='Patient',
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='active',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.booking') or '/'
        return super().create(vals_list)

    def action_save_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Booking data has been saved successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
