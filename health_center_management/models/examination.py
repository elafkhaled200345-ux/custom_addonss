from odoo import models, fields, api


class HealthExamination(models.Model):
    _name = 'health.examination'
    _description = 'Medical Examination'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(
        string='Examination Number',
        copy=False,
        default='/',
    )
    medical_record_id = fields.Many2one(
        'health.medical.record',
        string='Medical Record',
        required=True,
        ondelete='restrict',
    )
    medical_record_number = fields.Char(
        related='medical_record_id.name',
        string='Medical Record Number',
        store=True,
    )
    medical_record_report = fields.Text(
        related='medical_record_id.report',
        string='Medical Report',
    )
    patient_id = fields.Many2one(
        related='medical_record_id.patient_id',
        string='Patient',
        store=True,
    )
    patient_name = fields.Char(
        related='medical_record_id.patient_name',
        string='Patient Name',
        store=True,
    )
    booking_id = fields.Many2one(
        related='medical_record_id.booking_id',
        string='Booking',
        store=True,
    )
    booking_number = fields.Char(
        related='medical_record_id.booking_number',
        string='Booking Number',
        store=True,
    )
    create_date_manual = fields.Date(
        string='Examination Date',
        default=fields.Date.today,
    )
    result = fields.Text(string='Examination Result')
    prescription = fields.Text(string='Drug Prescription')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.examination') or '/'
        return super().create(vals_list)

    def action_save_confirm(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✔ Saved Successfully',
                'message': 'Examination data has been saved successfully.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_print_examination(self):
        self.ensure_one()
        return self.env.ref('health_center_management.report_health_examination').report_action(self)

    def action_download_report(self):
        self.ensure_one()
        return self.env.ref('health_center_management.report_health_examination').report_action(self)
