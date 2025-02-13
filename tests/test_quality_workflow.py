# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestQualityWorkflow(TransactionCase):

    def setUp(self):
        super(TestQualityWorkflow, self).setUp()

        # Create test product with quality templates
        self.test_product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
        })

        # Create quality checkpoint template
        self.checkpoint_template = self.env['quality.checkpoint.template'].create({
            'name': 'Dimension Check',
            'product_tmpl_id': self.test_product.product_tmpl_id.id,
            'check_type': 'measurement',
            'target_value': 100.0,
            'tolerance_range': 2.0,
        })

        # Create manufacturing order
        self.mo = self.env['mrp.production'].create({
            'product_id': self.test_product.id,
            'product_qty': 1.0,
            'product_uom_id': self.test_product.uom_id.id,
        })

    def test_01_checkpoint_generation(self):
        """Test automatic generation of quality checkpoints"""
        self.mo.action_confirm()

        self.assertTrue(self.mo.quality_check_ids, "Quality checks should be generated")
        self.assertEqual(len(self.mo.quality_check_ids), 1, "Should have one quality check from template")

        check = self.mo.quality_check_ids[0]
        self.assertEqual(check.name, 'Dimension Check', "Check name should match template")
        self.assertEqual(check.check_type, 'measurement', "Check type should match template")

    def test_02_validation_logic(self):
        """Test quality check validation logic"""
        self.mo.action_confirm()
        check = self.mo.quality_check_ids[0]

        # Test value within tolerance
        check.measured_value = 101.0
        check._onchange_measured_value()
        self.assertEqual(check.state, 'passed', "Check should pass when within tolerance")

        # Test value outside tolerance
        check.measured_value = 103.0
        check._onchange_measured_value()
        self.assertEqual(check.state, 'failed', "Check should fail when outside tolerance")

        # Test validation without value
        check.measured_value = False
        with self.assertRaises(ValidationError):
            check.action_confirm()

    def test_03_mo_status_updates(self):
        """Test MO status updates based on quality checks"""
        self.mo.action_confirm()

        self.assertEqual(self.mo.quality_state, 'in_progress', "Initial state should be pending")

        # Pass the check
        check = self.mo.quality_check_ids[0]
        check.measured_value = 101.0
        check.action_confirm()

        self.assertEqual(self.mo.quality_state, 'passed', "MO should be passed when all checks pass")

        # Fail the check
        check.measured_value = 103.0

        self.assertEqual(self.mo.quality_state, 'failed', "Check should fail when outside tolerance")

        with self.assertRaises(UserError):
            check.action_confirm()

        self.assertEqual(self.mo.state, 'on_hold', "MO should be on hold when check fails")

    def test_04_mo_completion_validation(self):
        """Test MO completion validation"""
        self.mo.action_confirm()

        # Try to complete MO with failed check
        check = self.mo.quality_check_ids[0]
        check.measured_value = 103.0

        with self.assertRaises(UserError):
            check.action_confirm()

        # Pass the check and try again
        self.mo.action_revalidate_quality()
        check.measured_value = 101.0
        check.action_confirm()
        check.action_validate()

        # Should not raise error
        self.mo.button_mark_done()

    def test_05_report_generation(self):
        """Test quality report generation"""
        self.mo.action_confirm()
        check = self.mo.quality_check_ids[0]
        check.measured_value = 101.0
        check.action_confirm()
        check.action_validate()
        self.mo.button_mark_done()

        test_record_report = self.env['ir.actions.report']._render_qweb_pdf('mrp_quality_workflow.report_quality_check', res_ids=self.mo.id)
        self.assertTrue(test_record_report, "The PDF should have been generated")
        self.assertGreater(len(test_record_report), 0, "Report should have content")