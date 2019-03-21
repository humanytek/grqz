# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class StockKardex(models.TransientModel):
    _name = "stock.kardex"

    @api.multi
    def calculate(self):
        model_stock_move = self.env['stock.move']
        model_stock_kardex_detail = self.env['stock.kardex.detail']
        qty = 0
        moves = model_stock_move.search(
            [('product_id.id', '=', self.product_id.id),
             ('date', '>=', self.date_start),
             ('date', '<=', self.date_end),
             ('state', '=', 'done'),
             '|',
             ('location_id', '=', self.location_id.id),
             ('location_dest_id', '=', self.location_id.id)], order='date')

        moves_ini = model_stock_move.search(
            [('product_id.id', '=', self.product_id.id),
             ('date', '<', self.date_start),
             ('state', '=', 'done'),
             '|',
             ('location_id', '=', self.location_id.id),
             ('location_dest_id', '=', self.location_id.id)])

        val = {True: 1, False: -1}
        qty = sum([move.product_uom_qty * val[
            self.location_id.id == move.location_id.id] for
            move in moves_ini])

        stock_moves_reserved = model_stock_move.search(
            [('product_id.id', '=', self.product_id.id),
             ('date', '>=', self.date_start),
             ('date', '<=', self.date_end),
             ('state', 'in', ['assigned', 'confirmed',
                              'partially_available']),
             ('location_id', '=', self.location_id.id)], order='date')

        qty_reserve = sum([moves_reserved.reserved_availability for
                           moves_reserved in stock_moves_reserved])

        qty_ini = qty
        model_stock_kardex_detail.search([]).unlink()
        for move in moves.filtered(lambda a:
                                   a.location_id.id != a.location_dest_id.id):
            product_incomming = 0
            product_outgoing = 0
            val = {True: -1, False: 1}
            product_move = {True: move.product_uom_qty, False: 0}
            qty += (move.product_uom_qty * val[
                self.location_id.id == move.location_id.id])
            product_outgoing = product_move[
                self.location_id.id == move.location_id.id]
            product_incomming = product_move[
                self.location_id.id != move.location_id.id]

            model_stock_kardex_detail.create(
                {'stock_move_id': move.id,
                    'product_id': self.product_id.id,
                    'stock_kardex_id': self.id,
                    'qty_product': qty,
                    'product_incomming': product_incomming,
                    'product_outgoing': product_outgoing})
        self.write({'stock_end': qty, 'qty_reserve': qty_reserve,
                    'stock_start': qty_ini})

        return {'type': 'ir.actions.act_window',
                'res_model': 'stock.kardex',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
                }

    @api.model
    def _get_default_location_id(self):
        location = self.env.ref('stock.stock_location_stock',
                                raise_if_not_found=False)
        return location.id if location else False

    product_id = fields.Many2one('product.product', 'Product', required=True)
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        default=_get_default_location_id)
    date_start = fields.Datetime('Start Date', required=True)
    date_end = fields.Datetime('End Date', required=True)
    stock_start = fields.Float('Starting stock', readonly=True)
    stock_end = fields.Float('Ending stock', readonly=True,)
    qty_reserve = fields.Float('Total Reserved Product', readonly=True,)
    stock_kardex_detail_ids = fields.One2many(
        'stock.kardex.detail',
        'stock_kardex_id',
        string='Detail')


class StockKardexDetail(models.TransientModel):
    _name = "stock.kardex.detail"

    stock_kardex_id = fields.Many2one('stock.kardex', 'Kardex')
    stock_move_id = fields.Many2one('stock.move', 'Move', readonly=True)
    qty_product = fields.Float('Quantity Total', readonly=True)
    product_incomming = fields.Float('Incoming Products', readonly=True)
    product_outgoing = fields.Float('Outgoing Products', readonly=True)
    move_qty_product = fields.Float(
        related='stock_move_id.product_uom_qty',
        string='Quantity',
        readonly=True,
        store=False)
    move_date = fields.Datetime(
        related='stock_move_id.date',
        string='Date',
        readonly=True,
        store=False)
    location_id = fields.Many2one(
        related='stock_move_id.location_id',
        string='Source Location',
        readonly=True, store=False)
    location_dest_id = fields.Many2one(
        related='stock_move_id.location_dest_id',
        string='Destination Location',
        readonly=True, store=False)
