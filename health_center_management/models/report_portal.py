# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class HealthReportPortalLogin(models.TransientModel):
    _name = 'health.report.portal.login'
    _description = 'Reports Portal Login / دخول بوابة التقارير'

    password = fields.Char(string='Password / كلمة المرور', required=True)

    def action_verify(self):
        self.ensure_one()
        config = self.env['health.portal.config'].get_config()
        if config.reports_portal_password_hash:
            ok = config.verify_reports_password(self.password)
        else:
            ok = config.verify_employee_password(self.password)
        if not ok:
            raise UserError(
                'كلمة المرور غير صحيحة. تم رفض الدخول.\nIncorrect password. Access denied.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports Hub / مركز التقارير',
            'res_model': 'health.report.hub',
            'view_mode': 'form',
            'target': 'current',
            'context': {'create': False, 'delete': False},
        }


class HealthReportHub(models.TransientModel):
    _name = 'health.report.hub'
    _description = 'Reports Hub / مركز التقارير'

    report_type = fields.Selection(
        selection=[
            ('patient', 'Patients / المرضى'),
            ('booking', 'Bookings / الحجوزات'),
            ('medical_record', 'Medical Records / السجلات الطبية'),
            ('examination', 'Examinations / الفحوصات'),
            ('lab_request', 'Lab Requests / طلبات المختبر'),
            ('invoice', 'Invoices / الفواتير'),
            ('pharmacy', 'Pharmacy Dispenses / صرف الصيدلية'),
        ],
        string='Report Type / نوع التقرير', required=True,
    )

    # Map: report_type → (model, list_name, report_xml_id or False)
    _REPORT_MAP = {
        'patient':        ('health.patient',           'Patients / المرضى',                  False),
        'booking':        ('health.booking',            'Bookings / الحجوزات',                'health_center_management.report_health_booking'),
        'medical_record': ('health.medical.record',    'Medical Records / السجلات الطبية',   'health_center_management.report_health_medical_record'),
        'examination':    ('health.examination',        'Examinations / الفحوصات',            'health_center_management.report_health_examination'),
        'lab_request':    ('health.lab.request',        'Lab Requests / طلبات المختبر',       'health_center_management.report_health_lab_request'),
        'invoice':        ('health.invoice',            'Invoices / الفواتير',                'health_center_management.report_health_invoice'),
        'pharmacy':       ('health.pharmacy.dispense',  'Pharmacy Dispenses / صرف الصيدلية', False),
    }

    def _get_map(self):
        self.ensure_one()
        if not self.report_type:
            raise UserError('يرجى اختيار نوع التقرير.\nPlease select a report type.')
        return self._REPORT_MAP[self.report_type]

    def action_open_list(self):
        """Open the records list view."""
        self.ensure_one()
        model, title, _ = self._get_map()
        return {
            'type': 'ir.actions.act_window',
            'name': title,
            'res_model': model,
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_print_pdf(self):
        """Print a PDF report for all records of the selected type."""
        self.ensure_one()
        model, title, report_xml_id = self._get_map()
        if not report_xml_id:
            raise UserError(
                f'لا يوجد تقرير PDF مرتبط بـ "{title}".\n'
                f'No PDF report available for "{title}".')
        records = self.env[model].search([])
        if not records:
            raise UserError(
                'لا توجد سجلات لطباعتها.\nNo records found to print.')
        report_action = self.env.ref(report_xml_id)
        return report_action.report_action(records)
