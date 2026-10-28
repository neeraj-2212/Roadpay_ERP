from odoo import models, fields


class Rate(models.Model):
    _name = "roadpay.rate"
    _description = "Toll Rate Configuration"

    # Added new fields #T10787
    plaza_id = fields.Many2one("roadpay.plaza", required=True)
    vehicle_type = fields.Selection(
        [
            ("car", "Car/Jeep/Van"),
            ("bus", "Bus"),
            ("truck", "Truck"),
            ("lcv", "LCV"),
            ("multi", "Multi-Axle"),
        ],
        required=True,
    )
    amount = fields.Float(required=True)
