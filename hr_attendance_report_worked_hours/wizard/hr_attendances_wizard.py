from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta,time
import datetime

class AttendancesWizard(models.TransientModel):

    _name="hr_attendance_report.hr_attendances_wizard_report"

    start_date = fields.Datetime(string="Start Date",required=True)
    end_date = fields.Datetime(string="End Date",required=True)
    type = fields.Selection([('employee','By Employee'),('all','All')],default="all")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    file_format = fields.Selection([('pdf','PDF'),('xls','Excel')])

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date','file_format','employee_id','type'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['desde', 'hasta','file_format','employee_id','type'])[0])
        return self.env.ref('hr_attendance_report_worked_hours.attendances_report_action').report_action(self, data)

class ReportAttendanceWizard(models.AbstractModel):
    _name = 'report.hr_attendance_report_worked_hours.attendance_report'
    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        attendances_list = list()
        i = 0
        flag = False
        if docs.type=="employee":
            while True:
               if flag == True:
                   break
               else:
                    if i==0:
                        date = docs.start_date
                    attendances = self.env['hr.attendance'].search([('date_check','=',date)])
                    if attendances:
                        attendances = attendances[0]
                        date_check = attendances.date_check
                        employee_id = attendances.employee_id.id
                        leave_reason = 'N/A'
                        time_check_in = attendances.time_check_in
                        time_check_out = attendances.time_check_out
                        worked_hours = attendances.worked_hours
                        overtime_hours = attendances.overtime_hours

                        data={
                            'date' :date_check,
                            'employee_id' : employee_id,
                            'leave_reason' : leave_reason,
                            'time_check_in' : time_check_in,
                            'time_check_out' : time_check_out,
                            'worked_hours' : worked_hours,
                            'overtime_hours' : overtime_hours
                        }
                        res= self.env['hr.attendances.report.transient'].create(data)
                        attendances_list.append(res)
                    else:
                        print("***** FECHA: *****", date)
                        leaves = self.env['hr.holidays'].search([('date_from_format','<=',date),('date_to_format','>=',date),('state','=','validate'),('employee_id','=',docs.employee_id.id)])
                        if leaves:
                            print("***** FECHA: *****",date)
                            print("***** FECHA PROYECTO *****",leaves.date_from_format)
                            date_check = date
                            employee_id = leaves.employee_id.id
                            leave_reason = leaves.name
                            time_check_in = 'N/A'
                            time_check_out = 'N/A'
                            worked_hours = 8
                            overtime_hours = 0
                            data={
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
                                'employee_id': docs.employee_id.id,
                                'leave_reason': 'N/A',
                                'time_check_in': 'N/A',
                                'time_check_out': 'N/A',
                                'worked_hours': 0,
                                'overtime_hours': 0
                            }
                            res = self.env['hr.attendances.report.transient'].create(data)
                            attendances_list.append(res)
                    if date[:10] == docs.end_date[:10]:
                        flag= True
                        docargs = {
                            'doc_ids': self.ids,
                            'doc_model': self.model,
                            'docs': docs,
                            'time': time,
                            'attendances': attendances_list
                        }
                    else:
                        format_date = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
                        date = str(format_date + timedelta(days=1))[:10]
                        i += 1
                        attendances = None
        else:
            employees = self.env['hr.employee'].search([])
            docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'time': time,
                'employees': employees
            }
        return docargs




class AttendancesTransReportModel(models.TransientModel):
    _name = 'hr.attendances.report.transient'

    date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee',string='Employee')
    leave_reason = fields.Char(string="Leave reason")
    time_check_in = fields.Char(string="Time check in")
    time_check_out = fields.Char(string="Time check out")
    worked_hours = fields.Integer(string="Worked Hours")
    overtime_hours = fields.Integer(string="Overtime Hours")
