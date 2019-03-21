# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = 'stock.move'

    product_brand = fields.Char(
        related='product_id.product_brand_id.name',
        string='Brand',
        readonly=True,
        store=True)
    product_default_code = fields.Char(
        related='product_id.default_code',
        string='Default code',
        readonly=True,
        store=True)
    mrp_date = fields.Datetime(
        compute='_compute_mrp_date',
        string='Date Planned',
        search='_search_date_planned',
        readonly=True,
        store=False)
    lotes = fields.Char(
        compute='_compute_lote',
        string='Lots',
        readonly=True,
        store=False)

    def _compute_mrp_date(self):
        for move in self.mapped('raw_material_production_id'):
            move.move_raw_ids.update({'mrp_date': move.date_planned_start})

    @api.multi
    def _search_date_planned(self, operator, value):
        model_mrp_production = self.env['mrp.production']
        moves = model_mrp_production.search(
            [('date_planned_start', operator, value)])
        list_ids = moves.mapped('move_raw_ids.id')
        return [('id', 'in', list_ids)]

    def _compute_lote(self):
        for moves in self.filtered('move_line_ids.lot_id'):
            lots = ""
            for move in moves.mapped('move_line_ids').filtered('product_qty'):
                lots += '%s  %s,' % (move.lot_id.name or '', move.product_qty)
            moves.lotes = lots
