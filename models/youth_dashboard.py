from collections import OrderedDict
from dateutil.relativedelta import relativedelta

from odoo import models, api, fields

CATEGORY_LABELS = OrderedDict([
    ('tour', 'Tours'),
    ('ice_cream', 'Ice Cream Stalls'),
    ('radham', 'Radham (Vehicle)'),
    ('convention', 'Events / Conventions'),
    ('other', 'Other'),
])

CATEGORY_ICONS = {
    'tour': 'fa-bus',
    'ice_cream': 'fa-cutlery',
    'radham': 'fa-car',
    'convention': 'fa-users',
    'other': 'fa-folder',
}


class YouthEvent(models.Model):
    _inherit = 'youth.event'

    @api.model
    def get_ninja_dashboard_data(self):
        """Fetch real-time accounting metrics for the Youth Finance Dashboard."""
        events = self.search([])
        finances = self.env['youth.finance'].search([])

        total_expense = sum(f.amount for f in finances if f.type == 'expense')
        total_ledger_income = sum(f.amount for f in finances if f.type == 'income')
        total_fees = sum(events.filtered(lambda e: e.event_type == 'tour').mapped('total_fees'))
        total_income = total_ledger_income + total_fees
        net_profit = total_income - total_expense

        # ---- Breakdown by category ----
        breakdown = []
        for key, label in CATEGORY_LABELS.items():
            cat_events = events.filtered(lambda e, k=key: e.event_type == k)
            income = sum(cat_events.mapped('total_income'))
            expense = sum(cat_events.mapped('total_expense'))
            breakdown.append({
                'key': key,
                'label': label,
                'icon': CATEGORY_ICONS.get(key, 'fa-folder'),
                'count': len(cat_events),
                'income': income,
                'expense': expense,
                'profit': income - expense,
            })

        # ---- Monthly trend (last 6 months, income vs expense) ----
        today = fields.Date.context_today(self)
        months = []
        for i in range(5, -1, -1):
            m_date = today - relativedelta(months=i)
            months.append((m_date.strftime('%Y-%m'), m_date.strftime('%b %Y')))

        month_income = OrderedDict((key, 0.0) for key, _ in months)
        month_expense = OrderedDict((key, 0.0) for key, _ in months)

        for f in finances:
            if not f.date:
                continue
            key = f.date.strftime('%Y-%m')
            if key not in month_income:
                continue
            if f.type == 'income':
                month_income[key] += f.amount
            else:
                month_expense[key] += f.amount

        for ev in events.filtered(lambda e: e.event_type == 'tour' and e.date):
            key = ev.date.strftime('%Y-%m')
            if key in month_income:
                month_income[key] += ev.total_fees

        trend = {
            'labels': [label for _, label in months],
            'income': [round(month_income[key], 2) for key, _ in months],
            'expense': [round(month_expense[key], 2) for key, _ in months],
        }

        participants_count = self.env['youth.participant'].search_count([])

        recent_finances = finances.search_read(
            [], ['date', 'name', 'type', 'amount', 'event_id'],
            limit=8, order='date desc, id desc'
        )
        for r in recent_finances:
            r['event_name'] = r['event_id'][1] if r['event_id'] else '-'

        return {
            'summary': {
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': net_profit,
                'total_events': len(events),
                'total_participants': participants_count,
            },
            'breakdown': breakdown,
            'trend': trend,
            'recent_finances': recent_finances,
        }
