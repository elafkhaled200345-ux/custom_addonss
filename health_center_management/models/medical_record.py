from odoo import models, fields, api


class HealthMedicalRecord(models.Model):
    _name = 'health.medical.record'
    _description = 'Medical Record'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(
        string='Medical Record Number',
        copy=False,
        default='/',
    )
    patient_id = fields.Many2one(
        'health.patient',
        string='Patient',
        required=True,
        ondelete='restrict',
    )
    patient_name = fields.Char(
        related='patient_id.name',
        string='Patient Name',
        store=True,
    )
    booking_id = fields.Many2one(
        'health.booking',
        string='Booking',
        ondelete='restrict',
    )
    booking_number = fields.Char(
        related='booking_id.name',
        string='Booking Number',
        store=True,
    )
    create_date_manual = fields.Date(
        string='Creation Date',
        default=fields.Date.today,
    )
    report = fields.Text(
        string='Medical Report',
    )
    examination_ids = fields.One2many(
        'health.examination',
        'medical_record_id',
        string='Examinations',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.medical.record') or '/'
        return super().create(vals_list)

    def action_save_confirm(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Medical record has been saved successfully.',
                'type': 'success',
                'sticky': False,
            }
        }
