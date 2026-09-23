from odoo import models, fields, api


class HealthPrescription(models.Model):
    _name = 'health.prescription'
    _description = 'Prescription / وصفة طبية'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Prescription Number / رقم الوصفة', default='/', copy=False, readonly=True)
    medical_record_id = fields.Many2one(
        'health.medical.record', string='Medical Record / السجل الطبي',
        required=True, ondelete='cascade', tracking=True)
    patient_id = fields.Many2one(
        related='medical_record_id.patient_id', string='Patient / المريض', store=True)
    doctor_id = fields.Many2one(
        related='medical_record_id.doctor_id', string='Doctor / الطبيب', store=True)
    prescription_date = fields.Date(
        string='Prescription Date / تاريخ الوصفة', default=fields.Date.today, required=True)
    line_ids = fields.One2many(
        'health.prescription.line', 'prescription_id', string='Medicines / الأدوية')
    notes = fields.Text(string='Notes / ملاحظات')
    state = fields.Selection(
        [('draft', 'Draft / مسودة'), ('issued', 'Issued / معتمدة'), ('cancelled', 'Cancelled / ملغاة')],
        string='Status / الحالة', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.prescription') or '/'
        return super().create(vals_list)

    def action_issue(self):
        self.write({'state': 'issued'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class HealthPrescriptionLine(models.Model):
    _name = 'health.prescription.line'
    _description = 'Prescription Line / سطر وصفة'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    prescription_id = fields.Many2one(
        'health.prescription', string='Prescription / الوصفة', required=True, ondelete='cascade')
    medicine_id = fields.Many2one(
        'health.medicine', string='Medicine / الدواء', required=True, ondelete='restrict')
    quantity = fields.Float(string='Quantity / الكمية', digits=(16, 2), default=1.0)
    dosage_instructions = fields.Char(string='Dosage / تعليمات الجرعة', required=True)
    duration = fields.Char(string='Duration / المدة')
    notes = fields.Char(string='Notes / ملاحظات')
