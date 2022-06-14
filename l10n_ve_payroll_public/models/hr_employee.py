from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    childs_ids = fields.One2many('hr.employee.child', 'employee_id', string='Hijos(a)')
    children = fields.Integer(compute='get_number_children', store=True)

    @api.depends('childs_ids.age')
    def get_number_children(self):
        if len(self.childs_ids) >= 1:
            childs = 0
            for child in self.childs_ids:
                if child.age <= 17:
                    childs += 1
            self.children = childs
        else:
            self.children = 0


class HrEmployeeChild(models.Model):
    _name = 'hr.employee.child'
    _description = 'Hijos(a) de los Empleados'

    name = fields.Char(string='Nombre y Apellido', required=True)
    birth_date = fields.Date(string='Fecha de Nacimiento', required=True)
    age = fields.Integer(string='Edad', compute='get_age', store=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado')

    @api.depends('birth_date')
    def get_age(self):
        for child in self:
            if child.birth_date:
                child.age = relativedelta(datetime.now(), child.birth_date).years

    @api.model
    def _cron_update_annio_children(self):
        children = self.env['hr.employee.child'].search([])
        employees = self.env['hr.employee'].search([])
        for child in children:
            child.age = relativedelta(datetime.now(), child.birth_date).years
        for employee in employees:
            if len(employee.childs_ids) > 1:
                childs = 0
                for child in employee.childs_ids:
                    if child.age < 17:
                        childs += 1
                employee.children = childs
            else:
                employee.children = 0
