{
    'name': 'Sale Discount Rules',
    'version': '1.0.0',
    'summary': 'Dynamic sales discount rules engine (apply best matching discount)',
    'category': 'Sales',
    'author': 'Assistant',
    'license': 'OPL-1',
    'depends': ['sale_management','sale'],
    'data': [
        # 'security/sale_discount_rules_security.xml',
        'security/ir.model.access.csv',
        'views/sale_discount_rule_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}