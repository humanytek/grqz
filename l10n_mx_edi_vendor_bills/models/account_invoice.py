# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from codecs import BOM_UTF8
import requests

from lxml import objectify
from werkzeug import url_encode

from odoo import _, api, models
from odoo.tools.float_utils import float_repr

BOM_UTF8U = BOM_UTF8.decode('UTF-8')
CFDI_SAT_QR_STATE = {
    'No Encontrado': 'not_found',
    'Cancelado': 'cancelled',
    'Vigente': 'valid',
}


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def generate_xml_attachment(self):
        self.ensure_one()
        if not self.l10n_mx_edi_cfdi:
            return False
        fname = ("%s-%s-MX-Bill-%s.xml" % (
            self.journal_id.code, self.reference,
            self.company_id.partner_id.vat or '')).replace('/', '')
        data_attach = {
            'name': fname,
            'datas': base64.encodebytes(
                self.l10n_mx_edi_cfdi and
                self.l10n_mx_edi_cfdi.lstrip(BOM_UTF8U).encode('UTF-8') or ''),
            'datas_fname': fname,
            'description': _('XML signed from Invoice %s.') % self.number,
            'res_model': self._name,
            'res_id': self.id,
        }
        self.l10n_mx_edi_cfdi_name = fname
        return self.env['ir.attachment'].with_context({}).create(data_attach)

    @api.multi
    def l10n_mx_edi_update_sat_status(self):
        res = super(AccountInvoice, self).l10n_mx_edi_update_sat_status()
        url = 'https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl'  # noqa
        headers = {'SOAPAction':
                   'http://tempuri.org/IConsultaCFDIService/Consulta',
                   'Content-Type': 'text/xml; charset=utf-8'}
        template = """<?xml version="1.0" encoding="UTF-8"?>
                      <SOAP-ENV:Envelope xmlns:ns0="http://tempuri.org/"
                       xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
                       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
                      <SOAP-ENV:Header/>
                      <ns1:Body>
                      <ns0:Consulta>
                          <ns0:expresionImpresa>?%s</ns0:expresionImpresa>
                      </ns0:Consulta>
                      </ns1:Body>
                      </SOAP-ENV:Envelope>"""
        namespace = {'a': 'http://schemas.datacontract.org/2004/07/'
                     'Sat.Cfdi.Negocio.ConsultaCfdi.Servicio'}

        for inv in self.filtered(lambda r: r.type == 'in_invoice' and
                                 r.l10n_mx_edi_cfdi_uuid):
            supplier_rfc = inv.l10n_mx_edi_cfdi_supplier_rfc
            customer_rfc = inv.l10n_mx_edi_cfdi_customer_rfc
            total = float_repr(inv.l10n_mx_edi_cfdi_amount,
                               precision_digits=inv.currency_id.decimal_places)
            uuid = inv.l10n_mx_edi_cfdi_uuid
            params = url_encode({
                're': supplier_rfc,
                'rr': customer_rfc,
                'tt': total,
                'id': uuid}, separator='&amp;')
            soap_env = template % (params)
            try:
                soap_xml = requests.post(url, data=soap_env, headers=headers)
                response = objectify.fromstring(soap_xml.text)
                status = response.xpath('//a:Estado', namespaces=namespace)
            except BaseException as e:
                inv.l10n_mx_edi_log_error(str(e))
                continue
            inv.l10n_mx_edi_sat_status = CFDI_SAT_QR_STATE.get(
                status[0] if status else False, 'none')
        return res
