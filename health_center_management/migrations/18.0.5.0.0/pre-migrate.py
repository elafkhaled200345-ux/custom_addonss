# -*- coding: utf-8 -*-
# Pre-migration script for health_center_management v5 → v6
# Cleans up stale ir.model.fields.selection records that cause:
# AttributeError: 'Float' object has no attribute 'ondelete'

import logging
_logger = logging.getLogger(__name__)

# Models where field types changed from Selection to Char/other
MODELS_TO_CLEAN = [
    ('health.clinic', 'name'),
    ('health.clinic', 'clinic_type'),
    ('health.patient', 'gender'),
    ('health.doctor', 'specialization'),
]

def migrate(cr, version):
    if not version:
        # Fresh install — nothing to clean
        return

    _logger.info('health_center_management: Running pre-migration cleanup...')

    for model, field_name in MODELS_TO_CLEAN:
        cr.execute("""
            DELETE FROM ir_model_fields_selection
            WHERE field_id IN (
                SELECT id FROM ir_model_fields
                WHERE model = %s AND name = %s
            )
        """, (model, field_name))
        deleted = cr.rowcount
        if deleted:
            _logger.info(
                'Cleaned %d stale selection values for %s.%s',
                deleted, model, field_name
            )

    # Also clean any orphaned selection values for this module
    cr.execute("""
        DELETE FROM ir_model_fields_selection
        WHERE field_id IN (
            SELECT f.id FROM ir_model_fields f
            JOIN ir_model m ON m.id = f.model_id
            WHERE m.model LIKE 'health.%%'
            AND f.ttype != 'selection'
        )
    """)
    deleted = cr.rowcount
    if deleted:
        _logger.info(
            'Cleaned %d orphaned selection values from health.* models',
            deleted
        )

    _logger.info('health_center_management: Pre-migration cleanup done.')
