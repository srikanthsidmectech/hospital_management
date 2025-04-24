from odoo import models, fields


class HospitalReception(models.Model):
    _name = "hospital.reception"
    _rec_name = "reception_id"

    reception_id = fields.Many2one("res.users", "Name")
    age = fields.Integer("Age")
