# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class AttendanceExt(models.Model):

    _inherit = "hr.attendance"

    overtime_hours = fields.Float(string="Total Overtime Hours", compute='_compute_overtime_hours' ,store=True)

    @api.depends('overtime_50','overtime_100')
    def _compute_overtime_hours(self):
        for rec in self:
            if rec.overtime_50 or rec.overtime_100:
                rec.overtime_hours = rec.overtime_50 + rec.overtime_100

