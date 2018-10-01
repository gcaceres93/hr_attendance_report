from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta,time
import datetime

class AttendancesWizard(models.TransientModel):

    _name="hr_attendance_worked_hours_wizard"

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
        if self.file_format == 'pdf':
            return self.env.ref('hr_attendance_report_worked_hours.attendances_report_action').report_action(self, data)
        else:
            return self.env.ref('hr_attendance_report_worked_hours.attendances_report_xlsx_action').report_action(self, data)



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
                        leaves = self.env['hr.holidays'].search([('date_from_format','<=',date),('date_to_format','>=',date),('state','=','validate'),('employee_id','=',docs.employee_id.id)])
                        if leaves:
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

class ReportAttendanceXLSXWizard(models.AbstractModel):
    _name = 'report.hr_attendance_report_worked_hours.attendance_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        attendances_list = list()
        i = 3
        # Create a format to use in the merged range.
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#F15F40',
            'font_color': 'white'})
        bold = workbook.add_format({'bold': True, 'fg_color': 'gray', 'align': 'center'})
        border = workbook.add_format({'border': 1})
        if wizard.type=="employee":
            sheet = workbook.add_worksheet(str(wizard.employee_id.name))
            sheet.merge_range('A1:G1', 'Attendance Report By Employee', merge_format)
            sheet.merge_range('A2:G2', 'Employee:'+str(wizard.employee_id.name), merge_format)
            sheet.set_column('A:G', 25)
            sheet.write(2, 0, 'Date', bold)
            sheet.write(2, 1, 'Employee', bold)
            sheet.write(2, 2, 'Leave reason', bold)
            sheet.write(2, 3, 'Check in', bold)
            sheet.write(2, 4, 'Check out', bold)
            sheet.write(2, 5, 'Worked Hours', bold)
            sheet.write(2, 6, 'Overtime Hours', bold)
            attendances_list = wizard.employee_id.getAttendances(wizard.start_date,wizard.end_date) #get all attendances for employee
            if attendances_list:
                for att in attendances_list:
                    sheet.write(i, 0, att.date,border)
                    sheet.write(i, 1, att.employee_id.name,border)
                    sheet.write(i, 2, att.leave_reason,border)
                    sheet.write(i, 3, att.time_check_in,border)
                    sheet.write(i, 4, att.time_check_out,border)
                    sheet.write(i, 5, att.worked_hours, border)
                    sheet.write(i, 6, att.overtime_hours, border)
                    i += 1
        else:
            employees = self.env['hr.employee'].search([('active','=',True)])
            if employees:
                for e in employees:
                    sheet = workbook.add_worksheet(str(e.name))
                    sheet.merge_range('A1:G1', 'Attendance Report', merge_format)
                    sheet.merge_range('A2:G2', 'Employee:' + str(e.name), merge_format)
                    sheet.set_column('A:G', 25)
                    sheet.write(2, 0, 'Date', bold)
                    sheet.write(2, 1, 'Employee', bold)
                    sheet.write(2, 2, 'Leave reason', bold)
                    sheet.write(2, 3, 'Check in', bold)
                    sheet.write(2, 4, 'Check out', bold)
                    sheet.write(2, 5, 'Worked Hours', bold)
                    sheet.write(2, 6, 'Overtime Hours', bold)
                    attendances_list = e.getAttendances(wizard.start_date,wizard.end_date)
                    if attendances_list:
                        for att in attendances_list:
                            sheet.write(i, 0, att.date, border)
                            sheet.write(i, 1, att.employee_id.name, border)
                            sheet.write(i, 2, att.leave_reason, border)
                            sheet.write(i, 3, att.time_check_in, border)
                            sheet.write(i, 4, att.time_check_out, border)
                            sheet.write(i, 5, att.worked_hours, border)
                            sheet.write(i, 6, att.overtime_hours, border)
                            i += 1
                    i = 3

class AttendancesTransReportModel(models.TransientModel):
    _name = 'hr.attendances.report.transient'

    date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee',string='Employee')
    leave_reason = fields.Char(string="Leave reason")
    time_check_in = fields.Char(string="Time check in")
    time_check_out = fields.Char(string="Time check out")
    worked_hours = fields.Integer(string="Worked Hours")
    overtime_hours = fields.Integer(string="Overtime Hours")
