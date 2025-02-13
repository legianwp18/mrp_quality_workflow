from odoo import models, api

class QualityCheckReport(models.AbstractModel):
    _name = 'report.mrp_quality_workflow.report_quality_check'
    _description = 'Quality Check Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }