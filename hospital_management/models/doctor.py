from odoo import models, fields


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _rec_name = "doctor_name"

    doctor_name = fields.Char("Doctor")
    doctor_age = fields.Integer("Age")
    experience = fields.Integer("Experience")
