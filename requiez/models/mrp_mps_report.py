# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Humanytek (<www.humanytek.com>).
#    Rubén Bravo <rubenred18@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import datetime
import babel.dates
from dateutil import relativedelta
from odoo import api, models, _, fields
import pytz

NUMBER_OF_COLS = 12


class MrpMpsReport(models.TransientModel):
    _inherit = 'mrp.mps.report'

    @api.multi
    def get_data(self, product):
        result = []
        forecasted = product.mps_forecasted
        date = datetime.datetime.now()
        local_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        indirect = self.get_indirect(product)[product.id]
        display = _('To Receive / To Supply / Produce')
        buy_type = self.env.ref('purchase.route_warehouse0_buy', raise_if_not_found=False)
        mo_type = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        lead_time = 0
        if buy_type and buy_type.id in product.route_ids.ids:
            lead_time = (product.seller_ids and product.seller_ids[0].delay or 0) + self.env.user.company_id.po_lead
        if mo_type and mo_type.id in product.route_ids.ids:
            lead_time = product.produce_delay + self.env.user.company_id.manufacturing_lead
        leadtime = date + relativedelta.relativedelta(days=int(lead_time))
        # Take first day of month or week
        if self.period == 'month':
            date = datetime.datetime(date.year, date.month, 1)
        elif self.period == 'week':
            date = date - relativedelta.relativedelta(days=date.weekday())

        if date < datetime.datetime.today():
            initial = product.with_context(to_date=date.strftime('%Y-%m-%d')).qty_available
        else:
            initial = product.qty_available
        # Compute others cells
        for p in range(NUMBER_OF_COLS):
            if self.period == 'month':
                date_to = date + relativedelta.relativedelta(months=1)
                name = date.strftime('%b')
                name = babel.dates.format_date(format="MMM YY", date=date, locale=self._context.get('lang') or 'en_US')
            elif self.period == 'week':
                date_to = date + relativedelta.relativedelta(days=7)
                name = _('Week %s') % babel.dates.format_datetime(
                    date, format="w",
                    locale=self._context.get('lang') or 'en_US'
                )
            else:
                date_to = date + relativedelta.relativedelta(days=1)
                name = babel.dates.format_date(
                    format="MMM d", date=date.replace(tzinfo=pytz.utc).astimezone(local_tz), locale=self._context.get('lang') or 'en_US')
            forecasts = self.env['sale.forecast'].search([
                ('date', '>=', date.strftime('%Y-%m-%d')),
                ('date', '<', date_to.strftime('%Y-%m-%d')),
                ('product_id', '=', product.id),
            ])
            state = 'draft'
            mode = 'auto'
            proc_dec = False
            for f in forecasts:
                if f.mode == 'manual':
                    mode = 'manual'
                if f.state == 'done':
                    state = 'done'
                    proc_dec = True
            demand = sum(forecasts.filtered(lambda x: x.mode == 'auto').mapped('forecast_qty'))
            indirect_total = 0.0
            for day, qty in indirect.items():
                if (day >= date.strftime('%Y-%m-%d')) and (day < date_to.strftime('%Y-%m-%d')):
                    indirect_total += qty
            to_supply = product.mps_forecasted - initial + demand + indirect_total
            to_supply = max(to_supply, product.mps_min_supply)
            if product.mps_max_supply > 0:
                to_supply = min(product.mps_max_supply, to_supply)

            # Need to compute auto and manual separately as forecasts are still important
            if mode == 'manual':
                to_supply = sum(forecasts.filtered(lambda x: x.mode == 'manual').mapped('to_supply'))
            if proc_dec:
                wh = self.env['stock.warehouse'].search([], limit=1)
                loc = wh.lot_stock_id
                purchase_lines = self.env['purchase.order.line'].search([('order_id.picking_type_id.default_location_dest_id', 'child_of', loc.id),
                                                                         ('product_id', '=', product.id),
                                                                         ('state', 'in', ('draft', 'sent', 'to approve')),
                                                                         ('date_planned', '>=', date.strftime('%Y-%m-%d')),
                                                                         ('date_planned', '<', date_to.strftime('%Y-%m-%d'))])
                move_lines = self.env['stock.move'].search([('location_dest_id', 'child_of', loc.id),
                                                            ('product_id', '=', product.id),
                                                            ('state', 'not in', ['done', 'cancel', 'draft']),
                                                            ('location_id.usage', '!=', 'internal'),
                                                            ('date_expected', '>=', date.strftime('%Y-%m-%d')),
                                                            ('date_expected', '<', date_to.strftime('%Y-%m-%d'))])
                to_supply = sum([x.product_uom._compute_quantity(x.product_qty, x.product_id.uom_id) for x in purchase_lines]) + sum([x.product_qty for x in move_lines])
            forecasted = to_supply - demand + initial - indirect_total
            result.append({
                'period': name,
                'date': date.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'initial': initial,
                'demand': demand,
                'mode': mode,
                'state': state,
                'indirect': indirect_total,
                'to_supply': to_supply,
                'forecasted': forecasted,
                'route_type': display,
                'procurement_enable': True if not proc_dec and leadtime >= date else False,
                'procurement_done': proc_dec,
                'lead_time': leadtime.strftime('%Y-%m-%d'),
            })
            initial = forecasted
            date = date_to
        return result

    @api.model
    def get_html(self, domain=None):
        domain = domain or []
        res = self.search([], limit=1)
        if not res:
            res = self.create({})
        domain.append(['mps_active', '=', True])
        rcontext = {
            'products': [
                (x, res.get_data(x))
                for x in self.env['product.product'].search(domain, limit=20)],
            'nb_periods': NUMBER_OF_COLS,
            'company': self.env.user.company_id,
            'format_float': self.env['ir.qweb.field.float'].value_to_html,
        }
        result = {
            'html': self.env.ref('mrp_mps.report_inventory').render(rcontext),
            'report_context': {'nb_periods': NUMBER_OF_COLS,
                               'period': res.period},
        }
        return result


class MMpsLocation(models.Model):
    _name = "mrp.mps.location"

    location_id = fields.Many2one('stock.location', 'Location', required=True)
    active = fields.Boolean('Active', default=True)
