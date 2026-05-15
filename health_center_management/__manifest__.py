{
    'name': 'Health Center Patient Services Management',
    'version': '18.0.1.0.0',
    'summary': 'Patient Services Management System for Health Centers',
    'description': """
        A complete patient services management system for health centers including:
        - Patient and Booking Management
        - Clinic and Doctor Management
        - Medical Records and Examinations
        - Role-based Access Control (Patient / Doctor / Employee)
        - Pharmacy and Laboratory Portal
        - Password-Protected Employee and Doctor Portals
        - Password-Protected Reports Portal (Employee & Doctor only) — fully in English
        - Save & Confirm button (✔) on ALL editable forms/tables
        - Discard confirmation dialog on all editable forms
        - Health Center home screen: Today's Available Clinics + Contact Us icon
        - Contact Us popup (read-only for all users)
        - Employee Portal: Edit Contact Information settings directly
        - PDF Reports for all tables
    """,
    'author': 'Health Center',
    'category': 'Healthcare',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/clinic_data.xml',
        'data/portal_config_data.xml',
        'data/portal_sections_data.xml',
        'report/examination_report.xml',
        'report/health_reports.xml',
        'views/contact_views.xml',
        'views/clinic_views.xml',
        'views/doctor_views.xml',
        'views/appointment_views.xml',
        'views/booking_views.xml',
        'views/patient_views.xml',
        'views/medical_record_views.xml',
        'views/examination_views.xml',
        'views/portal_sections_views.xml',
        'views/portal_login_views.xml',
        'views/report_portal_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
