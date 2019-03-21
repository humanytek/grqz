# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import OrderedDict
from odoo import api, models
_logger = logging.getLogger(__name__)


class ProductSupply(models.AbstractModel):
    _name = 'report.product_supply.report_product_supply'

    @api.model
    def get_report_values(self, docids, data=None):
        docids = data['extra_data']['ids']
        model_stock_move = self.env['stock.move']
        docs = model_stock_move.browse(docids)
        data['extra_data']['moves'] = {b: OrderedDict(
            sorted(v.items(), key=lambda x: x[0])) for b, v in data[
                'extra_data']['moves'].items()}
        return {
            'doc_ids': docids,
            'docs': docs,
            'data': data['extra_data'],
            'env': self.env
        }
