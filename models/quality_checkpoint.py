from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class QualityCheckpoint(models.Model):
    _name = 'mrp.quality.checkpoint'
    _description = 'Manufacturing Quality Checkpoint'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=True, ondelete='cascade')
    check_type = fields.Selection([
        ('visual', 'Visual Inspection'),
        ('measurement', 'Measurement'),
        ('functional', 'Functional Test')
    ], string='Check Type', required=True)
    tolerance_range = fields.Float('Tolerance Range (±)')
    target_value = fields.Float('Target Value')
    measured_value = fields.Float('Measured Value', copy='False')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    ], string='Status', compute='_onchange_measured_value', store=True)
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Waiting Approval'),
        ('validate', 'Approved'),
    ], string='Approval Status', default='draft', copy='False')
    notes = fields.Text('Notes')
    checked_by = fields.Many2one('res.users', string='Checked By', copy='False')
    check_date = fields.Datetime('Check Date', copy='False')
    approved_by = fields.Many2one('res.users', string='Approved By', copy='False')
    approval_date = fields.Datetime('Approval Date', copy='False')

    @api.depends('measured_value')
    def _onchange_measured_value(self):
        for check in self:
            if check.measured_value and check.measured_value != 0:
                if abs(check.measured_value - check.target_value) <= check.tolerance_range:
                    check.state = 'passed'
                else:
                    check.state = 'failed'
            else:
                check.state = 'pending'

    def action_confirm(self):
        self.ensure_one()
        if not self.measured_value:
            raise ValidationError(_('Please enter the measured value before validation.'))

        if self.state != 'passed':
            raise UserError(_('Cannot confirm until quality checks are passed.'))

        self.write({
            'approval_state': 'confirm',
            'check_date': fields.Datetime.now(),
            'checked_by': self.env.user.id,
        })
        self.production_id._compute_quality_state()
        self.production_id._compute_state()

    def action_validate(self):
        self.ensure_one()
        if not self.measured_value:
            raise ValidationError(_('Please enter the measured value before validation.'))

        if self.state != 'passed':
            raise UserError(_('Cannot confirm until quality checks are passed.'))

        self.write({
            'approval_state': 'validate',
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        })


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quality_checkpoint_template_ids = fields.One2many(
        'quality.checkpoint.template', 'product_tmpl_id',
        string='Quality Checkpoint Templates')


class QualityCheckpointTemplate(models.Model):
    _name = 'quality.checkpoint.template'
    _description = 'Quality Checkpoint Template'

    name = fields.Char('Name', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', required=True, ondelete='cascade')
    check_type = fields.Selection([
        ('visual', 'Visual Inspection'),
        ('measurement', 'Measurement'),
        ('functional', 'Functional Test')
    ], string='Check Type', required=True)
    tolerance_range = fields.Float('Tolerance Range (±)')
    target_value = fields.Float('Target Value')
    sequence = fields.Integer('Sequence', default=10)