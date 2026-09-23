from odoo import models, fields, api


class HealthExamination(models.Model):
    _name = 'health.examination'
    _description = 'Medical Examination / فحص طبي'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Examination Number / رقم الفحص',
        copy=False, default='/', readonly=True,
    )
    medical_record_id = fields.Many2one(
        'health.medical.record', string='Medical Record / السجل الطبي',
        required=True, ondelete='cascade', tracking=True,
    )
    clinic_id = fields.Many2one(
        related='medical_record_id.clinic_id', string='Clinic / العيادة', store=True)
    patient_id = fields.Many2one(
        related='medical_record_id.patient_id', string='Patient / المريض', store=True)
    patient_name = fields.Char(
        related='medical_record_id.patient_name', string='Patient Name', store=True)
    booking_id = fields.Many2one(
        related='medical_record_id.booking_id', string='Booking', store=True)
    booking_number = fields.Char(
        related='medical_record_id.booking_number', string='Booking Number', store=True)
    doctor_id = fields.Many2one(
        related='medical_record_id.doctor_id', string='Doctor', store=True)

    examination_name = fields.Char(
        string='Examination Name / اسم الفحص', required=True)
    examination_type = fields.Selection(
        selection=[
            ('clinical', 'Clinical / سريري'),
            ('laboratory', 'Laboratory / مختبر'),
            ('radiology', 'Radiology / أشعة'),
            ('ultrasound', 'Ultrasound / سونار'),
            ('other', 'Other / أخرى'),
        ],
        string='Type / النوع', default='clinical',
    )
    performed_by = fields.Many2one(
        'health.employee', string='Performed By / أجرى الفحص',
        ondelete='set null', default=lambda self: self._default_employee(), tracking=True)
    examination_fees = fields.Float(
        string='Fees / رسوم الفحص', digits=(16, 2), default=0.0, tracking=True)
    create_date_manual = fields.Date(
        string='Examination Date / تاريخ الفحص', default=fields.Date.today)
    result = fields.Text(string='Examination Result / نتيجة الفحص')
    prescription = fields.Text(string='Drug Prescription / الوصفة الطبية')
    state = fields.Selection(
        selection=[
            ('pending', 'Pending / معلق'),
            ('done', 'Done / منتهى'),
        ],
        string='Status', default='pending', tracking=True,
    )

    @api.model
    def _default_employee(self):
        employee = self.env['health.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee.id or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('health.examination') or '/'
                )
        return super().create(vals_list)

    def action_mark_done(self):
        self.write({'state': 'done'})

    def action_print_examination(self):
        self.ensure_one()
        return self.env.ref(
            'health_center_management.report_health_examination'
        ).report_action(self)
