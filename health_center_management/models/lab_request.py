from odoo import models, fields, api


class HealthLabRequest(models.Model):
    _name = 'health.lab.request'
    _description = 'Lab Test Request / طلب فحص مختبر'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Request Number / رقم الطلب',
        copy=False, default='/', readonly=True,
    )
    patient_id = fields.Many2one(
        'health.patient', string='Patient / المريض',
        required=True, ondelete='restrict', tracking=True,
    )
    patient_name = fields.Char(related='patient_id.name', store=True, string='Patient Name')
    age = fields.Integer(related='patient_id.age', store=True, string='Age / العمر')
    doctor_id = fields.Many2one(
        'health.doctor', string='Doctor / الطبيب',
        required=True, ondelete='restrict', tracking=True,
    )
    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة', ondelete='restrict')
    medical_record_id = fields.Many2one(
        'health.medical.record', string='Medical Record / السجل الطبي',
        ondelete='cascade',
    )
    request_date = fields.Date(
        string='Date / التاريخ', default=fields.Date.today, required=True)
    diagnosis = fields.Char(string='Diagnosis / التشخيص')
    priority = fields.Selection(
        [('normal', 'Normal / عادي'), ('urgent', 'Urgent / عاجل'), ('stat', 'STAT / فوري')],
        string='Priority / الأولوية', default='normal', required=True, tracking=True)
    collected_date = fields.Datetime(string='Collected Date / تاريخ جمع العينة', tracking=True)
    result_date = fields.Datetime(string='Result Date / تاريخ النتيجة', tracking=True)
    approved_by = fields.Many2one(
        'health.employee', string='Approved By / اعتمد بواسطة',
        ondelete='set null', tracking=True)

    # ── Dynamic test lines (replaces Boolean fields) ──────────────────
    line_ids = fields.One2many(
        'health.lab.request.line', 'request_id',
        string='Tests / الفحوصات',
    )
    line_count = fields.Integer(
        string='Tests Count', compute='_compute_line_count')

    # ── Clinical Notes ────────────────────────────────────────────────
    case_of = fields.Char(string='A Case Of / حالة')
    on_medication = fields.Char(string='On Medication / دواء')
    chief_complaint = fields.Char(string='Chief Complaint / الشكوى')
    for_purpose = fields.Char(string='For (Purpose) / الغرض')
    additional_notes = fields.Text(string='Additional Notes / ملاحظات إضافية')

    state = fields.Selection(
        selection=[
            ('draft', 'Draft / مسودة'),
            ('sent', 'Sent to Lab / أُرسل'),
            ('partial', 'Partial Results / نتائج جزئية'),
            ('done', 'Complete / مكتمل'),
            ('cancelled', 'Cancelled / ملغى'),
        ],
        string='Status / الحالة', default='draft', tracking=True,
    )

    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('health.lab.request') or '/'
                )
        return super().create(vals_list)

    def action_send_to_lab(self):
        self.write({'state': 'sent'})
        self.message_post(body='Lab request sent to laboratory.', message_type='notification')

    def action_mark_done(self):
        employee = self.env['health.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        vals = {'state': 'done', 'result_date': fields.Datetime.now()}
        if employee:
            vals['approved_by'] = employee.id
        self.write(vals)

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_print_lab_request(self):
        self.ensure_one()
        return self.env.ref(
            'health_center_management.report_health_lab_request'
        ).report_action(self)
