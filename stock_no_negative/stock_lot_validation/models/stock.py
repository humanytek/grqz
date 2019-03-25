# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models, _
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_show_details(self):
        stock_lot_ids = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id),
             ('location_id', '=', self.location_id.id)]).ids
        self.env.context = {'stock_lot_ids': stock_lot_ids}
        return super(StockMove, self).action_show_details()


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # pylint: disable=access-member-before-definition
    @api.onchange('lot_id', 'qty_done')
    def onchange_lot(self):
        res = {}
        location = self.location_id
        if location.usage == 'supplier':
            return res
        if self.lot_id and self.qty_done > 0:
            quants = self.lot_id.quant_ids.filtered(
                lambda q: q.product_id.id == self.product_id.id and
                (q.location_id.id == location.id or
                 location.id in [value.id for value in
                                 q.location_id.child_ids]))
            qty_total = sum(quant.quantity for quant in quants) or 0
            if self.qty_done > qty_total:
                self.qty_done = 0
                message = "You have no stock on this lot"
                res['warning'] = {'title': _('Warning'),
                                  'message': _(message)}
        return res
