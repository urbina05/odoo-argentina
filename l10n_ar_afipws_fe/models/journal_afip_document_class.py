# -*- coding: utf-8 -*-
from openerp import models, api, _
import logging

_logger = logging.getLogger(__name__)


class account_journal_afip_document_class(models.Model):
    _inherit = "account.journal.afip_document_class"

    @api.multi
    def get_pyafipws_last_invoice(self):
        self.ensure_one()
        document_class = self.afip_document_class_id.afip_code
        point_of_sale = self.journal_id.point_of_sale_id
        company = point_of_sale.company_id
        afip_ws = point_of_sale.afip_ws
        self.ensure_one()

        if not afip_ws:
            raise Warning(_('No AFIP WS selected on point of sale %s') % (
                point_of_sale.name))
        ws = company.get_connection(afip_ws).connect()
        # call the webservice method to get the last invoice at AFIP:
        if afip_ws in ("wsfe", "wsmtxca"):
            last = ws.CompUltimoAutorizado(
                document_class, point_of_sale.number)
        elif afip_ws == "wsfex":
            last = ws.GetLastCMP(
                document_class, point_of_sale.number)
        else:
            raise Warning(_('AFIP WS %s not implemented') % afip_ws)
        msg = " - ".join([ws.Excepcion, ws.ErrMsg, ws.Obs])
        return {
            'type': 'ir.actions.act_window.message',
            'title': _('Last Invoice %s' % last),
            'message': msg,
            }

    @api.one
    def update_afip_data(self):
        self.get_afip_items_generated()
        self._get_afip_state()
        self.afip_connection_id.server_id.wsfe_update_tax(
            self.afip_connection_id.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: