# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HealthDashboard(models.TransientModel):
    """Live statistics dashboard — values computed fresh on every open."""
    _name = 'health.dashboard'
    _description = 'Health Center Dashboard / لوحة المتابعة'

    # ── Today ──────────────────────────────────────────────────────────
    today_appointments = fields.Integer(string="Appointments Today / مواعيد اليوم")
    available_appointments_today = fields.Integer(string="Available Slots / مواعيد متاحة")
    today_patients = fields.Integer(string="Patients Today / مرضى اليوم")
    today_revenue = fields.Float(string="Today's Revenue / إيرادات اليوم", digits=(16, 2))

    # ── Overall ────────────────────────────────────────────────────────
    total_patients = fields.Integer(string='Total Patients / إجمالي المرضى')
    total_bookings = fields.Integer(string='Total Bookings / إجمالي الحجوزات')
    total_revenue = fields.Float(string='Total Revenue / إجمالي الإيرادات', digits=(16, 2))
    pending_invoices = fields.Integer(string='Unpaid Invoices / فواتير غير مدفوعة')
    active_clinics_today = fields.Integer(string='Active Clinics Today / عيادات نشطة')
    low_stock_medicines = fields.Integer(string='Low Stock Medicines / أدوية منخفضة')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        today = fields.Date.today()
        Appt = self.env['health.appointment']
        Patient = self.env['health.patient']
        Booking = self.env['health.booking']
        Invoice = self.env['health.invoice']
        Medicine = self.env['health.medicine']
        Clinic = self.env['health.clinic']

        res['today_appointments'] = Appt.search_count([
            ('appointment_date', '=', today)])
        res['available_appointments_today'] = Appt.search_count([
            ('appointment_date', '=', today),
            ('is_available', '=', True)])
        today_bookings = Booking.search([
            ('booking_date', '=', today),
            ('state', 'in', ['confirmed', 'checked_in', 'visited'])])
        res['today_patients'] = len(set(today_bookings.mapped('patient_id').ids))
        today_paid = Invoice.search([
            ('invoice_date', '=', today),
            ('invoice_status', '=', 'paid')])
        res['today_revenue'] = sum(today_paid.mapped('total_amount'))
        res['total_patients'] = Patient.search_count([])
        res['total_bookings'] = Booking.search_count([])
        all_paid = Invoice.search([('invoice_status', '=', 'paid')])
        res['total_revenue'] = sum(all_paid.mapped('total_amount'))
        res['pending_invoices'] = Invoice.search_count([
            ('invoice_status', '=', 'unpaid')])
        res['active_clinics_today'] = Clinic.search_count([
            ('appointment_ids.appointment_date', '=', today)])
        medicines = Medicine.search([])
        res['low_stock_medicines'] = sum(
            1 for m in medicines if m.qty_available <= m.reorder_level)
        return res

    def action_refresh(self):
        """Reload current record with fresh computed values (avoids stale TransientModel records)."""
        self.ensure_one()
        vals = self.default_get(list(self._fields))
        self.write({k: v for k, v in vals.items() if k in self._fields})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'health.dashboard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'inline',
            'context': {'create': False},
        }

    # ── Quick navigation shortcuts ─────────────────────────────────────
    def action_open_patients(self):
        return {'type': 'ir.actions.act_window', 'name': 'Patients / المرضى',
                'res_model': 'health.patient', 'view_mode': 'list,form'}

    def action_open_invoices(self):
        return {'type': 'ir.actions.act_window', 'name': 'Unpaid Invoices / فواتير غير مدفوعة',
                'res_model': 'health.invoice', 'view_mode': 'list,form',
                'domain': [('invoice_status', '=', 'unpaid')]}

    def action_open_appointments(self):
        return {'type': 'ir.actions.act_window', 'name': 'Appointments Today / مواعيد اليوم',
                'res_model': 'health.appointment', 'view_mode': 'calendar,list,form',
                'domain': [('appointment_date', '=', fields.Date.today())]}
