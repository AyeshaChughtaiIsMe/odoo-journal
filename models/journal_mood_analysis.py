from odoo import models, fields, api, tools  # ADDED 'tools' import
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class JournalMoodAnalysis(models.Model):
    """
    Journal Mood Analysis SQL View Model

    Provides analytical views and statistics for journal mood tracking.
    This is a SQL view (not a regular table) that aggregates mood data
    for efficient reporting and analytics.

    Key Features:
    - SQL view for fast aggregation queries
    - Mood statistics by various dimensions
    - Trend analysis over time periods
    - Timeline data for chart visualizations
    - Mood correlation analysis

    Note: This is a read-only model (_auto=False) that maps to a SQL view.

    Attributes:
        entry_date (Date): Date of journal entry
        mood (Selection): Emotional state (happy, sad, excited, etc.)
        user_id (Many2one): User who created the entry
        notebook_id (Many2one): Notebook containing the entry
        entry_count (Integer): Count of entries for this grouping
        total_word_count (Integer): Sum of word counts
        avg_word_count (Float): Average words per entry

    Methods:
        init(): Creates/refreshes the SQL view
        get_mood_statistics(): Comprehensive mood stats for user
        _calculate_mood_trends(): Calculates mood change trends
        get_mood_timeline(): Timeline data for chart visualizations
        _calculate_mood_consistency(): Calculates mood consistency score
        get_mood_calendar(): Calendar view data for specific month
        get_mood_correlations(): Analyzes mood correlations with factors
    """
    _name = 'journal.mood.analysis'
    _description = 'Journal Mood Analysis'
    _auto = False  # This will be a SQL view

    entry_date = fields.Date(string='Entry Date')
    mood = fields.Selection([
        ('happy', '😊 Happy'),
        ('sad', '😢 Sad'),
        ('excited', '😃 Excited'),
        ('angry', '😠 Angry'),
        ('peaceful', '😌 Peaceful'),
        ('anxious', '😰 Anxious'),
        ('grateful', '🙏 Grateful'),
        ('tired', '😴 Tired'),
    ], string='Mood')
    user_id = fields.Many2one('res.users', string='User')
    notebook_id = fields.Many2one('journal.notebook', string='Notebook')
    entry_count = fields.Integer(string='Entry Count')
    total_word_count = fields.Integer(string='Total Words')
    avg_word_count = fields.Float(string='Average Words')

    def init(self):
        """Initialize the SQL view for mood analysis"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW journal_mood_analysis AS (
                SELECT 
                    ROW_NUMBER() OVER () as id,
                    je.entry_date as entry_date,
                    je.mood as mood,
                    je.user_id as user_id,
                    je.notebook_id as notebook_id,
                    COUNT(je.id) as entry_count,
                    SUM(je.word_count) as total_word_count,
                    AVG(je.word_count) as avg_word_count
                FROM journal_entry je
                WHERE je.mood IS NOT NULL
                GROUP BY je.entry_date, je.mood, je.user_id, je.notebook_id
            )
        """)

    @api.model
    def get_mood_statistics(self, user_id=None, period='all'):
        """Get comprehensive mood statistics for a user"""
        user_id = user_id or self.env.user.id

        # Build domain based on period
        domain = [('user_id', '=', user_id)]

        if period == 'week':
            start_date = datetime.now().date() - timedelta(days=7)
            domain.append(('entry_date', '>=', start_date))
        elif period == 'month':
            start_date = datetime.now().date().replace(day=1)
            domain.append(('entry_date', '>=', start_date))
        elif period == 'year':
            start_date = datetime.now().date().replace(month=1, day=1)
            domain.append(('entry_date', '>=', start_date))

        # Get entries with mood data
        entries = self.env['journal.entry'].search(domain)
        mood_entries = entries.filtered(lambda e: e.mood)

        if not mood_entries:
            return {
                'total_entries': 0,
                'mood_counts': {},
                'mood_percentages': {},
                'most_common_mood': None,
                'mood_trends': {},
                'notebook_breakdown': {},
            }

        # Count moods
        mood_counts = {}
        for entry in mood_entries:
            mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1

        total_entries = len(mood_entries)

        # Calculate percentages
        mood_percentages = {}
        for mood, count in mood_counts.items():
            mood_percentages[mood] = round((count / total_entries) * 100, 2)

        # Find most common mood
        most_common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None

        # Calculate mood trends (last 7 days vs previous 7 days)
        mood_trends = self._calculate_mood_trends(user_id)

        # Notebook breakdown
        notebook_breakdown = {}
        for entry in mood_entries:
            notebook_name = entry.notebook_id.name
            if notebook_name not in notebook_breakdown:
                notebook_breakdown[notebook_name] = {}
            notebook_breakdown[notebook_name][entry.mood] = notebook_breakdown[notebook_name].get(entry.mood, 0) + 1

        return {
            'total_entries': total_entries,
            'mood_counts': mood_counts,
            'mood_percentages': mood_percentages,
            'most_common_mood': most_common_mood,
            'mood_trends': mood_trends,
            'notebook_breakdown': notebook_breakdown,
            'period': period,
        }

    def _calculate_mood_trends(self, user_id):
        """Calculate mood trends comparing recent period with previous period"""
        end_date = datetime.now().date()
        recent_start = end_date - timedelta(days=7)
        previous_start = recent_start - timedelta(days=7)

        # Recent period entries
        recent_entries = self.env['journal.entry'].search([
            ('user_id', '=', user_id),
            ('mood', '!=', False),
            ('entry_date', '>=', recent_start),
            ('entry_date', '<=', end_date)
        ])

        # Previous period entries
        previous_entries = self.env['journal.entry'].search([
            ('user_id', '=', user_id),
            ('mood', '!=', False),
            ('entry_date', '>=', previous_start),
            ('entry_date', '<', recent_start)
        ])

        # Count moods for each period
        recent_counts = {}
        for entry in recent_entries:
            recent_counts[entry.mood] = recent_counts.get(entry.mood, 0) + 1

        previous_counts = {}
        for entry in previous_entries:
            previous_counts[entry.mood] = previous_counts.get(entry.mood, 0) + 1

        # Calculate trends
        trends = {}
        all_moods = set(list(recent_counts.keys()) + list(previous_counts.keys()))

        for mood in all_moods:
            recent_count = recent_counts.get(mood, 0)
            previous_count = previous_counts.get(mood, 0)

            if previous_count == 0:
                trend = 100 if recent_count > 0 else 0
            else:
                trend = ((recent_count - previous_count) / previous_count) * 100

            trends[mood] = {
                'recent_count': recent_count,
                'previous_count': previous_count,
                'trend_percentage': round(trend, 2),
                'trend_direction': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
            }

        return trends

    @api.model
    def get_mood_timeline(self, user_id=None, days=30):
        """Get mood timeline data for charts"""
        user_id = user_id or self.env.user.id
        start_date = datetime.now().date() - timedelta(days=days)

        entries = self.env['journal.entry'].search([
            ('user_id', '=', user_id),
            ('mood', '!=', False),
            ('entry_date', '>=', start_date)
        ], order='entry_date')

        timeline_data = []
        mood_sequence = []

        for entry in entries:
            timeline_data.append({
                'date': entry.entry_date.strftime('%Y-%m-%d'),
                'mood': entry.mood,
                'mood_display': dict(self.env['journal.entry']._fields['mood'].selection).get(entry.mood, ''),
                'entry_name': entry.name,
                'word_count': entry.word_count,
                'notebook': entry.notebook_id.name,
            })

            mood_sequence.append({
                'date': entry.entry_date.strftime('%Y-%m-%d'),
                'mood': entry.mood,
            })

        # Calculate mood consistency
        consistency = self._calculate_mood_consistency(mood_sequence)

        return {
            'timeline_data': timeline_data,
            'mood_sequence': mood_sequence,
            'consistency': consistency,
            'days': days,
            'total_entries': len(entries),
        }

    def _calculate_mood_consistency(self, mood_sequence):
        """Calculate mood consistency metrics"""
        if not mood_sequence:
            return {'score': 0, 'trend': 'stable'}

        # Simple consistency: count mood changes
        changes = 0
        previous_mood = None

        for entry in mood_sequence:
            if previous_mood and entry['mood'] != previous_mood:
                changes += 1
            previous_mood = entry['mood']

        total_entries = len(mood_sequence)
        consistency_score = max(0, 100 - (changes / max(1, total_entries - 1)) * 100)

        return {
            'score': round(consistency_score, 2),
            'changes': changes,
            'trend': 'high' if consistency_score > 70 else 'medium' if consistency_score > 40 else 'low'
        }

    @api.model
    def get_mood_calendar(self, user_id=None, year=None, month=None):
        """Get mood calendar data for specific year/month"""
        user_id = user_id or self.env.user.id
        current_date = datetime.now().date()
        year = year or current_date.year
        month = month or current_date.month

        # Get first and last day of month
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        start_date = f"{year}-{month:02d}-01"
        end_date = f"{next_year}-{next_month:02d}-01"

        entries = self.env['journal.entry'].search([
            ('user_id', '=', user_id),
            ('mood', '!=', False),
            ('entry_date', '>=', start_date),
            ('entry_date', '<', end_date)
        ])

        calendar_data = {}
        mood_summary = {}

        for entry in entries:
            date_str = entry.entry_date.strftime('%Y-%m-%d')
            if date_str not in calendar_data:
                calendar_data[date_str] = {
                    'moods': [],
                    'entries': [],
                    'primary_mood': None,
                    'entry_count': 0,
                }

            calendar_data[date_str]['moods'].append(entry.mood)
            calendar_data[date_str]['entries'].append({
                'name': entry.name,
                'mood': entry.mood,
                'mood_display': dict(self.env['journal.entry']._fields['mood'].selection).get(entry.mood, ''),
                'word_count': entry.word_count,
            })
            calendar_data[date_str]['entry_count'] += 1

            # Count for mood summary
            mood_summary[entry.mood] = mood_summary.get(entry.mood, 0) + 1

        # Determine primary mood for each day
        for date_str, data in calendar_data.items():
            if data['moods']:
                # Find most frequent mood for the day
                from collections import Counter
                mood_counter = Counter(data['moods'])
                data['primary_mood'] = mood_counter.most_common(1)[0][0]

        return {
            'year': year,
            'month': month,
            'calendar_data': calendar_data,
            'mood_summary': mood_summary,
            'total_days_with_entries': len(calendar_data),
            'total_entries': len(entries),
        }

    @api.model
    def get_mood_correlations(self, user_id=None):
        """Analyze correlations between moods and other factors"""
        user_id = user_id or self.env.user.id

        entries = self.env['journal.entry'].search([
            ('user_id', '=', user_id),
            ('mood', '!=', False)
        ])

        if not entries:
            return {}

        # Mood vs Word Count
        mood_word_stats = {}
        for entry in entries:
            mood = entry.mood
            if mood not in mood_word_stats:
                mood_word_stats[mood] = []
            mood_word_stats[mood].append(entry.word_count)

        # Calculate averages
        mood_avg_words = {}
        for mood, word_counts in mood_word_stats.items():
            mood_avg_words[mood] = sum(word_counts) / len(word_counts)

        # Mood vs Notebook
        mood_notebook_stats = {}
        for entry in entries:
            mood = entry.mood
            notebook = entry.notebook_id.name
            if mood not in mood_notebook_stats:
                mood_notebook_stats[mood] = {}
            mood_notebook_stats[mood][notebook] = mood_notebook_stats[mood].get(notebook, 0) + 1

        # Mood vs Day of Week
        mood_weekday_stats = {}
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for entry in entries:
            mood = entry.mood
            weekday = entry.entry_date.weekday()
            if mood not in mood_weekday_stats:
                mood_weekday_stats[mood] = [0] * 7
            mood_weekday_stats[mood][weekday] += 1

        return {
            'mood_avg_words': {mood: round(avg, 2) for mood, avg in mood_avg_words.items()},
            'mood_notebook_distribution': mood_notebook_stats,
            'mood_weekday_distribution': mood_weekday_stats,
            'weekdays': weekdays,
        }