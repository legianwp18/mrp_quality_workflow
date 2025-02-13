from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    quality_check_ids = fields.One2many('mrp.quality.checkpoint', 'production_id', string='Quality Checks')
    state = fields.Selection(selection_add=[
        ('on_hold', 'On Hold')
    ])
    quality_state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    ], string='Quality Status', compute='_compute_quality_state', store=True)
    require_revalidation = fields.Boolean('Require Revalidation', default=False, copy=False)
    last_state = fields.Char(string='Last State')

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for production in self:
            production._create_quality_checkpoints()
        return res

    def _create_quality_checkpoints(self):
        QualityCheckpoint = self.env['mrp.quality.checkpoint']
        for production in self:
            for template in production.product_id.quality_checkpoint_template_ids:
                QualityCheckpoint.create({
                    'name': template.name,
                    'production_id': production.id,
                    'check_type': template.check_type,
                    'tolerance_range': template.tolerance_range,
                    'target_value': template.target_value,
                })

    def button_mark_done(self):
        for production in self:
            if production.state == 'on_hold':
                raise UserError(_('Cannot complete manufacturing order while on hold.'))
            if production.quality_state != 'passed':
                raise UserError(_('Cannot complete manufacturing order until all quality checks are passed.'))
            if any(check.approval_state != 'validate' for check in production.quality_check_ids):
                raise UserError(_('Cannot complete manufacturing order until quality all approval status are approved.'))
        return super(MrpProduction, self).button_mark_done()

    @api.depends('quality_check_ids.state', 'quality_check_ids.measured_value')
    def _compute_quality_state(self):
        for production in self:
            if not production.quality_check_ids:
                production.quality_state = 'pending'
            elif any(check.state == 'failed' for check in production.quality_check_ids):
                production.quality_state = 'failed'
            elif all(check.state == 'passed' for check in production.quality_check_ids):
                production.quality_state = 'passed'
            else:
                production.quality_state = 'in_progress'

    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity', 'move_finished_ids.state',
        'workorder_ids.state', 'product_qty', 'qty_producing', 'move_raw_ids.picked', 
        'quality_check_ids.state', 'quality_check_ids.measured_value')
    def _compute_state(self):
        for production in self:
            if production.quality_state == 'failed' and production.state not in ('done', 'cancel'):
                production.last_state = production.state
                production.require_revalidation = True
                production.state = 'on_hold'
                result = self
            else:
                if production.require_revalidation:
                    production.require_revalidation = False
                    production.state = production.last_state
                result = super(MrpProduction, self)._compute_state()
        return result

    def action_revalidate_quality(self):
        self.ensure_one()
        if not self.require_revalidation:
            raise UserError(_('This order does not require revalidation.'))

        failed_checks = self.quality_check_ids.filtered(lambda x: x.state == 'failed')
        failed_checks.write({
            'state': 'pending',
            'measured_value': False,
        })

        self.write({
            'quality_state': 'in_progress',
            'require_revalidation': False
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Quality Revalidation'),
            'res_model': 'mrp.production',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }