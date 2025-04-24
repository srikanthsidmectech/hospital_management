from odoo import models, fields, api


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char(string='Patient ID', required=True, copy=False, readonly=True,
                       default='New')
    patient_id = fields.Many2one("res.partner", "Name", domain=[
        ("email", "!=", False),
    ])
    email = fields.Char(related="patient_id.email", string="email")
    patient_age = fields.Integer("Age")
    date = fields.Date("Date")
    is_in_ward = fields.Boolean(string="Is patient in ward")
    from_date = fields.Date(string="Admit Date")
    to_date = fields.Date(string="Discharge Date")
    invoices = fields.One2many("hospital.patient.invoices", "patient")
    reception_id = fields.Many2one("hospital.reception", "Reception")
    company_id = fields.Many2one("res.company", string="Company", compute="compute_user_company")
    user_id = fields.Many2one("res.users", compute="compute_user_company")
    move_id = fields.Many2one("account.move", string="Accounting Invoice", readonly=True)
    status = fields.Selection([("draft", "Draft"), ("confirm", "Confirmed")], "status", default="draft")
    appointment_id = fields.Many2one('hospital.patient.appointments', string="Appointment")

    #
    def compute_user_company(self):
        for vals in self:
            vals.user_id = self.env.user.id
            vals.company_id = self.env.company.id

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.patient') or 'New'
        return super(HospitalPatient, self).create(vals)

    #
    # def compute_name(self):
    #         for rec in self:
    #             rec.name = self.env['ir.sequence'].next_by_code('hospital.patient') or 'New'

    def action_send_email(self):
        template = self.env.ref("hospital_management.mail_template_demo_patient_invoice")
        for rec in self:
            if not rec.patient_id.email:
                raise ValueError("pls add partner email")
            else:
                rec.user_id = self.env.user.id
                template.send_mail(rec.id, force_send=True)

    def return_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('move_type', '=', 'out_invoice'), ('partner_id', '=', self.patient_id.id)],
            'context': {'create': False},
            'target': 'current',
        }

    def action_reset_to_draft(self):
        for rec in self:
            rec.status = "draft"

    def action_confirm(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise ValueError("No sale journal found. Please configure a sale journal.")

        for rec in self:
            if not rec.patient_id:
                raise ValueError("Patient has no linked customer (res.partner). Please set it.")

            invoice_lines = []
            for i in rec.invoices:
                invoice_lines.append((0, 0, {
                    'product_id': i.product.id,
                    'quantity': i.qty,
                    'price_unit': i.unit_price,
                    'name': i.product.name,
                }))

            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': rec.patient_id.id,
                'invoice_date': rec.date or fields.Date.today(),
                'journal_id': journal.id,
                'invoice_line_ids': invoice_lines,
            }

            if rec.move_id:
                # If invoice already exists, update it instead of creating a new one
                rec.move_id.write({
                    'partner_id': rec.patient_id.id,
                    'invoice_date': rec.date,
                    'invoice_line_ids': [(5, 0, 0)] + invoice_lines,  # clear old lines and add new
                })
            else:
                move = self.env['account.move'].create(move_vals)
                rec.move_id = move.id

            rec.status = "confirm"


class HospitalPatientInvoice(models.Model):
    _name = "hospital.patient.invoices"
    _description = "Patient Invoice"
    _rec_name = "product"

    product = fields.Many2one("product.product", string="Product name", required=True)
    qty = fields.Float(string="Qty", required=True)
    unit_price = fields.Float(related="product.lst_price", string="Unit price")
    amount_due = fields.Float(string="Due Amount")
    sub_total = fields.Float(string="Sub Total", readonly=True, compute="compute_subtotal")
    patient = fields.Many2one("hospital.patient", string="Patient", required=True)

    def compute_subtotal(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price
