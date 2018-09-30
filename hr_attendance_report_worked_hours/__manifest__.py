# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{   'author' : 'Rapidsoft SA',
    'name': 'Attendances Report Date Range',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Generate employee attendances report',
    'description': """
This module aims to generate employee attendances report, including ausences.
==================================================

Generate report of the attendances of the employees on the basis of the
actions(Check in/Check out) performed by them and the related ausences with a date range and worked hours. 
       """,
    'website': 'http://rapidsoft.com.py',
    'depends': ['hr','hr_holidays','hr_attendance'],
    'data': [
        'report/reports.xml',
        'report/hr_attendances_report.xml',
        'wizard/hr_attendances_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
