{
    "name": "Hospital Management",
    "description": "patients,receptionists,doctors and accountants managed in Hospital",
    "version": "18.0",
    'license': 'LGPL-3',
    "depends": ['mail', "account", "sale", "web", ],
    "data":
        [
            "security/security.xml",
            "security/ir.model.access.csv",
            "data/mail_template_patient_invoice.xml",
            "views/view_patient.xml",
            "data/ir_sequence.xml",
            "views/view_doctor.xml",
            "views/view_reciptionsts.xml",
            "views/view_patient_appointment.xml",
            "report/patient_report_pdf.xml",
            "wizard/view_sale_report_wizard.xml",
            "report/sale_report_wizard.xml",
            "report/reports.xml",
            "views/menu_items.xml", ],
}
