# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    brand = fields.Char(readonly=True, help="Product Brand")
    invoice = fields.Char(readonly=True, help="Invoice")

    def _from(self):
        from_str = super(AccountInvoiceReport, self)._from()
        from_str += """
        left JOIN product_brand pb ON pb.id = pt.product_brand_id
        """
        return from_str

    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        group_by_str += """
        , pb.name, ai.number
        """
        return group_by_str

    def _sub_select(self):
        sub_select_str = super(AccountInvoiceReport, self)._sub_select()
        sub_select_str += """
        , pb.name as brand, ai.number AS invoice
        """
        return sub_select_str

    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += """
        , sub.brand, sub.invoice
        """
        return select_str
