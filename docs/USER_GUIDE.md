# 📓 Journal Module - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Creating Journal Entries](#creating-journal-entries)
3. [Managing Notebooks](#managing-notebooks)
4. [Working with Tags](#working-with-tags)
5. [Searching Entries](#searching-entries)
6. [Mood Analytics](#mood-analytics)
7. [Exporting Entries](#exporting-entries)
8. [Version History](#version-history)
9. [Managing Archived Content](#managing-archived-content)
10. [Tips & Best Practices](#tips--best-practices)

---

## 1. Getting Started

### 1.1 First Time Setup
1. **Access the Journal**:
   - Click on the **Journal** app in your Odoo main menu
   - You'll see the main dashboard with "My Entries"

### 1.2 Understanding the Interface
- **My Entries**: Your main journal entries list
- **Notebooks**: Organize entries into categories
- **Tags**: Label entries for easy filtering
- **Mood Analysis**: View analytics on your journaling habits
- **Archived**: Access archived entries, notebooks, and tags

### 1.3 Quick Start Checklist
- [ ] Create your first notebook
- [ ] Write your first entry
- [ ] Add some tags
- [ ] Set a mood for your entry
- [ ] Explore the mood analytics dashboard

---

## 2. Creating Journal Entries

### 2.1 Creating a New Entry
1. Navigate to **Journal → My Entries**
2. Click **New Entry** button
3. Fill in the form:
   - **Title**: What's on your mind?
   - **Notebook**: Select an existing notebook (required)
   - **Tags**: Add relevant tags (optional)
   - **Date**: Entry date (defaults to today)
   - **Mood**: Select your current mood from 8 options
   - **Content**: Write your thoughts in the HTML editor

### 2.2 Entry States Explained
Each entry has three states:

| State | Description |
|-------|-------------|
| **Draft** | Entry is being written, not visible in searches |
| **Published** | Entry is complete and searchable |
| **Archived** | Entry is hidden from main view |

### 2.3 Entry Actions
From the entry form header, you can:
- **Publish**: Move from Draft to Published
- **Set to Draft**: Return Published to Draft
- **Archive**: Move any entry to Archived
- **Toggle Favorite**: Click star icon to mark/unmark as favorite
- **Delete**: Permanently remove entry (with confirmation)
- **Export PDF**: Save entry as PDF document
- **Export Markdown**: Save entry as Markdown text file
- **Version History**: View all saved versions of this entry

### 2.4 Auto-Calculated Fields
- **Word Count**: Automatically calculated as you type
- **Character Count**: Shows total characters
- **Versions Count**: Shows number of saved versions
- **Current Version**: Shows which version you're viewing

### 2.5 Required Fields
- **Title**: Entry title
- **Notebook**: Must select a notebook for each entry

---

## 3. Managing Notebooks

### 3.1 Creating Notebooks
1. Go to **Journal → Notebooks**
2. Click **New Notebook**
3. Enter:
   - **Name**: Notebook name
   - **Color**: Choose from 12 color options (default: Grey)
   - **Sequence**: Number for ordering (lower numbers appear first)

### 3.2 Notebook Colors Available
You have 12 color options for notebooks:

| Color | Display |
|-------|---------|
| Grey | Default neutral color |
| Red | Bright attention color |
| Orange | Warm, energetic color |
| Yellow | Bright, cheerful color |
| Light Blue | Calm, peaceful color |
| Dark Purple | Royal, creative color |
| Salmon Pink | Soft, gentle color |
| Medium Blue | Professional, trustworthy color |
| Dark Blue | Serious, formal color |
| Fuchsia | Vibrant, energetic color |
| Green | Growth, natural color |
| Purple | Creative, spiritual color |

### 3.3 Notebook Statistics
Each notebook in the list shows:
- **Entries Count**: Number of entries in this notebook
- **Last Entry Date**: Date of most recent entry
- **Active Status**: Green checkmark (active) or grey X (archived)

### 3.4 Notebook Actions
From the notebook form:
- **Save**: Save changes
- **Discard**: Cancel without saving
- **View Entries**: See all entries in this notebook
- **Delete Notebook**: Delete notebook and ALL its entries (with warning)

### 3.5 Notebook Ordering
- Notebooks are ordered by **Sequence** number (ascending)
- Lower sequence numbers appear first
- If sequence is same, ordered by name alphabetically

---

## 4. Working with Tags

### 4.1 Creating and Using Tags
1. Go to **Journal → Tags**
2. Click **New Tag**
3. Enter:
   - **Name**: Tag name
   - **Color**: Choose from 12 color options (same as notebooks)
   - **Active**: Checkbox to make tag active (uncheck to archive)

### 4.2 Tag Colors
Same 12 colors available as notebooks:
- Grey (0), Red (1), Orange (2), Yellow (3), Light Blue (4)
- Dark Purple (5), Salmon Pink (6), Medium Blue (7), Dark Blue (8)
- Fuchsia (9), Green (10), Purple (11)

### 4.3 Tagging Entries
When creating/editing an entry:
- Click in the **Tags** field
- Type to search existing tags
- Select from dropdown or create new tags
- Tags display with their colored circles

### 4.4 Tag Statistics
Each tag shows:
- **Entries Count**: How many entries use this tag
- **Active Status**: Whether tag is active or archived

### 4.5 Tag Management
- **Archive**: Uncheck "Active" to hide tag without deleting
- **Delete**: Permanently delete tag (removes from all entries)
- **Color Coding**: Use colors to group related tags

### 4.6 Viewing Tagged Entries
From the tags list, you can:
- See which tags are most used (by entry count)
- Filter to show only active or archived tags
- Group tags by color or active status

---

## 5. Searching Entries

### 5.1 Basic Search
- **Search Bar**: Type to search entry titles
- **Advanced Search**: Click filter icon for more options

### 5.2 Available Filters
Use the filter panel to narrow results:

| Filter | Description |
|--------|-------------|
| **My Entries** | Show only entries you created |
| **Draft** | Show draft entries only |
| **Published** | Show published entries only |
| **Archived** | Show archived entries only |
| **Favorites** | Show starred/favorite entries only |
| **Has Mood** | Show entries with mood set |
| **Full Text Search** | Search across titles AND content |

### 5.3 Group By Options
Organize your entries by:

| Group By | Description |
|----------|-------------|
| **Notebook** | Group entries by notebook |
| **Status** | Group by draft/published/archived |
| **Mood** | Group by emotional state |
| **Date** | Group by month |

### 5.4 Search Tips
- Use **Full Text Search** to find words within entry content
- Combine **multiple filters** for precise results
- Save frequent searches as **favorites** in your browser
- Use **Group By** to see patterns in your entries

---

## 6. Mood Analytics

### 6.1 Accessing Analytics
1. Go to **Journal → Mood Analysis**
2. View three different perspectives:
   - **Tree View**: List of entries with moods
   - **Pivot Table**: Multi-dimensional analysis
   - **Graph View**: Visual mood distribution

### 6.2 Available Moods
You have 8 mood options:

| Mood | Emoji | When to Use |
|------|-------|-------------|
| **Happy** | 😊 | Joyful, positive moments |
| **Sad** | 😢 | Difficult, reflective times |
| **Excited** | 😃 | Enthusiastic, energetic states |
| **Angry** | 😠 | Frustrated, irritated feelings |
| **Peaceful** | 😌 | Calm, relaxed, serene |
| **Anxious** | 😰 | Worried, nervous, stressed |
| **Grateful** | 🙏 | Thankful, appreciative moments |
| **Tired** | 😴 | Fatigued, exhausted days |

### 6.3 Pivot Table Analysis
Analyze your journal data by:
- **Rows**: Mood and/or Notebook
- **Columns**: Date by month
- **Measures**: Word count totals

What you can discover:
- Which moods you experience most frequently
- How many words you write in different moods
- Mood patterns over time (by month)
- Connection between notebooks and moods

### 6.4 Graph Views
- **Pie Chart**: Shows percentage of each mood
- **Bar Chart**: Compares moods (alternative view)

### 6.5 Mood Analytics Filters
When in Mood Analysis, you can filter by:
- **My Entries**: Your entries only
- **Has Mood**: Entries with mood set
- **This Week**: Recent entries
- **This Month**: Current month entries
- **Last 30 Days**: Past month entries

### 6.6 Group By in Analytics
- **Mood**: Group entries by emotional state
- **Notebook**: Group by notebook category
- **Week**: Group by week of the year
- **Month**: Group by month

---

## 7. Exporting Entries

### 7.1 Export Options
From any entry form, click:
- **Export PDF**: Creates formatted PDF document
- **Export Markdown**: Creates plain text with markdown

### 7.2 What Gets Exported
Both exports include:
- Entry title
- Date
- Notebook
- Tags
- Mood
- Full content
- Word count

### 7.3 PDF Export Features
- Professional formatting
- Preserves text formatting
- Includes all entry metadata
- Ready for printing or sharing

### 7.4 Markdown Export Features
- Plain text format
- Markdown syntax for headings, lists, etc.
- Compatible with most text editors
- Good for backups or migrating content

---

## 8. Version History

### 8.1 How Versioning Works
- Every time you save changes to entry content, a new version is saved
- Automatic version tracking
- You can view all historical versions

### 8.2 Accessing Versions
1. Open any journal entry
2. Click **"Version History"** button
3. Browse through saved versions
4. See **"Current Version"** number in the form

### 8.3 Version Display
- **Versions Count**: Shows total number of versions
- **Current Version**: Shows which version you're viewing
- System keeps a limited history (automatic cleanup)

---

## 9. Managing Archived Content

### 9.1 What Can Be Archived
Three types of content can be archived:
1. **Journal Entries** (change state to "Archived")
2. **Tags** (uncheck "Active" checkbox)
3. **Notebooks** (uncheck "Active" checkbox)

### 9.2 Accessing Archived Content
1. Go to **Journal → Archived**
2. Choose from sub-menus:
   - **Archived Entries**: View archived journal entries
   - **Archived Tags**: View inactive tags
   - **Archived Notebooks**: View hidden notebooks

### 9.3 Restoring Archived Items
To restore any archived item:
1. Open the archived item from the Archived menu
2. For entries: Change state from "Archived" to "Published" or "Draft"
3. For tags/notebooks: Check the "Active" checkbox
4. Save changes

### 9.4 Archive Benefits
- **Clean View**: Hide old/unused items from main lists
- **Preservation**: Keep data without cluttering workspace
- **Reversible**: Easy to restore if needed later
- **Organization**: Separate active and inactive content

---

## 10. Tips & Best Practices

### 10.1 Getting Started Tips
1. **Start Simple**: Create 1-2 notebooks first
2. **Use Tags Wisely**: Create tags as you need them
3. **Set Moods**: Make it a habit to set mood for each entry
4. **Explore Features**: Try all the buttons and filters

### 10.2 Organization Strategies
- **Notebooks by Purpose**: Personal, Work, Ideas, Memories
- **Color Coding**: Use consistent colors for notebooks and tags
- **Sequence Numbers**: Use 10, 20, 30 for ordering (allows inserting later)
- **Regular Cleanup**: Archive old entries monthly

### 10.3 Writing Habits
- **Daily Practice**: Try to write something every day
- **Use Templates**: Copy previous entries as templates
- **Review Old Entries**: Use search to find related past entries
- **Export Important**: Export special entries as backup

### 10.4 Search Efficiency
- **Use Full Text Search**: Finds words anywhere in content
- **Save Filters**: Browser bookmarks for common searches
- **Combine Filters**: Mood + Date range for specific periods
- **Group Views**: Use "Group By" to see patterns

### 10.5 Mood Tracking Benefits
- **Self-Awareness**: Notice emotional patterns
- **Trigger Identification**: See what affects your moods
- **Progress Tracking**: Monitor emotional well-being over time
- **Writing Insight**: See which moods inspire more writing

### 10.6 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't find entry | Use Full Text Search |
| Missing notebook | Check Archived Notebooks |
| Tag not showing | Check if tag is Active |
| No mood options | Ensure field isn't empty |
| Can't export | Check browser permissions |
| Slow loading | Archive old entries |

---

## Need Help?

### Module Features Summary
- **Entries**: Create, edit, publish, archive, favorite, export
- **Notebooks**: Organize with colors and sequencing
- **Tags**: Categorize with color coding
- **Search**: Full-text search with advanced filters
- **Analytics**: Mood tracking with pivot tables and graphs
- **Versioning**: Automatic version history
- **Archiving**: Separate management of inactive content

### Color Reference
Remember the 12 available colors for notebooks and tags:
1. Grey, 2. Red, 3. Orange, 4. Yellow, 5. Light Blue
6. Dark Purple, 7. Salmon Pink, 8. Medium Blue, 9. Dark Blue
10. Fuchsia, 11. Green, 12. Purple

### Quick Reference
- **New Entry**: Journal → My Entries → New Entry
- **New Notebook**: Journal → Notebooks → New Notebook
- **New Tag**: Journal → Tags → New Tag
- **Analytics**: Journal → Mood Analysis
- **Archived**: Journal → Archived → [type]

---
*Last Updated: 04/12/2025* 

*Module Version: 1.0*