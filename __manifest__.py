{
    'name': 'Youth Management',
    'version': '19.0.1.0.0',
    'category': 'Management',
    'summary': 'Simple event and income/expense tracking for Youth Activities',
    'author': 'Youth Org',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/youth_dashboard_views.xml',
        'views/youth_event_views.xml',
        'views/youth_finance_views.xml',
        'views/youth_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'youth/static/src/js/youth_dashboard.js',
            'youth/static/src/xml/youth_dashboard.xml',
            'youth/static/src/scss/youth_dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
}