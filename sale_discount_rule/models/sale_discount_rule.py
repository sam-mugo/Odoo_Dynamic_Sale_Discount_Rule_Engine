from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleDiscountRule(models.Model):
    _name = 'sale.discount.rule'
    _description = 'Sale Discount Rule'
    _order = 'discount_percent desc, valid_from desc'


    name = fields.Char(required=True)
    min_amount = fields.Monetary(string='Minimum Amount', currency_field='company_currency_id', default=0.0)
    max_amount = fields.Monetary(string='Maximum Amount', currency_field='company_currency_id', default=0.0)
    discount_percent = fields.Float(string='Discount (%)', digits='Discount', required=True)
    customer_group_id = fields.Many2one('res.partner.category', string='Customer Tag')
    valid_from = fields.Date()
    valid_to = fields.Date()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


    # helper field for currency on amounts
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)


    @api.constrains('min_amount', 'max_amount', 'discount_percent')
    def _check_amounts(self):
        for rec in self:
            if rec.min_amount < 0 or rec.max_amount < 0:
                raise ValidationError('Min and Max amounts must be positive or zero.')
            if rec.max_amount and rec.min_amount > rec.max_amount:
                raise ValidationError('Minimum amount cannot be greater than maximum amount.')
            if rec.discount_percent < 0 or rec.discount_percent > 100:
                raise ValidationError('Discount percent must be between 0 and 100.')


    def _matches_order(self, order):
        """Return True if rule matches the given sale.order (order is a record).
        Amount comparison is performed in the company's currency of the rule / order.company_id.
        """
        self.ensure_one()
        if not self.active:
            return False
        if self.company_id and order.company_id != self.company_id:
            return False


        # check date validity
        today = fields.Date.context_today(order)
        if self.valid_from and self.valid_from > today:
            return False
        if self.valid_to and self.valid_to < today:
            return False


        # convert the order amount to the company's currency for comparison
        order_amount = order.amount_untaxed
        order_currency = order.currency_id or order.company_id.currency_id
        rule_currency = self.company_currency_id or order.company_id.currency_id
        if order_currency != rule_currency:
            order_amount = order_currency._convert(order_amount, rule_currency, order.company_id, order.date_order or today)


        # min/max check
        if self.min_amount and order_amount < self.min_amount:
            return False
        if self.max_amount and self.max_amount > 0 and order_amount > self.max_amount:
            return False


        # customer group check (if set)
        if self.customer_group_id:
        # partner tags are in partner.category_id or tag_ids depending on Odoo version
            if self.customer_group_id not in order.partner_id.category_id:
                return False


        return True