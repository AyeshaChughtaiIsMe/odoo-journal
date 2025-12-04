{
    'name': 'Journal',
    'version': '1.0',
    'summary': 'A comprehensive personal journal system with mood tracking and analytics',
    'description': """
    Personal Journal Module
    ======================
    
    A feature-rich journaling system for Odoo that helps users:
    - Write and organize journal entries
    - Track moods and emotions
    - Analyze writing patterns
    - Export entries in multiple formats
    - Maintain version history
    
    Features include:
    * Notebook organization
    * Tag-based categorization
    * Full-text search
    * Mood analytics dashboard
    * Version control system
    * PDF/Markdown export
    """,
    'category': 'Productivity',
    'author': 'Ayesha Chughtai',
    'website': 'https://ayeshachughtaiisme.github.io/odoo-journal',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/journal_views.xml',
        'views/journal_entry_version_views.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}