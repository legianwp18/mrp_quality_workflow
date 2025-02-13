# Manufacturing Quality Workflow

This module integrates quality control workflows into the manufacturing process in Odoo 17.

## Features

- Automatic generation of quality checkpoints for manufacturing orders
- Real-time validation of quality checks
- Dynamic status updates based on quality results
- PDF reports for quality checks
- Integration with manufacturing order workflow

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the module from the Apps menu
4. Configure quality check templates for your products

## Configuration

### Quality Check Templates

1. Go to Manufacturing > Products > Products
2. Open a product and go to the Quality tab
3. Add quality check templates with:
   - Check name
   - Check type (Visual/Measurement)
   - Expected values and tolerances

### User Access Rights

The module adds the following access groups:
- Quality User: Can perform quality checks
- Quality Manager: Can manage quality templates and review results

## Usage

### Creating Quality Checks

Quality checks are automatically generated when:
1. A manufacturing order is confirmed
2. Based on the product's quality templates

### Performing Quality Checks

1. Open a manufacturing order
2. Go to the Quality Checks tab
3. Input measurement values or inspection results
4. System validates inputs against defined tolerances
5. Manufacturing order status updates based on results
6. Clicks "Confirm" button to submit the quality check (User QC)
7. Clicks "Validate" button to provide final approval (Manager QC)

### Generating Reports

1. Open a manufacturing order
2. Click "Quality Control Report" button
3. Download the PDF report showing all quality checks

## Testing

### Automated Tests

Run the tests using:
```bash
python3 odoo-bin -i mrp_quality_workflow -d your_database --test-enable --test-tags=mrp_quality_workflow:
```

### Manual Testing Scenarios

1. Quality Check Generation
   - Create a new manufacturing order
   - Confirm the order
   - Verify quality checks are generated

2. Validation Testing
   - Input values within tolerance
   - Input values outside tolerance
   - Verify error messages
   - Check status updates

3. Report Testing
   - Complete quality checks
   - Generate report
   - Verify all data is present

## Troubleshooting

Common issues and solutions:

1. Quality checks not generating
   - Verify product has quality templates
   - Check user permissions

2. Validation errors
   - Verify tolerance ranges
   - Check measurement units

3. Report issues
   - Clear browser cache
   - Update module if needed

## Support

For bugs or feature requests, please create an issue in the repository.

## License

This module is published under the GNU LGPL v3 license.