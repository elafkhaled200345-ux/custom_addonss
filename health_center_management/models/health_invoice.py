from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class HealthInvoice(models.Model):
    _name = 'health.invoice'
    _description = 'Health Invoice / فاتورة صحية'
    _rec_name = 'name'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Invoice Number / رقم الفاتورة', readonly=True, copy=False, default='New')
    booking_id = fields.Many2one(
        'health.booking', string='Booking / الحجز', ondelete='restrict', tracking=True)
    patient_id = fields.Many2one(
        'health.patient', string='Patient / المريض', required=True,
        ondelete='restrict', tracking=True)
    patient_name = fields.Char(related='patient_id.name', store=True)
    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة', required=True, ondelete='restrict')
    appointment_id = fields.Many2one(
        'health.appointment', string='Appointment / الموعد', ondelete='set null')
    examination_id = fields.Many2one(
        'health.examination', string='Examination / الفحص', ondelete='set null')
    invoice_date = fields.Date(
        string='Invoice Date / تاريخ الفاتورة', default=fields.Date.today,
        required=True, tracking=True)

    currency_id = fields.Many2one(
        'res.currency', string='Currency / العملة', required=True,
        default=lambda self: self.env.company.currency_id)
    consultation_fee = fields.Float(string='Consultation Fee / رسوم الكشف', digits=(16, 2), default=0.0)
    examination_fee = fields.Float(
        string='Examination Fee / رسوم الفحص', digits=(16, 2),
        compute='_compute_examination_fee', store=True)
    discount = fields.Float(string='Discount % / الخصم', digits=(5, 2), default=0.0)
    tax = fields.Float(string='Tax % / الضريبة', digits=(5, 2), default=0.0)
    tax_amount = fields.Float(string='Tax Amount / قيمة الضريبة', compute='_compute_total', store=True, digits=(16, 2))
    total_amount = fields.Float(string='Total / الإجمالي', compute='_compute_total', store=True, digits=(16, 2))

    payment_method = fields.Selection(
        selection=[
            ('cash', 'Cash / نقد'), ('bank_app', 'Bank Transfer / تحويل بنكي'),
            ('insurance', 'Insurance / تأمين صحي'), ('credit', 'Credit Card / بطاقة ائتمان'),
        ],
        string='Payment Method / طريقة الدفع', tracking=True)
    transaction_number = fields.Char(
        string='Transaction / Reference Number',
        help='Bank transfer or insurance claim reference number')
    amount_paid = fields.Float(string='Amount Paid / المبلغ المدفوع', digits=(16, 2), default=0.0, tracking=True)
    remaining_balance = fields.Float(
        string='Remaining Balance / المبلغ المتبقي', compute='_compute_remaining_balance',
        store=True, digits=(16, 2))
    payment_date = fields.Date(string='Payment Date / تاريخ الدفع', tracking=True)
    receipt_number = fields.Char(string='Receipt Number / رقم الإيصال', copy=False, readonly=True)
    insurance_company = fields.Char(
        string='Insurance Company / شركة التأمين', related='patient_id.insurance_company', store=False)
    insurance_number = fields.Char(
        string='Insurance Policy Number / رقم التأمين', related='patient_id.insurance_number', store=False)
    invoice_status = fields.Selection(
        selection=[
            ('unpaid', 'Unpaid / غير مدفوع'), ('partial', 'Partially Paid / مدفوع جزئياً'),
            ('paid', 'Paid / مدفوع'), ('insurance_pending', 'Insurance Pending / تأمين قيد المعالجة'),
            ('cancelled', 'Cancelled / ملغى'),
        ],
        string='Payment Status / حالة الدفع', default='unpaid', required=True, tracking=True)
    notes = fields.Text(string='Notes / ملاحظات')

    @api.onchange('booking_id')
    def _onchange_booking_id(self):
        if self.booking_id:
            self.patient_id = self.booking_id.patient_id
            self.clinic_id = self.booking_id.clinic_id
            self.appointment_id = self.booking_id.appointment_id
            if self.booking_id.appointment_id:
                self.consultation_fee = self.booking_id.appointment_id.examination_fees

    @api.depends('examination_id.examination_fees')
    def _compute_examination_fee(self):
        for rec in self:
            rec.examination_fee = rec.examination_id.examination_fees if rec.examination_id else 0.0

    @api.depends('consultation_fee', 'examination_fee', 'discount', 'tax')
    def _compute_total(self):
        for rec in self:
            subtotal = rec.consultation_fee + rec.examination_fee
            after_discount = subtotal * (1 - rec.discount / 100.0)
            rec.tax_amount = after_discount * (rec.tax / 100.0)
            rec.total_amount = after_discount + rec.tax_amount

    @api.depends('total_amount', 'amount_paid')
    def _compute_remaining_balance(self):
        for rec in self:
            rec.remaining_balance = max(rec.total_amount - rec.amount_paid, 0.0)

    @api.constrains('booking_id', 'patient_id', 'clinic_id', 'appointment_id')
    def _check_booking_consistency(self):
        for rec in self:
            if not rec.booking_id:
                continue
            if rec.patient_id != rec.booking_id.patient_id or rec.clinic_id != rec.booking_id.clinic_id:
                raise ValidationError('Invoice patient/clinic must match the selected booking.')
            if rec.appointment_id and rec.appointment_id != rec.booking_id.appointment_id:
                raise ValidationError('Invoice appointment must match the selected booking.')

    @api.constrains('discount', 'tax', 'amount_paid')
    def _check_amounts(self):
        for rec in self:
            if not 0 <= rec.discount <= 100:
                raise ValidationError('Discount must be between 0 and 100%.')
            if rec.tax < 0:
                raise ValidationError('Tax cannot be negative.')
            if rec.amount_paid < 0:
                raise ValidationError('Amount paid cannot be negative.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            booking = self.env['health.booking'].browse(vals.get('booking_id')).exists()
            if booking:
                vals.setdefault('patient_id', booking.patient_id.id)
                vals.setdefault('clinic_id', booking.clinic_id.id)
                vals.setdefault('appointment_id', booking.appointment_id.id or False)
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('health.invoice') or 'New'
        return super().create(vals_list)

    @api.constrains('payment_method', 'transaction_number', 'invoice_status')
    def _check_payment_fields(self):
        for rec in self:
            if rec.invoice_status == 'paid':
                if rec.payment_method in ('bank_app', 'insurance') and not rec.transaction_number:
                    raise UserError('This payment method requires a transaction/reference number.')

    def action_mark_paid(self):
        for rec in self:
            if not rec.payment_method:
                raise UserError('Please select a payment method before marking as paid.\nيرجى اختيار طريقة الدفع أولاً.')
            vals = {
                'invoice_status': 'paid',
                'amount_paid': rec.total_amount,
                'payment_date': fields.Date.today(),
            }
            if not rec.receipt_number:
                vals['receipt_number'] = self.env['ir.sequence'].next_by_code('health.invoice.receipt') or '/'
            rec.write(vals)
            rec.message_post(body=f'✔ Invoice {rec.name} marked as PAID.', message_type='notification')

    def action_cancel(self):
        self.write({'invoice_status': 'cancelled'})

    def action_print_invoice(self):
        self.ensure_one()
        return self.env.ref('health_center_management.report_health_invoice').report_action(self)
