from odoo import models, fields


class HealthContactSettings(models.Model):
    _name = 'health.contact.settings'
    _description = 'Health Center Contact Information / معلومات التواصل'
    _rec_name = 'center_name'

    center_name = fields.Char(
        string='Health Center Name / اسم المركز الصحي', required=True)
    address = fields.Text(string='Address / العنوان')
    phone = fields.Char(string='Phone / هاتف')
    phone2 = fields.Char(string='Phone 2 / هاتف 2')
    whatsapp = fields.Char(string='WhatsApp')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website / الموقع الإلكتروني')
    working_hours = fields.Text(string='Working Hours / أوقات العمل')
    logo = fields.Image(string='Logo / الشعار', max_width=512, max_height=512)
    social_twitter = fields.Char(string='Twitter / X')
    social_instagram = fields.Char(string='Instagram')
    social_snapchat = fields.Char(string='Snapchat')
