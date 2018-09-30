from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta,time
import datetime

class EmployeeModel(models.Model):
    _inherit="hr.employee"



    @api.multi
    def getAttendances(self,start_date,end_date):
        for rec in self:
            attendances_list = list()
            i = 0

            flag = False
            while True:
                    if flag == True:
                        break
                    else:
                        if i == 0:
                            date = start_date

                        attendances = self.env['hr.attendance'].search([('date_check', '=', date),('employee_id','=',rec.id)])
                        if attendances:
                            attendances = attendances[0]
                            date_check = attendances.date_check
                            employee_id = attendances.employee_id.id
                            leave_reason = 'N/A'
                            time_check_in = attendances.time_check_in
                            time_check_out = attendances.time_check_out
                            worked_hours = attendances.worked_hours
                            overtime_hours = attendances.overtime_hours

                            data = {
                                'date': date_check,
                                'employee_id': employee_id,
                                'leave_reason': leave_reason,
                                'time_check_in': time_check_in,
                                'time_check_out': time_check_out,
                                'worked_hours': worked_hours,
                                'overtime_hours': overtime_hours
                            }
                            res = self.env['hr.attendances.report.transient'].create(data)
                            attendances_list.append(res)
                        else:
                            leaves = self.env['hr.holidays'].search(
                                [('date_from_format', '<=', date), ('date_to_format', '>=', date),
                                 ('state', '=', 'validate'), ('employee_id', '=', rec.id)])
                            if leaves:
                                date_check = date
                                employee_id = leaves.employee_id.id
                                leave_reason = leaves.name
                                time_check_in = 'N/A'
                                time_check_out = 'N/A'
                                worked_hours = 8
                                overtime_hours = 0
                                data = {
                                    'date': date_check,
                                    'employee_id': employee_id,
                                    'leave_reason': leave_reason,
                                    'time_check_in': time_check_in,
                                    'time_check_out': time_check_out,
                                    'worked_hours': worked_hours,
                                    'overtime_hours': overtime_hours
                                }
                                res = self.env['hr.attendances.report.transient'].create(data)
                                attendances_list.append(res)
                            else:
                                data = {
                                    'date': date,
                                    'employee_id': rec.id,
                                    'leave_reason': 'N/A',
                                    'time_check_in': 'N/A',
                                    'time_check_out': 'N/A',
                                    'worked_hours': 0,
                                    'overtime_hours': 0
                                }
                                res = self.env['hr.attendances.report.transient'].create(data)
                                attendances_list.append(res)
                        if date[:10] == end_date[:10]:
                            flag = True
                            return attendances_list
                        else:
                            format_date = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
                            date = str(format_date + timedelta(days=1))[:10]
                            i += 1
                            attendances = None