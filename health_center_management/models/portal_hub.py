# -*- coding: utf-8 -*-
from odoo import models, fields


class HealthEmployeeHub(models.TransientModel):
    """Landing page after employee portal login."""
    _name = 'health.employee.hub'
    _description = 'Employee Portal Hub / بوابة الموظف'

    def action_patients(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patients / المرضى',
            'res_model': 'health.patient',
            'view_mode': 'list,form',
        }

    def action_bookings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bookings / الحجوزات',
            'res_model': 'health.booking',
            'view_mode': 'list,form',
        }

    def action_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments / المواعيد',
            'res_model': 'health.appointment',
            'view_mode': 'calendar,list,form',
        }

    def action_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices / الفواتير',
            'res_model': 'health.invoice',
            'view_mode': 'list,form',
        }

    def action_pharmacy(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pharmacy / الصيدلية',
            'res_model': 'health.pharmacy.dispense',
            'view_mode': 'list,form',
        }

    def action_lab_requests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lab Requests / طلبات المختبر',
            'res_model': 'health.lab.request',
            'view_mode': 'list,form',
        }

    def action_medical_records(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Records / السجلات الطبية',
            'res_model': 'health.medical.record',
            'view_mode': 'list,form',
        }


class HealthDoctorHub(models.TransientModel):
    """Landing page after doctor portal login."""
    _name = 'health.doctor.hub'
    _description = 'Doctor Portal Hub / بوابة الطبيب'

    doctor_id = fields.Many2one(
        'health.doctor', string='Doctor / الطبيب', readonly=True)
    clinic_id = fields.Many2one(
        'health.clinic', string='Clinic / العيادة', readonly=True)

    def action_medical_records(self):
        self.ensure_one()
        domain = [('doctor_id', '=', self.doctor_id.id)] if self.doctor_id else []
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Records / السجلات الطبية',
            'res_model': 'health.medical.record',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'default_doctor_id': self.doctor_id.id,
                        'default_clinic_id': self.clinic_id.id} if self.doctor_id else {},
        }

    def action_examinations(self):
        self.ensure_one()
        domain = [('doctor_id', '=', self.doctor_id.id)] if self.doctor_id else []
        return {
            'type': 'ir.actions.act_window',
            'name': 'Examinations / الفحوصات',
            'res_model': 'health.examination',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'default_doctor_id': self.doctor_id.id} if self.doctor_id else {},
        }

    def action_lab_requests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lab Requests / طلبات المختبر',
            'res_model': 'health.lab.request',
            'view_mode': 'list,form',
        }

    def action_appointments(self):
        self.ensure_one()
        domain = [('doctor_id', '=', self.doctor_id.id)] if self.doctor_id else []
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Appointments / مواعيدي',
            'res_model': 'health.appointment',
            'view_mode': 'calendar,list,form',
            'domain': domain,
        }

    def action_patients(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patients / المرضى',
            'res_model': 'health.patient',
            'view_mode': 'list,form',
        }
