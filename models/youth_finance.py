from odoo import models, fields


class YouthFinance(models.Model):
    _name = 'youth.finance'
    _description = 'Youth Income and Expense Record'
    _order = 'date desc, id desc'

    name = fields.Char(string='Description', required=True)
    event_id = fields.Many2one('youth.event', string='Activity / Event', ondelete='set null')
    event_type = fields.Selection(related='event_id.event_type', string='Category', store=True, readonly=True)
    type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
    ], string='Type', required=True, default='income')

    amount = fields.Float(string='Amount', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
