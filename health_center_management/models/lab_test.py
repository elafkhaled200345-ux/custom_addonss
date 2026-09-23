from odoo import models, fields


class HealthLabTestType(models.Model):
    """Master list of available lab tests / قائمة الفحوصات المتاحة."""
    _name = 'health.lab.test.type'
    _description = 'Lab Test Type / نوع فحص المختبر'
    _rec_name = 'name'
    _order = 'category, name'

    name = fields.Char(string='Test Name / اسم الفحص', required=True)
    name_ar = fields.Char(string='Arabic Name / الاسم بالعربي')
    code = fields.Char(string='Code / الرمز')
    category = fields.Selection(
        selection=[
            ('blood', 'Blood / دم'),
            ('urine', 'Urine / بول'),
            ('xray', 'X-Ray / أشعة'),
            ('ct', 'CT Scan / مقطعية'),
            ('ultrasound', 'Ultrasound / سونار'),
            ('audiology', 'Audiology / سمع'),
            ('other', 'Other / أخرى'),
        ],
        string='Category / التصنيف', required=True, default='blood',
    )
    active = fields.Boolean(string='Active', default=True)


class HealthLabRequestLine(models.Model):
    """A single test line within a lab request / سطر فحص في طلب المختبر."""
    _name = 'health.lab.request.line'
    _description = 'Lab Request Line / سطر طلب مختبر'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Seq', default=10)
    request_id = fields.Many2one(
        'health.lab.request', string='Request', required=True, ondelete='cascade')
    test_type_id = fields.Many2one(
        'health.lab.test.type', string='Test / الفحص', required=True, ondelete='restrict')
    test_name = fields.Char(
        related='test_type_id.name', string='Test Name', store=True)
    test_category = fields.Selection(
        related='test_type_id.category', string='Category', store=True)
    result = fields.Text(string='Result / النتيجة')
    normal_range = fields.Char(string='Normal Range / المعدل الطبيعي')
    unit = fields.Char(string='Unit / الوحدة')
    state = fields.Selection(
        selection=[
            ('pending', 'Pending / معلق'),
            ('done', 'Done / منتهى'),
        ],
        string='Status', default='pending',
    )
    notes = fields.Char(string='Notes / ملاحظات')
