# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = 'stock.move'

    compromise_qty_move = fields.Float('Compromise',
                                       compute='_compute_compromise_qty_move',
                                       readonly=True, help="Amount committed")

    @api.multi
    def _compute_compromise_qty_move(self):
        product_compromise_obj = self.env['product.compromise']
        for record in self:
            commited_products = product_compromise_obj.search([
                ('stock_move_in_id.id', '=', record.id),
                ('state', '=', 'assigned')])
            record.compromise_qty_move = sum([prod_compromise.qty_compromise
                                              for prod_compromise in
                                              commited_products])
