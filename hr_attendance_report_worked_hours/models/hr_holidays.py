from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta,time
import datetime

class HolidayModel(models.Model):
    _inherit="hr.holidays"

    date_from_format = fields.Char(compute="_compute_date",store=True)
    date_to_format = fields.Char(compute="_compute_date",store=True)

    @api.depends('date_from','date_to')
    def _compute_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                rec.date_from_format = rec.date_from[:10]
                rec.date_to_format = rec.date_to[:10]