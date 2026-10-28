from odoo import models, fields


class Plaza(models.Model):
    _name = "roadpay.plaza"
    _description = "RoadPay Plaza"

    # Added new fields #T10787
    name = fields.Char(required=True)
    total_gates = fields.Integer()
    manager_id = fields.Many2one("roadpay.manager.data", store=True)
    active = fields.Boolean(default=True)
    rate_ids = fields.One2many("roadpay.rate", "plaza_id")
    operator_ids = fields.One2many("roadpay.operator.data", "plaza_id")

    # Added sql constraint for unique plaza name and manager name. #T10787
    _sql_constraints = [
        ("name_unique", "unique(name)", "The plaza name must be unique!"),
        (
            "manager_unique",
            "unique(manager_id)",
            "This Manager is already assigned to another plaza!",
        ),
    ]
