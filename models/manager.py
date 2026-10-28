from odoo import fields, models, api


class ManagerData(models.Model):
    _name = "roadpay.manager.data"
    _description = "Manager Information"

    # Added new fields #T10787
    user_id = fields.Many2one("res.users")
    name = fields.Char(required=True)
    age = fields.Integer()
    phone_number = fields.Char()
    address = fields.Char()
    image = fields.Binary()
    plaza_ids = fields.One2many(
        "roadpay.plaza",
        "manager_id",
    )
    operators_id = fields.One2many(
        "roadpay.operator.data",
        "manager_id",
    )
    plaza_count = fields.Integer(compute="_compute_counts", store=True)
    operator_count = fields.Integer(compute="_compute_counts", store=True)
    display_plaza_name = fields.Char(compute="_compute_display_plaza_name")
    display_operators_count = fields.Integer(compute="_compute_display_operators_count")

    # Added new methods #T10787
    @api.depends("plaza_ids")
    def _compute_display_plaza_name(self):
        """
        This method displays plaza name in kanban view. #T10787
        """
        for rec in self:
            rec.display_plaza_name = (
                rec.plaza_ids[0].name if rec.plaza_ids else "No Plaza Assigned"
            )

    @api.depends("operators_id")
    def _compute_display_operators_count(self):
        """
        This method displays operators count in kanban view. #T10787
        """
        for rec in self:
            rec.display_operators_count = len(rec.operators_id)

    @api.depends("plaza_ids", "operators_id")
    def _compute_counts(self):
        """
        This method displays count of plaza and operators for smart buttons. #T10787
        """
        for rec in self:
            rec.plaza_count = len(rec.plaza_ids)
            rec.operator_count = len(rec.operators_id)

    def action_view_plazas(self):
        """
        This method open list view of plaza from smart button. #T10787
        """
        self.ensure_one()
        return {
            "name": "Managed Plazas",
            "type": "ir.actions.act_window",
            "res_model": "roadpay.plaza",
            "view_mode": "list,form",
            "domain": [("manager_id", "=", self.id)],
            "context": {"default_manager_id": self.id},
        }

    def action_view_operators(self):
        """
        This method opens kanban view of operators added by that manager
        from smart button. #T10787
        """
        self.ensure_one()
        return {
            "name": "Managed Operators",
            "type": "ir.actions.act_window",
            "res_model": "roadpay.operator.data",
            "view_mode": "kanban,list,form",
            "domain": [("manager_id", "=", self.id)],
            "context": {"default_manager_id": self.id},
        }
