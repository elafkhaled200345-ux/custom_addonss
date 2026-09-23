# Database Review Implementation - Health Center Management 18.0.7.0.0

This release implements the database-review recommendations supplied with the project.

## Implemented corrections

1. **Patient normalization**
   - Removed visit-specific fields from `health.patient`: clinic, appointment, booking, invoice, medical-record, visit type/state and their derived display fields.
   - Added reverse One2many relations only: appointments, bookings, medical records and invoices.
   - Patient is now master data only.

2. **Booking as the visit hub**
   - `health.booking` now stores the visit type, patient, clinic, appointment, doctor and prior follow-up booking.
   - Added Arrival Time, Queue Number, Reception Employee, Check-in Time and Waiting Time.
   - Moved confirm/check-in/complete/cancel workflow from Patient to Booking.
   - Confirming a booking creates the visit medical record and consultation invoice where applicable.

3. **Appointment**
   - Added Appointment Type: Consultation, Follow-Up, Emergency.
   - Added No Show state and action.

4. **Medical Record / Prescription**
   - Added ICD-10 Diagnosis Code.
   - Replaced the medical-record free-text prescription with normalized models:
     `health.prescription` -> `health.prescription.line` -> `health.medicine`.
   - Legacy free-text prescription content is preserved in prescription notes during upgrade migration.

5. **Examination**
   - Added `performed_by`.

6. **Lab Request**
   - Added Priority (Normal/Urgent/STAT), Collected Date, Result Date and Approved By.

7. **Invoice**
   - Added Booking link, Currency, Tax %, Tax Amount, Amount Paid, Remaining Balance, Payment Date and Receipt Number.
   - Added Partial payment status.

8. **Pharmacy**
   - Added Dispensed By to dispense orders.
   - Added Batch Number and Expiry Date to dispense lines.

9. **Employee**
   - Added Department, Hire Date, National ID, System User and Signature.

10. **Normalization / dependent code**
   - Updated dashboard, clinic patient counts, security rule for doctor-patient visibility, demo data, reports and views to use the normalized relationships.
   - Added migration scripts for 18.0.7.0.0 to preserve legacy visit and prescription data.

## Validation performed

- Python source compilation (`compileall`).
- XML well-formedness parsing for all XML files.
- Static search for removed Patient visit-field references.

A full Odoo runtime upgrade/install test still requires an Odoo 18 server and database environment.
