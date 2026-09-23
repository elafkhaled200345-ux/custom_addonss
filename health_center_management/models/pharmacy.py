from odoo import models, fields, api
from odoo.exceptions import UserError


class HealthMedicine(models.Model):
    """Medicine / دواء — master catalogue."""
    _name = 'health.medicine'
    _description = 'Medicine / دواء'
    _rec_name = 'name'
    _order = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string='Medicine Name / اسم الدواء', required=True, tracking=True)
    generic_name = fields.Char(string='Generic Name / الاسم العلمي')
    category = fields.Selection(
        selection=[
            ('antibiotic', 'Antibiotic / مضاد حيوي'),
            ('analgesic', 'Analgesic / مسكن ألم'),
            ('antiviral', 'Antiviral / مضاد فيروسي'),
            ('antifungal', 'Antifungal / مضاد فطري'),
            ('antihistamine', 'Antihistamine / مضاد هيستامين'),
            ('vitamin', 'Vitamin / فيتامين'),
            ('chronic', 'Chronic Disease / أمراض مزمنة'),
            ('other', 'Other / أخرى'),
        ],
        string='Category / التصنيف', default='other',
    )
    dosage_form = fields.Selection(
        selection=[
            ('tablet', 'Tablet / قرص'),
            ('capsule', 'Capsule / كبسولة'),
            ('syrup', 'Syrup / شراب'),
            ('injection', 'Injection / حقنة'),
            ('cream', 'Cream / كريم'),
            ('drops', 'Drops / قطرة'),
            ('inhaler', 'Inhaler / بخاخ'),
            ('other', 'Other / أخرى'),
        ],
        string='Form / الشكل', default='tablet',
    )
    strength = fields.Char(string='Strength / التركيز', help='e.g. 500mg, 250mg/5ml')
    unit_price = fields.Float(string='Unit Price / سعر الوحدة', digits=(16, 2))
    qty_available = fields.Float(
        string='In Stock / المخزون', digits=(16, 2), default=0.0, tracking=True)
    reorder_level = fields.Float(
        string='Reorder Level / حد إعادة الطلب', digits=(16, 2), default=10.0)
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes / ملاحظات')

    low_stock = fields.Boolean(
        string='Low Stock', compute='_compute_low_stock', store=False)

    @api.depends('qty_available', 'reorder_level')
    def _compute_low_stock(self):
        for rec in self:
            rec.low_stock = rec.qty_available <= rec.reorder_level


class HealthPharmacyDispense(models.Model):
    """Pharmacy Dispense Order / صرف دواء."""
    _name = 'health.pharmacy.dispense'
    _description = 'Pharmacy Dispense / صرف صيدلية'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Dispense Number / رقم الصرف',
        copy=False, default='/', readonly=True,
    )
    patient_id = fields.Many2one(
        'health.patient', string='Patient / المريض',
        required=True, ondelete='restrict', tracking=True,
    )
    doctor_id = fields.Many2one(
        'health.doctor', string='Prescribing Doctor / الطبيب',
        ondelete='set null', tracking=True,
    )
    medical_record_id = fields.Many2one(
        'health.medical.record', string='Medical Record / السجل الطبي',
        ondelete='set null',
    )
    dispensed_by = fields.Many2one(
        'health.employee', string='Dispensed By / صرف بواسطة',
        ondelete='set null', tracking=True)
    dispense_date = fields.Date(
        string='Date / التاريخ', default=fields.Date.today, required=True)
    line_ids = fields.One2many(
        'health.pharmacy.dispense.line', 'dispense_id',
        string='Medicines / الأدوية',
    )
    total_amount = fields.Float(
        string='Total / الإجمالي',
        compute='_compute_total', store=True, digits=(16, 2),
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft / مسودة'),
            ('dispensed', 'Dispensed / صُرف'),
            ('cancelled', 'Cancelled / ملغى'),
        ],
        string='Status / الحالة', default='draft', tracking=True,
    )
    notes = fields.Text(string='Notes / ملاحظات')

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('health.pharmacy.dispense') or '/'
                )
        return super().create(vals_list)

    def action_dispense(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('Only draft orders can be dispensed.')
            for line in rec.line_ids:
                if line.medicine_id.qty_available < line.quantity:
                    raise UserError(
                        f'Insufficient stock for: {line.medicine_id.name}\n'
                        f'المخزون غير كافٍ لـ: {line.medicine_id.name}'
                    )
                line.medicine_id.qty_available -= line.quantity
            employee = self.env['health.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            rec.write({'state': 'dispensed', 'dispensed_by': employee.id or False})
            rec.message_post(
                body=f'✔ Medicines dispensed. Total: {rec.total_amount}',
                message_type='notification',
            )


class HealthPharmacyDispenseLine(models.Model):
    _name = 'health.pharmacy.dispense.line'
    _description = 'Dispense Line / سطر صرف'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Seq', default=10)
    dispense_id = fields.Many2one(
        'health.pharmacy.dispense', string='Dispense',
        required=True, ondelete='cascade',
    )
    medicine_id = fields.Many2one(
        'health.medicine', string='Medicine / الدواء',
        required=True, ondelete='restrict',
    )
    dosage_form = fields.Selection(
        related='medicine_id.dosage_form', string='Form', store=False)
    quantity = fields.Float(string='Qty / الكمية', digits=(16, 2), default=1.0)
    unit_price = fields.Float(
        string='Price / السعر', digits=(16, 2),
        related='medicine_id.unit_price', store=True,
    )
    subtotal = fields.Float(
        string='Subtotal / المجموع', digits=(16, 2),
        compute='_compute_subtotal', store=True,
    )
    batch_number = fields.Char(string='Batch Number / رقم التشغيلة')
    expiry_date = fields.Date(string='Expiry Date / تاريخ الانتهاء')
    dosage_instructions = fields.Char(
        string='Instructions / التعليمات',
        help='e.g. 1 tablet 3 times daily after meals',
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price
