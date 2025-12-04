from odoo import http
from odoo.http import request, content_disposition
import logging
import subprocess
import tempfile
import os
import difflib
import re
import html as html_parser

_logger = logging.getLogger(__name__)


class JournalExportController(http.Controller):

    @http.route('/journal/entry/<int:entry_id>/pdf', type='http', auth='user')
    def export_pdf(self, entry_id, **kwargs):
        """Export journal entry as real PDF using wkhtmltopdf"""
        try:
            entry = request.env['journal.entry'].browse(entry_id)
            if not entry.exists() or entry.user_id != request.env.user:
                return request.not_found()

            _logger.info(f"Starting PDF export for entry {entry_id}: {entry.name}")

            # Generate HTML content
            html_content = entry._generate_pdf_html_content()

            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_file:
                html_file.write(html_content)
                html_path = html_file.name

            pdf_path = html_path.replace('.html', '.pdf')

            try:
                # Call wkhtmltopdf DIRECTLY - using the exact path that worked in your test
                wkhtmltopdf_path = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"

                _logger.info(f"Calling wkhtmltopdf: {wkhtmltopdf_path}")

                # Simple command - no complex options that might fail
                result = subprocess.run([
                    wkhtmltopdf_path,
                    '--quiet',
                    html_path,
                    pdf_path
                ], capture_output=True, timeout=30, shell=True)  # Added shell=True for Windows

                _logger.info(f"wkhtmltopdf return code: {result.returncode}")

                if result.returncode == 0 and os.path.exists(pdf_path):
                    _logger.info(f"PDF successfully created: {pdf_path}")

                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_content = pdf_file.read()

                    filename = f"journal_entry_{entry.name.replace(' ', '_')}_{entry.entry_date}.pdf"

                    response = request.make_response(
                        pdf_content,
                        headers=[
                            ('Content-Type', 'application/pdf'),
                            ('Content-Disposition', content_disposition(filename)),
                            ('Content-Length', str(len(pdf_content))),
                        ]
                    )

                    _logger.info(f"PDF response ready, size: {len(pdf_content)} bytes")
                    return response
                else:
                    error_msg = f"wkhtmltopdf failed. Return code: {result.returncode}, Stderr: {result.stderr.decode('utf-8', errors='ignore')}"
                    _logger.error(error_msg)
                    raise Exception(error_msg)

            except subprocess.TimeoutExpired:
                _logger.error("wkhtmltopdf timed out")
                raise Exception("PDF generation timed out")
            except Exception as e:
                _logger.error(f"PDF generation error: {e}")
                raise e

            finally:
                # Clean up temp files
                try:
                    if os.path.exists(html_path):
                        os.unlink(html_path)
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)
                except Exception as clean_error:
                    _logger.warning(f"Cleanup error: {clean_error}")

        except Exception as e:
            _logger.error(f"PDF export completely failed: {e}")
            # Return a simple error message instead of falling back to HTML
            error_html = f"""
            <html>
            <body>
                <h1>PDF Export Failed</h1>
                <p>Could not generate PDF file.</p>
                <p>Error: {str(e)}</p>
                <p>Please check Odoo server logs for details.</p>
            </body>
            </html>
            """
            return request.make_response(
                error_html.encode('utf-8'),
                headers=[('Content-Type', 'text/html')]
            )

    @http.route('/journal/entry/<int:entry_id>/markdown', type='http', auth='user')
    def export_markdown(self, entry_id, **kwargs):
        """Export journal entry as Markdown"""
        try:
            entry = request.env['journal.entry'].browse(entry_id)
            if not entry.exists() or entry.user_id != request.env.user:
                return request.not_found()

            markdown_content = entry._generate_markdown_content()
            filename = f"journal_entry_{entry.name.replace(' ', '_')}_{entry.entry_date}.md"

            return request.make_response(
                markdown_content.encode('utf-8'),
                headers=[
                    ('Content-Type', 'text/markdown; charset=utf-8'),
                    ('Content-Disposition', content_disposition(filename))
                ]
            )
        except Exception as e:
            _logger.error(f"Markdown export error: {e}")
            return request.not_found()

    @http.route('/journal/compare/<int:entry_id>/<int:version1_id>/<int:version2_id>', type='http', auth='user')
    def compare_versions(self, entry_id, version1_id, version2_id, **kwargs):
        """Compare two versions side by side with change highlighting"""
        try:
            entry = request.env['journal.entry'].browse(entry_id)
            version1 = request.env['journal.entry.version'].browse(version1_id)
            version2 = request.env['journal.entry.version'].browse(version2_id)

            if not all([entry.exists(), version1.exists(), version2.exists()]):
                return request.not_found()

            # HTML diff with change highlighting
            def html_diff_with_highlighting(old_html, new_html):
                # Convert HTML to plain text for diffing
                def html_to_text(html):
                    if not html:
                        return ""
                    # Simple HTML to text conversion
                    text = html.replace('<p>', '\n').replace('</p>', '\n')
                    text = re.sub(r'<[^>]+>', '', text)
                    text = html_parser.unescape(text)
                    return text

                old_text = html_to_text(old_html)
                new_text = html_to_text(new_html)

                # Generate diff
                diff = difflib.unified_diff(
                    old_text.splitlines(keepends=True),
                    new_text.splitlines(keepends=True),
                    fromfile=f'Version {version1.version_number}',
                    tofile=f'Version {version2.version_number}',
                    n=3
                )

                diff_html = []
                for line in diff:
                    if line.startswith('+'):
                        diff_html.append(f'<div class="diff-added">+ {html_parser.escape(line[1:])}</div>')
                    elif line.startswith('-'):
                        diff_html.append(f'<div class="diff-removed">- {html_parser.escape(line[1:])}</div>')
                    elif line.startswith('@'):
                        diff_html.append(f'<div class="diff-header">{html_parser.escape(line)}</div>')
                    else:
                        diff_html.append(f'<div class="diff-context">{html_parser.escape(line)}</div>')

                return ''.join(diff_html) if diff_html else '<div class="no-changes">No changes detected</div>'

            diff_content = html_diff_with_highlighting(version1.content, version2.content)

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Compare: {html_parser.escape(entry.name)}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .comparison-container {{ display: flex; gap: 20px; }}
                    .version-panel {{ flex: 1; border: 1px solid #dee2e6; border-radius: 5px; overflow: hidden; }}
                    .version-header {{ background: #e9ecef; padding: 15px; border-bottom: 1px solid #dee2e6; }}
                    .version-content {{ padding: 15px; max-height: 600px; overflow-y: auto; }}
                    .diff-container {{ flex: 1; border: 1px solid #dee2e6; border-radius: 5px; overflow: hidden; }}
                    .diff-header {{ background: #e9ecef; padding: 15px; border-bottom: 1px solid #dee2e6; }}
                    .diff-content {{ padding: 15px; max-height: 600px; overflow-y: auto; font-family: monospace; }}
                    .diff-added {{ background: #d4edda; color: #155724; padding: 2px 5px; margin: 1px 0; }}
                    .diff-removed {{ background: #f8d7da; color: #721c24; padding: 2px 5px; margin: 1px 0; }}
                    .diff-context {{ color: #6c757d; padding: 2px 5px; margin: 1px 0; }}
                    .diff-header {{ background: #fff3cd; color: #856404; padding: 5px; font-weight: bold; }}
                    .no-changes {{ color: #6c757d; font-style: italic; text-align: center; padding: 20px; }}
                    .back-button {{ margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }}
                    .btn:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Compare Versions: {html_parser.escape(entry.name)}</h1>
                    <p>Entry: {html_parser.escape(entry.name)} | Notebook: {html_parser.escape(entry.notebook_id.name)}</p>
                </div>

                <div class="comparison-container">
                    <div class="version-panel">
                        <div class="version-header">
                            <h3>Version {version1.version_number}</h3>
                            <small>Created: {version1.create_date} | {version1.word_count} words | {version1.char_count} chars</small>
                        </div>
                        <div class="version-content">
                            {version1.content or '<p><em>No content</em></p>'}
                        </div>
                    </div>

                    <div class="version-panel">
                        <div class="version-header">
                            <h3>Version {version2.version_number}</h3>
                            <small>Created: {version2.create_date} | {version2.word_count} words | {version2.char_count} chars</small>
                        </div>
                        <div class="version-content">
                            {version2.content or '<p><em>No content</em></p>'}
                        </div>
                    </div>
                </div>

                <div style="margin-top: 30px;">
                    <div class="diff-container">
                        <div class="diff-header">
                            <h3>Change Highlights</h3>
                            <small>Green = Added, Red = Removed, Gray = Unchanged</small>
                        </div>
                        <div class="diff-content">
                            {diff_content}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            return request.make_response(
                html_content.encode('utf-8'),
                headers=[('Content-Type', 'text/html; charset=utf-8')]
            )

        except Exception as e:
            _logger.error(f"Version comparison error: {e}")
            return request.not_found()

    @http.route('/journal/compare/<int:entry_id>/<int:version_id>/current', type='http', auth='user')
    def compare_with_current(self, entry_id, version_id, **kwargs):
        """Compare a version with current entry content"""
        try:
            entry = request.env['journal.entry'].browse(entry_id)
            version = request.env['journal.entry.version'].browse(version_id)

            if not all([entry.exists(), version.exists()]):
                return request.not_found()

            # HTML diff with change highlighting
            def html_diff_with_highlighting(old_html, new_html):
                # Convert HTML to plain text for diffing
                def html_to_text(html):
                    if not html:
                        return ""
                    # Simple HTML to text conversion
                    text = html.replace('<p>', '\n').replace('</p>', '\n')
                    text = re.sub(r'<[^>]+>', '', text)
                    text = html_parser.unescape(text)
                    return text

                old_text = html_to_text(old_html)
                new_text = html_to_text(new_html)

                # Generate diff
                diff = difflib.unified_diff(
                    old_text.splitlines(keepends=True),
                    new_text.splitlines(keepends=True),
                    fromfile=f'Version {version.version_number}',
                    tofile='Current Version',
                    n=3
                )

                diff_html = []
                for line in diff:
                    if line.startswith('+'):
                        diff_html.append(f'<div class="diff-added">+ {html_parser.escape(line[1:])}</div>')
                    elif line.startswith('-'):
                        diff_html.append(f'<div class="diff-removed">- {html_parser.escape(line[1:])}</div>')
                    elif line.startswith('@'):
                        diff_html.append(f'<div class="diff-header">{html_parser.escape(line)}</div>')
                    else:
                        diff_html.append(f'<div class="diff-context">{html_parser.escape(line)}</div>')

                return ''.join(diff_html) if diff_html else '<div class="no-changes">No changes detected</div>'

            diff_content = html_diff_with_highlighting(version.content, entry.content)

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Compare with Current: {html_parser.escape(entry.name)}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .comparison-container {{ display: flex; gap: 20px; }}
                    .version-panel {{ flex: 1; border: 1px solid #dee2e6; border-radius: 5px; overflow: hidden; }}
                    .version-header {{ background: #e9ecef; padding: 15px; border-bottom: 1px solid #dee2e6; }}
                    .version-content {{ padding: 15px; max-height: 600px; overflow-y: auto; }}
                    .current-version {{ border: 2px solid #28a745; }}
                    .diff-container {{ flex: 1; border: 1px solid #dee2e6; border-radius: 5px; overflow: hidden; }}
                    .diff-header {{ background: #e9ecef; padding: 15px; border-bottom: 1px solid #dee2e6; }}
                    .diff-content {{ padding: 15px; max-height: 600px; overflow-y: auto; font-family: monospace; }}
                    .diff-added {{ background: #d4edda; color: #155724; padding: 2px 5px; margin: 1px 0; }}
                    .diff-removed {{ background: #f8d7da; color: #721c24; padding: 2px 5px; margin: 1px 0; }}
                    .diff-context {{ color: #6c757d; padding: 2px 5px; margin: 1px 0; }}
                    .diff-header {{ background: #fff3cd; color: #856404; padding: 5px; font-weight: bold; }}
                    .no-changes {{ color: #6c757d; font-style: italic; text-align: center; padding: 20px; }}
                    .back-button {{ margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }}
                    .btn:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Compare with Current: {html_parser.escape(entry.name)}</h1>
                    <p>Entry: {html_parser.escape(entry.name)} | Notebook: {html_parser.escape(entry.notebook_id.name)}</p>
                </div>

                <div class="comparison-container">
                    <div class="version-panel">
                        <div class="version-header">
                            <h3>Version {version.version_number}</h3>
                            <small>Created: {version.create_date} | {version.word_count} words | {version.char_count} chars</small>
                        </div>
                        <div class="version-content">
                            {version.content or '<p><em>No content</em></p>'}
                        </div>
                    </div>

                    <div class="version-panel current-version">
                        <div class="version-header">
                            <h3>Current Version (v{entry.current_version - 1})</h3>
                            <small>Latest • {entry.word_count} words | {entry.char_count} chars</small>
                        </div>
                        <div class="version-content">
                            {entry.content or '<p><em>No content</em></p>'}
                        </div>
                    </div>
                </div>

                <div style="margin-top: 30px;">
                    <div class="diff-container">
                        <div class="diff-header">
                            <h3>Change Highlights</h3>
                            <small>Green = Added in current, Red = Removed from version, Gray = Unchanged</small>
                        </div>
                        <div class="diff-content">
                            {diff_content}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            return request.make_response(
                html_content.encode('utf-8'),
                headers=[('Content-Type', 'text/html; charset=utf-8')]
            )

        except Exception as e:
            _logger.error(f"Current version comparison error: {e}")
            return request.not_found()