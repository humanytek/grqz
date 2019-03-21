# Copyright 2018 Vauxoo.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleBrand(models.AbstractModel):
    _name = 'sale.brand'

    brand = fields.Char(compute='_compute_brand_id',
                        search='_search_brand',
                        readonly=True,
                        help='Product Brand')

    @api.multi
    def _compute_brand_id(self):
        model_line = {'sale.order': 'order_line',
                      'account.invoice': 'invoice_line_ids'}
        for record in self:
            line = record.mapped(model_line[self._name])
            if line and line[0].product_id.product_brand_id: # noqa
                record.brand = line[0].product_id.product_brand_id.name # noqa

    @api.multi
    def _search_brand(self, operator, value):
        list_ids = []
        compare = {
            '=': lambda a, b: a == b,
            '!=': lambda a, b: a != b
        }
        model_line = {'sale.order': 'order_line',
                      'account.invoice': 'invoice_line_ids'}
        for doc in self.search([]):
            lines = doc.mapped(model_line[self._name]).filtered(
                lambda a: a.product_id.product_brand_id)
            for line in lines:
                brand = line.product_id.product_brand_id.name
                if compare.get(operator, lambda a, b: False)(brand, value):
                    list_ids.append(doc.id)
        return [('id', 'in', list_ids)]
