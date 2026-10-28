from odoo import fields, models, api


class OperatorData(models.Model):
    _name = "roadpay.operator.data"
    _description = "Operator Information"

    # Added new fields #T10787
    user_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        readonly=True,
    )
    name = fields.Char(required=True)
    age = fields.Integer()
    gate_no = fields.Selection(
        [(str(i), str(i)) for i in range(1, 7)],
    )
    image = fields.Binary()
    phone_number = fields.Char()
    address = fields.Char()
    plaza_id = fields.Many2one(
        "roadpay.plaza",
        required=True,
    )
    manager_id = fields.Many2one(
        "roadpay.manager.data",
        required=True,
        index=True,
    )
    transaction_ids = fields.One2many(
        "roadpay.operation.data",
        "operator_id",
    )
    txn_count = fields.Integer(
        compute="_compute_txn_count",
        store=True,
    )

    # Added new methods #T10787
    @api.depends("transaction_ids")
    def _compute_txn_count(self):
        """
        This method calculates the total number of linked transactions for
        the operator. #T10787
        """
        for rec in self:
            rec.txn_count = len(rec.transaction_ids)

    @api.onchange("plaza_id")
    def _onchange_plaza_id(self):
        """
        This method auto-set manager from selected plaza. #T10787
        """
        for rec in self:
            rec.manager_id = rec.plaza_id.manager_id

        return {"domain": {"plaza_id": [("manager_id.user_id", "=", self.env.uid)]}}

    @api.model
    def create(self, vals):
        """
        This method overrides record creation to ensure the manager is assigned
        if a plaza is provided. #t10787
        """
        if vals.get("plaza_id") and not vals.get("manager_id"):
            plaza = self.env["roadpay.plaza"].browse(vals["plaza_id"])
            vals["manager_id"] = plaza.manager_id.id
        return super().create(vals)

    def action_view_transactions(self):
        """
        This method opens a list view of transactions of particular
        operator. #T10787
        """
        self.ensure_one()
        return {
            "name": "Operator Transactions",
            "type": "ir.actions.act_window",
            "res_model": "roadpay.operation.data",
            "view_mode": "list,form",
            "domain": [("operator_id", "=", self.id)],
            "context": {"default_operator_id": self.id},
        }
