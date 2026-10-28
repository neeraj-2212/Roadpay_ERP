from odoo import api, fields, models


class OperationsData(models.Model):
    _name = "roadpay.operation.data"
    _description = "Operation Data"
    _rec_name = "name"

    # Added new fields #T10788
    name = fields.Char(
        readonly=True,
        copy=False,
        default="New",
    )
    plaza_id = fields.Many2one("roadpay.plaza", required=True)
    manager_id = fields.Many2one(
        "roadpay.manager.data", related="plaza_id.manager_id", store=True, readonly=True
    )
    operator_id = fields.Many2one("roadpay.operator.data", required=True)
    gate_no = fields.Selection(related="operator_id.gate_no", store=True, readonly=True)
    vehicle_no = fields.Char()
    vehicle_type = fields.Selection(
        [
            ("car", "Car/Jeep/Van"),
            ("bus", "Bus"),
            ("truck", "Truck"),
            ("lcv", "LCV"),
            ("multi", "Multi-Axle"),
        ]
    )
    toll_amount = fields.Float(compute="_compute_toll_amount", store=True)
    timestamp = fields.Datetime(default=fields.Datetime.now)
    status = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("cancel", "Cancelled"),
        ],
        default="new",
        store=True,
        help="The status of the transaction record.",
    )

    # Added new methods #T10788
    @api.model_create_multi
    def create(self, vals_list):
        """
        This method create unique sequence for every transactions. #T10787
        """
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("roadpay.operation.sequence")
                    or "New"
                )
            # Ensure the initial state is set correctly upon creation
            if not vals.get("state"):
                vals["state"] = "draft"

        return super().create(vals_list)

    @api.onchange("plaza_id")
    def _onchange_plaza(self):
        """
        This method automatically fill manager and filter operators based on
        selected plaza. #T10787
        """
        if self.plaza_id:
            self.manager_id = self.plaza_id.manager_id.id
            return {"domain": {"operator_id": [("plaza_id", "=", self.plaza_id.id)]}}
        else:
            self.manager_id = False
            return {"domain": {"operator_id": []}}

    @api.onchange("operator_id")
    def _onchange_operator(self):
        """
        This method updates the plaza field automatically when an operator
        is selected. #T10787
        """
        if self.operator_id:
            self.plaza_id = self.operator_id.plaza_id.id

    @api.depends("vehicle_type", "plaza_id")
    def _compute_toll_amount(self):
        """
        This method calculates the toll amount based on the selected
        vehicle type and plaza. #T10788
        """
        for rec in self:
            rec.toll_amount = 0.0
            if rec.vehicle_type and rec.plaza_id:
                rate = self.env["roadpay.rate"].search(
                    [
                        ("plaza_id", "=", rec.plaza_id.id),
                        ("vehicle_type", "=", rec.vehicle_type),
                    ],
                    limit=1,
                )
                if rate:
                    rec.toll_amount = rate.amount
