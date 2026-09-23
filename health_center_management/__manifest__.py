{
    'name': 'Health Center Management',
    'version': '18.0.7.0.0',
    'summary': 'نظام إدارة مراكز الصحة — Professional Healthcare Management System',
    'description': """
        A fully professional patient services management system for health centers:
        ─────────────────────────────────────────────────────────────────
        • Patient, Booking & Appointment Management (Kanban + Calendar)
        • Clinic & Doctor Management
        • Medical Records with Attachments
        • Examinations & Prescriptions
        • Laboratory Requests (dynamic test lines)
        • Pharmacy Module
        • Health Invoicing with Insurance support
        • Role-based Access Control (Patient / Doctor / Employee)
        • Record-level security rules (patients see only their own data)
        • Hashed passwords — no plain-text storage
        • Chatter / Activity tracking on all major models
        • Statistics Dashboard
        • PDF Reports
        • Arabic + English bilingual support
    """,
    'author': 'Health Center',
    'category': 'Healthcare',
    'depends': ['base', 'mail', 'web', 'account'],
    'data': [
        'security/security_groups.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/clinic_data.xml',
        'data/portal_config_data.xml',
        'data/contact_data.xml',
        'data/portal_sections_data.xml',
        'report/examination_report.xml',
        'report/health_reports.xml',
        'report/lab_request_report.xml',
        'report/invoice_report.xml',
        'views/dashboard_views.xml',
        'views/contact_views.xml',
        'views/clinic_views.xml',
        'views/doctor_views.xml',
        'views/employee_views.xml',
        'views/portal_config_views.xml',
        'views/appointment_views.xml',
        'views/booking_views.xml',
        'views/patient_views.xml',
        'views/medical_record_views.xml',
        'views/prescription_views.xml',
        'views/examination_views.xml',
        'views/lab_test_views.xml',
        'views/lab_request_views.xml',
        'views/pharmacy_views.xml',
        'views/health_invoice_views.xml',
        'views/portal_sections_views.xml',
        'views/portal_login_views.xml',
        'views/report_portal_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
