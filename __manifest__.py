# -*- coding: utf-8 -*-
{
    'name': 'MRP Quality Workflow',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quality Control Integration for Manufacturing Process',
    'depends': ['base', 'mrp', 'mail'],
    'data': [
        'security/quality_security.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
        'views/quality_checkpoint_views.xml',
        'report/quality_report_templates.xml',
        'report/quality_reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}