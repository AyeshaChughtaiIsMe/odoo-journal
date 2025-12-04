from odoo import models, fields, api
from odoo.tools import html2plaintext
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class JournalEntryVersion(models.Model):
    """
    Journal Entry Version History Model

    Stores historical versions of journal entries for tracking changes over time.
    Each time a journal entry's content is modified, a new version record is created
    preserving the previous state. This enables version control and content restoration.

    Key Features:
    - Automatic version numbering
    - Content preview generation
    - Human-readable timestamps
    - Version comparison capabilities
    - Restoration functionality

    Database Constraints:
    - Ensures unique version numbers per journal entry
    - Cascading deletion when parent entry is deleted

    Attributes:
        entry_id (Many2one): Reference to parent Journal Entry
        created_by (Many2one): User who created this version
        version_number (Integer): Sequential version identifier
        content (Html): Full HTML content at this version
        word_count (Integer): Word count at this version
        char_count (Integer): Character count at this version
        create_date (Datetime): Automatic timestamp of version creation
        preview (Text): Computed text preview (first 100 chars)
        time_ago (Char): Computed human-readable time difference

    Methods:
        _compute_preview(): Generates text preview from HTML content
        _compute_time_ago(): Calculates "time ago" string from create_date
        action_view_content(): Opens version in read-only dialog
        action_restore(): Restores this version as current content
        action_compare_with_current(): Compares with current entry version
        action_compare_with_version(): Compares with another version
    """
    _name = 'journal.entry.version'
    _description = 'Journal Entry Version History'
    _order = 'version_number desc'
    _rec_name = 'version_number'

    # Relationships
    entry_id = fields.Many2one(
        'journal.entry',
        string='Journal Entry',
        required=True,
        ondelete='cascade'
    )
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        required=True,
        default=lambda self: self.env.user
    )

    # Version fields
    version_number = fields.Integer(string='Version', required=True)
    content = fields.Html(string='Content', sanitize_attributes=False, strip_classes=False)
    word_count = fields.Integer(string='Word Count')
    char_count = fields.Integer(string='Character Count')

    # Timestamp
    create_date = fields.Datetime(string='Created On', readonly=True)

    # Computed fields
    preview = fields.Text(string='Preview', compute='_compute_preview')
    time_ago = fields.Char(string='Time Ago', compute='_compute_time_ago')

    @api.depends('content')
    def _compute_preview(self):
        """Generate a text preview of the content"""
        for record in self:
            if record.content:
                # Convert HTML to plain text and take first 100 chars
                plain_text = html2plaintext(record.content)
                record.preview = (plain_text[:100] + '...') if len(plain_text) > 100 else plain_text
            else:
                record.preview = ''

    @api.depends('create_date')
    def _compute_time_ago(self):
        """Compute human-readable time ago"""
        for record in self:
            if record.create_date:
                # Simple time ago calculation
                now = datetime.now()
                create_date = fields.Datetime.from_string(record.create_date)
                diff = now - create_date

                if diff.days > 0:
                    record.time_ago = f"{diff.days} days ago"
                elif diff.seconds >= 3600:
                    hours = diff.seconds // 3600
                    record.time_ago = f"{hours} hours ago"
                elif diff.seconds >= 60:
                    minutes = diff.seconds // 60
                    record.time_ago = f"{minutes} minutes ago"
                else:
                    record.time_ago = "Just now"
            else:
                record.time_ago = ''

    # Action methods
    def action_view_content(self):
        """Open version content in a dialog"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Version {self.version_number}',
            'res_model': 'journal.entry.version',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('journal.view_journal_entry_version_form').id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }

    def action_restore(self):
        """Restore this version"""
        self.ensure_one()
        return self.entry_id.action_restore_version(self.id)

    def action_compare_with_current(self):
        """Compare this version with current version"""
        self.ensure_one()
        # Compare with current entry content
        return {
            'type': 'ir.actions.act_url',
            'url': f'/journal/compare/{self.entry_id.id}/{self.id}/current',
            'target': 'new',
        }

    def action_compare_with_version(self, other_version_id):
        """Compare this version with another version"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/journal/compare/{self.entry_id.id}/{self.id}/{other_version_id}',
            'target': 'new',
        }

    # Constraints
    _sql_constraints = [
        ('unique_version_per_entry', 'UNIQUE(entry_id, version_number)', 'Version number must be unique per entry.'),
    ]