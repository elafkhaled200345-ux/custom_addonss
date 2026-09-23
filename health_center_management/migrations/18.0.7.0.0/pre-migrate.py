# -*- coding: utf-8 -*-
"""Snapshot visit data before normalising health.patient.

The old schema stored one clinic/appointment/booking/record/invoice directly on
health.patient.  Those fields are removed from the model in 18.0.7.0.0, so we
snapshot them before registry/model updates and restore them into health.booking
in post-migrate.
"""
import logging

_logger = logging.getLogger(__name__)


def _column_exists(cr, table, column):
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
    """, (table, column))
    return bool(cr.fetchone())


def migrate(cr, version):
    if not version:
        return

    required = [
        'clinic_id', 'appointment_id', 'booking_id', 'booking_type',
        'followup_booking_number', 'medical_record_id', 'invoice_id', 'state',
    ]
    if all(_column_exists(cr, 'health_patient', c) for c in required):
        cr.execute('DROP TABLE IF EXISTS hcm_mig_patient_visit_18_0_7')
        cr.execute("""
            CREATE TABLE hcm_mig_patient_visit_18_0_7 AS
            SELECT id AS patient_id, clinic_id, appointment_id, booking_id,
                   booking_type, followup_booking_number, medical_record_id,
                   invoice_id, state
            FROM health_patient
        """)
        _logger.info('Snapshotted legacy patient visit data for normalization.')

    if _column_exists(cr, 'health_medical_record', 'prescription'):
        cr.execute('DROP TABLE IF EXISTS hcm_mig_prescription_18_0_7')
        cr.execute("""
            CREATE TABLE hcm_mig_prescription_18_0_7 AS
            SELECT id AS medical_record_id, prescription
            FROM health_medical_record
            WHERE prescription IS NOT NULL AND btrim(prescription) <> ''
        """)
        _logger.info('Snapshotted legacy free-text prescriptions.')
