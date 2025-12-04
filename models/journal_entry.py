from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
import re
import html as html_parser
import logging
import string

_logger = logging.getLogger(__name__)


class JournalEntry(models.Model):
    """
    Journal Entry Model

    Represents a single journal entry with comprehensive tracking capabilities.
    Includes versioning, mood tracking, and content analysis.

    Attributes:
        name (Char): Title of the journal entry
        content (Html): Main content of the entry
        state (Selection): Current state - draft, published, or archived
        mood (Selection): Emotional state when writing
        word_count (Integer): Computed word count of content
        versions_count (Integer): Number of versions saved
        is_favorite (Boolean): Whether entry is marked as favorite

    Methods:
        action_publish(): Publish a draft entry
        action_draft(): Return published entry to draft
        action_archive(): Archive an entry
        action_toggle_favorite(): Toggle favorite status
        _compute_word_count(): Compute word count from content
    """
    _name = 'journal.entry'
    _description = 'Journal Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'entry_date desc, write_date desc'
    _rec_name = 'name'

    # Basic fields
    name = fields.Char(string='Title', required=True, tracking=True)
    content = fields.Html(string='Content', sanitize_attributes=False, strip_classes=False)

    # Relationships
    notebook_id = fields.Many2one(
        'journal.notebook',
        string='Notebook',
        required=True,
        tracking=True,
        domain="[('user_id', '=', user_id)]",
        ondelete='cascade'
    )
    tag_ids = fields.Many2many('journal.tag', string='Tags')
    user_id = fields.Many2one(
        'res.users',
        string='Author',
        default=lambda self: self.env.user,
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    # Date fields
    entry_date = fields.Date(
        string='Entry Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    create_date = fields.Datetime(string='Created On', readonly=True)
    write_date = fields.Datetime(string='Last Updated', readonly=True)

    # Status fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', tracking=True)

    # Technical fields
    word_count = fields.Integer(string='Word Count', compute='_compute_word_count', store=True)
    char_count = fields.Integer(string='Character Count', compute='_compute_word_count', store=True)
    is_favorite = fields.Boolean(string='Favorite')
    mood = fields.Selection([
        ('happy', '😊 Happy'),
        ('sad', '😢 Sad'),
        ('excited', '😃 Excited'),
        ('angry', '😠 Angry'),
        ('peaceful', '😌 Peaceful'),
        ('anxious', '😰 Anxious'),
        ('grateful', '🙏 Grateful'),
        ('tired', '😴 Tired'),
    ], string='Mood', tracking=True)

    # Version fields
    current_version = fields.Integer(string='Current Version', default=1, readonly=True)
    version_ids = fields.One2many('journal.entry.version', 'entry_id', string='Versions', readonly=True)
    versions_count = fields.Integer(string='Versions Count', compute='_compute_versions_count', store=True)

    # Full-text search fields
    search_vector = fields.Text(
        string='Search Vector',
        compute='_compute_search_vector',
        store=True,
        prefetch=False
    )

    @api.depends('version_ids')
    def _compute_versions_count(self):
        for record in self:
            record.versions_count = len(record.version_ids)

    @api.depends('name', 'content', 'tag_ids.name', 'notebook_id.name', 'mood')
    def _compute_search_vector(self):
        """Compute search vector for full-text search"""
        for record in self:
            search_parts = []

            # Add title
            if record.name:
                search_parts.append(record.name.lower())

            # Add content (strip HTML tags)
            if record.content:
                # Remove HTML tags from content
                text_content = re.sub(r'<[^>]+>', ' ', record.content)
                text_content = html_parser.unescape(text_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                if text_content:
                    search_parts.append(text_content.lower())

            # Add tags
            if record.tag_ids:
                tag_names = ' '.join(record.tag_ids.mapped('name'))
                search_parts.append(tag_names.lower())

            # Add notebook name
            if record.notebook_id.name:
                search_parts.append(record.notebook_id.name.lower())

            # Add mood
            if record.mood:
                # Add both the key and display value
                mood_display = dict(self._fields['mood'].selection).get(record.mood, '')
                search_parts.append(record.mood)
                if mood_display:
                    search_parts.append(mood_display.lower())

            # Combine all parts
            record.search_vector = ' '.join(search_parts) if search_parts else ''

    @api.depends('content')
    def _compute_word_count(self):
        """Compute word and character count from content"""
        for record in self:
            if record.content:
                try:
                    # Step 1: Replace specific HTML elements with appropriate spacing
                    content_with_spaces = record.content

                    # Replace block-level elements with spaces
                    block_elements = ['p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                    for element in block_elements:
                        content_with_spaces = re.sub(fr'</{element}>', ' ', content_with_spaces, flags=re.IGNORECASE)
                        content_with_spaces = re.sub(fr'<{element}[^>]*/?>', ' ', content_with_spaces,
                                                     flags=re.IGNORECASE)

                    # Step 2: Remove all remaining HTML tags
                    text_content = re.sub(r'<[^>]+>', '', content_with_spaces)

                    # Step 3: Handle HTML entities
                    text_content = html_parser.unescape(text_content)

                    # Step 4: Clean up whitespace
                    text_content = re.sub(r'\s+', ' ', text_content)

                    # Step 5: Trim and count
                    text_content = text_content.strip()

                    if text_content:
                        # Character count includes ALL characters
                        record.char_count = len(text_content)

                        # Word count excludes punctuation
                        translator = str.maketrans('', '', string.punctuation)
                        text_without_punctuation = text_content.translate(translator)

                        # Split into words and filter out empty strings
                        words = [word for word in text_without_punctuation.split() if word]
                        record.word_count = len(words)
                    else:
                        record.word_count = 0
                        record.char_count = 0

                except Exception as e:
                    _logger.error(f"Error computing word count for record {record.id}: {e}")
                    # Fallback: simple approach
                    text_content = re.sub(r'<[^>]+>', ' ', record.content)
                    text_content = re.sub(r'\s+', ' ', text_content).strip()

                    if text_content:
                        record.char_count = len(text_content)
                        translator = str.maketrans('', '', string.punctuation)
                        text_without_punctuation = text_content.translate(translator)
                        words = [word for word in text_without_punctuation.split() if word]
                        record.word_count = len(words)
                    else:
                        record.word_count = 0
                        record.char_count = 0
            else:
                record.word_count = 0
                record.char_count = 0

    # Version management methods
    def _create_version(self):
        """Create a new version when content changes"""
        for record in self:
            if record.content:
                # Create version record
                version_vals = {
                    'entry_id': record.id,
                    'version_number': record.current_version,
                    'content': record.content,
                    'word_count': record.word_count,
                    'char_count': record.char_count,
                    'created_by': record.env.user.id,
                }
                self.env['journal.entry.version'].create(version_vals)

                # Increment version number
                record.current_version += 1

    @api.model
    def create(self, vals):
        """Override create to handle initial version"""
        record = super().create(vals)
        return record

    def write(self, vals):
        """Override write to create versions on content changes"""
        if 'content' in vals:
            self._create_version()
        return super().write(vals)

    # Action methods
    def action_publish(self):
        """Publish the journal entry"""
        for entry in self:
            if entry.state == 'draft':
                entry.write({'state': 'published'})
        return True

    def action_draft(self):
        """Set entry back to draft"""
        for entry in self:
            if entry.state in ['published', 'archived']:
                entry.write({'state': 'draft'})
        return True

    def action_archive(self):
        """Archive the journal entry"""
        for entry in self:
            if entry.state == 'published':
                entry.write({'state': 'archived'})
        return True

    def action_toggle_favorite(self):
        """Toggle favorite status"""
        for entry in self:
            entry.is_favorite = not entry.is_favorite
        return True

    def action_delete(self):
        """Delete journal entries and return to entries list"""
        # Get the action to return to entries list BEFORE deleting
        action = self.env.ref('journal.action_journal_entries').read()[0]

        # Delete the entries
        self.unlink()

        # Return to entries list page
        return action

    def action_duplicate(self):
        """Duplicate the journal entry"""
        self.ensure_one()
        default = {
            'name': f"{self.name} (Copy)",
            'is_favorite': False,
            'current_version': 1,
        }
        return self.copy(default=default)

    def action_view_versions(self):
        """Open versions view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Versions of "{self.name}"',
            'res_model': 'journal.entry.version',
            'view_mode': 'tree,form',
            'domain': [('entry_id', '=', self.id)],
            'context': {'default_entry_id': self.id},
        }

    def action_restore_version(self, version_id):
        """Restore a specific version"""
        self.ensure_one()
        version = self.env['journal.entry.version'].browse(version_id)
        if version.entry_id == self:
            # Create current version before restoring
            self._create_version()
            # Restore the selected version
            self.write({
                'content': version.content,
                'word_count': version.word_count,
                'char_count': version.char_count,
            })
        return True

    def action_compare_versions(self):
        """Open version comparison view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Compare Versions of "{self.name}"',
            'res_model': 'journal.entry.version',
            'view_mode': 'tree',
            'domain': [('entry_id', '=', self.id)],
            'views': [(False, 'tree')],
            'context': {
                'default_entry_id': self.id,
                'comparison_mode': True,
            },
        }

    # Mood Analytics Methods
    def action_open_mood_analytics(self):
        """Open mood analytics dashboard"""
        action = self.env.ref('journal.action_journal_mood_analysis').read()[0]
        return action

    @api.model
    def get_mood_analytics_data(self, period='all'):
        """Get mood analytics data for the current user"""
        return self.env['journal.mood.analysis'].get_mood_statistics(
            user_id=self.env.user.id,
            period=period
        )

    @api.model
    def get_mood_timeline_data(self, days=30):
        """Get mood timeline data for charts"""
        return self.env['journal.mood.analysis'].get_mood_timeline(
            user_id=self.env.user.id,
            days=days
        )

    # Export methods
    def action_export_pdf(self):
        """Export journal entry as PDF"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/journal/entry/{self.id}/pdf',
            'target': 'new',
        }

    def action_export_markdown(self):
        """Export journal entry as Markdown"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/journal/entry/{self.id}/markdown',
            'target': 'new',
        }

    def _get_clean_content_text(self):
        """Convert HTML content to clean text for exports"""
        self.ensure_one()
        if not self.content:
            return ""

        # Remove HTML tags but preserve basic formatting
        text_content = re.sub(r'<br\s*/?>', '\n', self.content, flags=re.IGNORECASE)
        text_content = re.sub(r'<p[^>]*>', '\n', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'</p>', '\n\n', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'<h[1-6][^>]*>', '\n# ', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'</h[1-6]>', '\n\n', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'<strong[^>]*>', '**', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'</strong>', '**', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'<em[^>]*>', '*', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'</em>', '*', text_content, flags=re.IGNORECASE)
        text_content = re.sub(r'<[^>]+>', '', text_content)

        # Handle HTML entities
        text_content = html_parser.unescape(text_content)

        # Clean up whitespace
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        return text_content.strip()

    def _generate_markdown_content(self):
        """Generate Markdown formatted content"""
        self.ensure_one()

        # Header
        markdown = f"# {self.name}\n\n"

        # Metadata
        markdown += "## Metadata\n\n"
        markdown += f"- **Date:** {self.entry_date.strftime('%Y-%m-%d')}\n"
        markdown += f"- **Notebook:** {self.notebook_id.name}\n"
        if self.tag_ids:
            tags = ', '.join(self.tag_ids.mapped('name'))
            markdown += f"- **Tags:** {tags}\n"
        if self.mood:
            mood_display = dict(self._fields['mood'].selection).get(self.mood, '')
            markdown += f"- **Mood:** {mood_display}\n"
        markdown += f"- **Status:** {self.state.title()}\n"
        if self.is_favorite:
            markdown += "- **Favorite:** ⭐\n"
        markdown += f"- **Words:** {self.word_count}\n"
        markdown += f"- **Characters:** {self.char_count}\n"
        markdown += f"- **Version:** {self.current_version - 1}\n"

        # Content
        markdown += "\n## Content\n\n"
        markdown += self._get_clean_content_text()

        # Footer
        markdown += f"\n\n---\n*Exported from Journal on {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}*"

        return markdown

    def _generate_pdf_html_content(self):
        """Generate HTML content optimized for PDF generation"""
        self.ensure_one()

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{html_parser.escape(self.name)}</title>
    <style>
        @page {{
            margin: 2cm;
            size: A4;
        }}
        body {{
            font-family: "DejaVu Sans", "Arial", sans-serif;
            font-size: 12px;
            line-height: 1.4;
            color: #000000;
            margin: 0;
            padding: 0;
        }}
        .header {{
            border-bottom: 3px solid #333333;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        .title {{
            font-size: 20px;
            font-weight: bold;
            color: #000000;
            text-align: center;
            margin: 0;
        }}
        .metadata {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .metadata-row {{
            margin: 6px 0;
            display: flex;
        }}
        .metadata-label {{
            font-weight: bold;
            min-width: 100px;
            color: #495057;
        }}
        .metadata-value {{
            flex: 1;
        }}
        .content {{
            margin-top: 25px;
        }}
        .content p {{
            margin-bottom: 12px;
        }}
        .content h1, .content h2, .content h3 {{
            margin-top: 20px;
            margin-bottom: 10px;
            color: #000000;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #cccccc;
            color: #666666;
            font-size: 10px;
            text-align: center;
        }}
        .no-content {{
            font-style: italic;
            color: #6c757d;
            text-align: center;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{html_parser.escape(self.name)}</h1>
    </div>

    <div class="metadata">
        <div class="metadata-row">
            <span class="metadata-label">Date:</span>
            <span class="metadata-value">{self.entry_date.strftime('%B %d, %Y')}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Notebook:</span>
            <span class="metadata-value">{html_parser.escape(self.notebook_id.name)}</span>
        </div>
"""

        if self.tag_ids:
            tags = ', '.join(self.tag_ids.mapped('name'))
            html_content += f"""        <div class="metadata-row">
            <span class="metadata-label">Tags:</span>
            <span class="metadata-value">{html_parser.escape(tags)}</span>
        </div>
"""

        if self.mood:
            mood_display = dict(self._fields['mood'].selection).get(self.mood, '')
            html_content += f"""        <div class="metadata-row">
            <span class="metadata-label">Mood:</span>
            <span class="metadata-value">{html_parser.escape(mood_display)}</span>
        </div>
"""

        html_content += f"""        <div class="metadata-row">
            <span class="metadata-label">Status:</span>
            <span class="metadata-value">{self.state.title()}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Favorite:</span>
            <span class="metadata-value">{'⭐ Yes' if self.is_favorite else 'No'}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Words:</span>
            <span class="metadata-value">{self.word_count}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Characters:</span>
            <span class="metadata-value">{self.char_count}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Version:</span>
            <span class="metadata-value">{self.current_version - 1}</span>
        </div>
    </div>

    <div class="content">
        {self.content if self.content else '<p class="no-content">No content available</p>'}
    </div>

    <div class="footer">
        Exported from Journal on {fields.Datetime.now().strftime('%B %d, %Y at %H:%M')}
    </div>
</body>
</html>"""

        return html_content

    # Enhanced search method with full-text support
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """Enhanced search that includes content and tags with full-text support"""
        if args is None:
            args = []

        if name:
            # Split search terms for multiple word search
            search_terms = name.strip().split()

            # Build domain for each search term
            domain = args
            for term in search_terms:
                if len(term) > 2:  # Only search for terms with more than 2 characters
                    term_domain = ['|', '|', '|', '|',
                                   ('name', 'ilike', term),
                                   ('content', 'ilike', term),
                                   ('tag_ids.name', 'ilike', term),
                                   ('notebook_id.name', 'ilike', term),
                                   ('search_vector', 'ilike', f'%{term}%')
                                   ]
                    if domain == args:
                        domain = term_domain
                    else:
                        domain = ['&'] + domain + term_domain

            return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(name, args, operator, limit, name_get_uid)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """Override search to include full-text search capabilities"""
        if count:
            return super()._search(args, offset=offset, limit=limit, order=order, count=count)
        else:
            return super()._search(args, offset=offset, limit=limit, order=order)

    # Constraints
    @api.constrains('entry_date')
    def _check_entry_date(self):
        for entry in self:
            if entry.entry_date > fields.Date.today():
                raise ValidationError("Entry date cannot be in the future.")

    @api.constrains('name')
    def _check_name_length(self):
        for entry in self:
            if len(entry.name.strip()) < 2:
                raise ValidationError("Title must be at least 2 characters long.")