from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import random


class JournalTag(models.Model):
    """
    Journal Tag Model

    Categorization tags for journal entries with color coding.

    Attributes:
        name (Char): Tag name
        color (Integer): Color index for display
        active (Boolean): Whether tag is active
        entries_count (Integer): Computed count of associated entries
    """
    _name = 'journal.tag'
    _description = 'Journal Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
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
    active = fields.Boolean(default=True)

    # Relationships
    entry_ids = fields.Many2many('journal.entry', string='Entries')
    entries_count = fields.Integer(
        string='Entries Count',
        compute='_compute_entries_count',
        store=False
    )

    # Computed fields
    @api.depends('entry_ids')
    def _compute_entries_count(self):
        for tag in self:
            tag.entries_count = len(tag.entry_ids)

    @api.constrains('name')
    def _check_name(self):
        for tag in self:
            if not tag.name.strip():
                raise ValidationError("Tag name cannot be empty.")

    @api.model
    def create(self, vals):
        if 'color' not in vals:
            vals['color'] = str(random.randint(0, 11))
        return super().create(vals)

    def action_view_entries(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Entries tagged "{self.name}"',
            'res_model': 'journal.entry',
            'view_mode': 'tree,form',
            'domain': [('tag_ids', 'in', self.ids)],
        }

    def action_delete(self):
        """PERMANENTLY delete tags and remove references from entries"""
        # Get the action to return to tags list BEFORE deleting
        action = self.env.ref('journal.action_journal_tags').read()[0]

        # Remove this tag from all entries BEFORE deleting
        for tag in self:
            if tag.entry_ids:
                tag.entry_ids.write({'tag_ids': [(3, tag.id)]})

        # PERMANENTLY delete the tags
        self.unlink()

        # Return to tags list page
        return action

    def action_archive(self):
        """Archive the tag (soft delete) - tags remain in database but inactive"""
        for tag in self:
            # Remove tag from entries when archiving
            if tag.entry_ids:
                tag.entry_ids.write({'tag_ids': [(3, tag.id)]})

        # Archive the tags (set active=False)
        return self.write({'active': False})

    def action_unarchive(self):
        """Unarchive the tag"""
        return self.write({'active': True})