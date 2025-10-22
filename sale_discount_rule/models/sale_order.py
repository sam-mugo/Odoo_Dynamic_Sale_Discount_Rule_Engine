from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    discount_rule_id = fields.Many2one('sale.discount.rule', string='Applied Discount Rule', readonly=True)


    def _get_matching_discount_rules(self):
        """Return recordset of matching rules for this order, ordered by discount_percent desc, then valid_from desc."""
        self.ensure_one()
        domain = [
            ('active', '=', True),
            '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id),
        ]
        rules = self.env['sale.discount.rule'].search(domain)
        # filter in Python because matching requires currency conversion & partner tags
        matching = rules.filtered(lambda r: r._matches_order(self))
        # ordering: highest discount first, then newest
        return matching.sorted(key=lambda r: (r.discount_percent or 0.0, r.valid_from or fields.Date.today()), reverse=True)


    def apply_discount_rules(self):
        """Apply the best matching discount rule (if any) to order lines. Returns the applied rule or False."""
        self.ensure_one()
        best_rule = False
        matching = self._get_matching_discount_rules()
        if matching:
        # rules are sorted desc in _get_matching_discount_rules
            best_rule = matching[0]


        # apply discounts
        if best_rule:
            for line in self.order_line:
                # skip service products if you want: e.g., if line.product_id.type == 'service': continue
                line.write({'discount': best_rule.discount_percent})
            self.discount_rule_id = best_rule.id
        else:
            # no rule matches: clear any previously applied rule-discount (optional)
            # only clear if discount_rule_id was set by this module
            if self.discount_rule_id:
                for line in self.order_line:
                    # optionally only clear if discount == previously set percent
                    line.write({'discount': 0.0})
                self.discount_rule_id = False
        return best_rule


    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        # After creation apply discount rules for each
        for order in orders:
            try:
                order.apply_discount_rules()
            except Exception:
                # do not block creation - log and continue
                _logger = self.env['ir.logging']
                _logger.sudo().create({
                'name': 'sale_discount_rules.apply_error',
                'type': 'server',
                'dbname': self.env.cr.dbname,
                'level': 'ERROR',
                'message': 'Failed to apply discount rules on order %s' % (order.name,),
                'path': 'sale_discount_rules',
                })
        return orders


    def button_reapply_discounts(self):
        """Button action called from the form view to force re-evaluation."""
        for order in self:
            order.apply_discount_rules()
        return True