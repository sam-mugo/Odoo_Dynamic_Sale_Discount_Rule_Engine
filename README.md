# Odoo_Dynamic_Sale_Discount_Rule_Engine

### Compatibility
* v17 & v18

## Behavior summary

* Adds a model sale.discount.rule to store discount rules.
* Applies the best matching rule (highest discount_percent) automatically on sale order creation.
* Adds a button Reapply Discounts on the sale order to re-evaluate and apply discounts when lines/partner change.
* Applies the discount percentage to all order lines' discount field (configurable in code if needed).
* Adds access control so Sales Managers manage rules and Sales Users can view and trigger reapply.
