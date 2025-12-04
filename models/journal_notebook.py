from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import random


class JournalNotebook(models.Model):
    """
    Journal Notebook Model

    Organizational container for journal entries.

    Attributes:
        name (Char): Notebook name
        description (Text): Notebook description
        color (Integer): Color for visual identification
        entries_count (Integer): Computed count of entries in notebook
        last_entry_date (Date): Date of most recent entry
    """
    _name = 'journal.notebook'
    _description = 'Journal Notebook'
    _order = 'sequence, name'

    name = fields.Char(string='Notebook Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)

    # EXACTLY THE SAME as tags
    color = fields.Selection(
        selection=[
            ('0', 'Grey'),
            ('1', 'Red'),
            ('2', 'Orange'),
            ('3', 'Yellow'),
            ('4', 'Light Blue'),
            ('5', 'Dark Purple'),
            ('6', 'Salmon Pink'),
            ('7', 'Medium Blue'),
            ('8', 'Dark Blue'),
            ('9', 'Fuchsia'),
            ('10', 'Green'),
            ('11', 'Purple'),
        ],
        string='Color',
        default='0'
    )

    # Relationships
    user_id = fields.Many2one(
        'res.users',
        string='Owner',
        default=lambda self: self.env.user,
        required=True
    )
    entry_ids = fields.One2many('journal.entry', 'notebook_id', string='Entries')

    # Status fields - REMOVED is_public
    active = fields.Boolean(default=True)

    # Computed fields
    entries_count = fields.Integer(
        string='Entries Count',
        compute='_compute_entries_count',
        store=False
    )
    last_entry_date = fields.Date(
        string='Last Entry Date',
        compute='_compute_last_entry_date',
        store=False
    )

    @api.depends('entry_ids')
    def _compute_entries_count(self):
        for notebook in self:
            notebook.entries_count = len(notebook.entry_ids)

    @api.depends('entry_ids.entry_date')
    def _compute_last_entry_date(self):
        for notebook in self:
            if notebook.entry_ids:
                notebook.last_entry_date = max(notebook.entry_ids.mapped('entry_date'))
            else:
                notebook.last_entry_date = False

    @api.constrains('name')
    def _check_name(self):
        for notebook in self:
            if not notebook.name.strip():
                raise ValidationError("Notebook name cannot be empty.")

    # EXACTLY THE SAME as tags - random color on create
    @api.model
    def create(self, vals):
        if 'color' not in vals:
            vals['color'] = str(random.randint(0, 11))
        return super().create(vals)

    # Archive/Unarchive methods (same pattern as tags)
    def action_archive(self):
        """Archive the notebook (soft delete)"""
        return self.write({'active': False})

    def action_unarchive(self):
        """Unarchive the notebook"""
        return self.write({'active': True})

    def action_view_entries(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Entries in "{self.name}"',
            'res_model': 'journal.entry',
            'view_mode': 'tree,form',
            'domain': [('notebook_id', '=', self.id)],
            'context': {'default_notebook_id': self.id},
        }

    def action_delete(self):
        """Delete notebook and all its entries, return to notebooks list"""
        # Get the action to return to notebooks list BEFORE deleting
        action = self.env.ref('journal.action_journal_notebooks').read()[0]

        # Delete all entries in this notebook first
        if self.entry_ids:
            self.entry_ids.unlink()

        # Delete the notebook
        self.unlink()

        # Return to notebooks list page
        return action

    def unlink(self):
        """Override unlink to prevent deletion if there are entries (should be handled by action_delete)"""
        # Check if there are any entries left (should have been deleted by action_delete)
        for notebook in self:
            if notebook.entry_ids:
                raise UserError(
                    "Cannot delete notebook that still has entries. Use the 'Delete Notebook' button instead.")

        return super().unlink()