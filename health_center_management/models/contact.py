from odoo import models, fields, api


class HealthContactSettings(models.Model):
    _name = 'health.contact.settings'
    _description = 'Health Center Contact Settings'
    _rec_name = 'center_name'

    center_name = fields.Char(
        string='Health Center Name',
        required=True,
        default='Health Center',
    )
    phone = fields.Char(
        string='Phone',
        default='+966 XX XXX XXXX',
    )
    mobile = fields.Char(
        string='Mobile / WhatsApp',
        default='+966 XX XXX XXXX',
    )
    email = fields.Char(
        string='Email',
        default='info@healthcenter.com',
    )
    address = fields.Text(
        string='Address',
        default='Please update the health center address.',
    )
    working_hours = fields.Char(
        string='Working Hours',
        default='Sunday – Thursday: 8:00 AM – 4:00 PM',
    )
    emergency = fields.Char(
        string='Emergency Line',
        default='911',
    )

    @api.model
    def get_or_create(self):
        """Return the single settings record, creating it if needed."""
        record = self.search([], limit=1)
        if not record:
            record = self.create({
                'center_name': 'Health Center',
                'phone': '+966 XX XXX XXXX',
                'mobile': '+966 XX XXX XXXX',
                'email': 'info@healthcenter.com',
                'address': 'Please update the health center address.',
                'working_hours': 'Sunday – Thursday: 8:00 AM – 4:00 PM',
                'emergency': '911',
            })
        return record

    @api.model
    def action_open_singleton(self):
        """
        Open the Contact Information Settings form directly
        (singleton pattern — creates the record if it doesn't exist yet).
        Called by the ir.actions.server so the employee never sees
        an empty list or a 'New' button.
        """
        record = self.get_or_create()
        view_id = self.env.ref(
            'health_center_management.view_health_contact_settings_form'
        ).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact Information Settings',
            'res_model': 'health.contact.settings',
            'view_mode': 'form',
            'res_id': record.id,
            'view_id': view_id,
            'target': 'current',
            'context': {'form_view_initial_mode': 'edit'},
        }

    def action_save_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Contact information has been updated successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
