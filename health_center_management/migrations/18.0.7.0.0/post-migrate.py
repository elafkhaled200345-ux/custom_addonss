# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def _table_exists(cr, table):
    cr.execute("SELECT to_regclass(%s)", (table,))
    row = cr.fetchone()
    return bool(row and row[0])


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Booking = env['health.booking'].with_context(mail_create_nolog=True, tracking_disable=True)

    if _table_exists(cr, 'hcm_mig_patient_visit_18_0_7'):
        cr.execute("""
            SELECT patient_id, clinic_id, appointment_id, booking_id, booking_type,
                   followup_booking_number, medical_record_id, invoice_id, state
            FROM hcm_mig_patient_visit_18_0_7 ORDER BY patient_id
        """)
        state_map = {
            'draft': 'draft', 'confirmed': 'confirmed', 'visited': 'visited',
            'cancelled': 'cancelled', 'active': 'confirmed',
        }
        migrated = 0
        for row in cr.fetchall():
            (patient_id, clinic_id, appointment_id, booking_id, visit_type,
             previous_number, medical_record_id, invoice_id, old_state) = row
            if not clinic_id:
                continue

            booking = Booking.browse(booking_id).exists() if booking_id else Booking.browse()
            appointment = env['health.appointment'].browse(appointment_id).exists() if appointment_id else False
            vals = {
                'patient_id': patient_id,
                'clinic_id': clinic_id,
                'appointment_id': appointment_id or False,
                'doctor_id': appointment.doctor_id.id if appointment else False,
                'visit_type': visit_type if visit_type in ('new', 'followup') else 'new',
                'state': state_map.get(old_state, 'draft'),
            }
            if previous_number:
                previous = Booking.search([('name', '=', previous_number), ('patient_id', '=', patient_id)], limit=1)
                vals['previous_booking_id'] = previous.id or False

            if booking:
                booking.write(vals)
            else:
                booking = Booking.create(vals)

            if medical_record_id:
                env['health.medical.record'].browse(medical_record_id).exists().write({'booking_id': booking.id})
            if invoice_id:
                invoice = env['health.invoice'].browse(invoice_id).exists()
                if invoice:
                    invoice.write({
                        'booking_id': booking.id,
                        'patient_id': patient_id,
                        'clinic_id': clinic_id,
                        'appointment_id': appointment_id or False,
                    })
            migrated += 1

        _logger.info('Normalized %d legacy patient visit rows into bookings.', migrated)
        cr.execute('DROP TABLE hcm_mig_patient_visit_18_0_7')

    # Any legacy invoice not linked through the patient snapshot gets a minimal
    # booking so the new central visit relationship is still available.
    for invoice in env['health.invoice'].search([('booking_id', '=', False)]):
        clinic = invoice.clinic_id or invoice.appointment_id.clinic_id
        if not invoice.patient_id or not clinic:
            continue
        booking = Booking.create({
            'patient_id': invoice.patient_id.id,
            'clinic_id': clinic.id,
            'appointment_id': invoice.appointment_id.id or False,
            'doctor_id': invoice.appointment_id.doctor_id.id or False,
            'visit_type': 'new',
            'booking_date': invoice.invoice_date,
            'state': 'visited' if invoice.invoice_status == 'paid' else 'confirmed',
        })
        invoice.write({'booking_id': booking.id})

    if _table_exists(cr, 'hcm_mig_prescription_18_0_7'):
        cr.execute("SELECT medical_record_id, prescription FROM hcm_mig_prescription_18_0_7")
        for medical_record_id, text in cr.fetchall():
            record = env['health.medical.record'].browse(medical_record_id).exists()
            if record and not record.prescription_ids:
                env['health.prescription'].create({
                    'medical_record_id': record.id,
                    'notes': text,
                    'state': 'draft',
                })
        cr.execute('DROP TABLE hcm_mig_prescription_18_0_7')
        _logger.info('Migrated legacy free-text prescriptions into prescription records.')
