from odoo import models, fields, api


class YouthEvent(models.Model):
    _name = 'youth.event'
    _description = 'Youth Activity or Event'
    _order = 'date desc, id desc'

    name = fields.Char(string='Activity Name', required=True)
    event_type = fields.Selection([
        ('tour', 'Tour'),
        ('ice_cream', 'Ice Cream Stall'),
        ('radham', 'Radham (Vehicle Rental)'),
        ('convention', 'Event / Convention'),
        ('other', 'Other'),
    ], string='Category', required=True, default='tour')

    date = fields.Date(string='Date', default=fields.Date.context_today)
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    participant_ids = fields.One2many('youth.participant', 'event_id', string='Participants')
    finance_ids = fields.One2many('youth.finance', 'event_id', string='Finances')

    participant_count = fields.Integer(string='Participants', compute='_compute_totals', store=True)

    total_fees = fields.Float(string='Participant Fees', compute='_compute_totals', store=True,
                               help='Total fees collected from participants (Tour category only).')
    other_income = fields.Float(string='Other Income', compute='_compute_totals', store=True,
                                 help='Income recorded in the ledger (sponsorships, stall sales, rent, etc).')
    total_income = fields.Float(string='Total Income', compute='_compute_totals', store=True)
    total_expense = fields.Float(string='Total Expense', compute='_compute_totals', store=True)
    net_profit = fields.Float(string='Net Profit/Loss', compute='_compute_totals', store=True)

    @api.depends('finance_ids.type', 'finance_ids.amount', 'participant_ids.amount', 'event_type')
    def _compute_totals(self):
        for record in self:
            ledger_income = sum(line.amount for line in record.finance_ids if line.type == 'income')
            expense = sum(line.amount for line in record.finance_ids if line.type == 'expense')
            fees = sum(record.participant_ids.mapped('amount')) if record.event_type == 'tour' else 0.0


            record.participant_count = len(record.participant_ids)
            record.total_fees = fees
            record.other_income = ledger_income
            record.total_income = fees + ledger_income
            record.total_expense = expense
            record.net_profit = fees + ledger_income - expense


class YouthParticipant(models.Model):
    _name = 'youth.participant'
    _description = 'Tour Participant'
    _order = 'name'

    event_id = fields.Many2one('youth.event', string='Event', ondelete='cascade')
    name = fields.Char(string='Participant Name', required=True)
    total_person = fields.Float(string='Total person')
    amount = fields.Float(string='Tour Fee Paid', default=0.0)
    notes = fields.Char(string='Remarks')
