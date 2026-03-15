"""PDF generation service with graceful fallbacks."""
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFService:
    """Generate PDFs from HTML with multiple backend support."""

    def __init__(self):
        self._backend = self._detect_backend()
        logger.info(f"PDF service initialized with backend: {self._backend}")

    def _detect_backend(self) -> str:
        """Detect available PDF backend."""
        try:
            import weasyprint  # noqa
            return "weasyprint"
        except ImportError:
            pass
        try:
            from xhtml2pdf import pisa  # noqa
            return "xhtml2pdf"
        except ImportError:
            pass
        return "none"

    def html_to_pdf(self, html: str, title: str = "Document") -> Optional[bytes]:
        """Convert HTML to PDF bytes."""
        if self._backend == "weasyprint":
            return self._weasyprint_convert(html, title)
        elif self._backend == "xhtml2pdf":
            return self._xhtml2pdf_convert(html, title)
        else:
            logger.warning("No PDF backend available. Install weasyprint or xhtml2pdf.")
            return None

    def _weasyprint_convert(self, html: str, title: str) -> bytes:
        """Convert using WeasyPrint."""
        import weasyprint
        doc = weasyprint.HTML(string=html)
        return doc.write_pdf()

    def _xhtml2pdf_convert(self, html: str, title: str) -> bytes:
        """Convert using xhtml2pdf (pure Python)."""
        from xhtml2pdf import pisa
        result = io.BytesIO()
        # Add page size, encoding, and page numbering for Indian legal documents
        enhanced_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2.5cm 2cm 3cm 2cm;
                    @frame header {{
                        -pdf-frame-content: page-header;
                        top: 0.5cm;
                        margin-left: 2cm;
                        margin-right: 2cm;
                        height: 1cm;
                    }}
                    @frame footer {{
                        -pdf-frame-content: page-footer;
                        bottom: 0.5cm;
                        margin-left: 2cm;
                        margin-right: 2cm;
                        height: 1.5cm;
                    }}
                }}
                body {{ font-family: 'Helvetica', 'Arial', sans-serif; font-size: 11pt; line-height: 1.5; color: #1a1a1a; }}
                h1 {{ font-size: 18pt; color: #111; margin-bottom: 10pt; }}
                h2 {{ font-size: 14pt; color: #222; margin-top: 15pt; }}
                h3 {{ font-size: 12pt; color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 10pt; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .signature-block {{ margin-top: 30pt; page-break-inside: avoid; }}
                #page-header {{ font-size: 8pt; color: #999; text-align: center; }}
                #page-footer {{ font-size: 8pt; color: #999; text-align: center; }}
            </style>
        </head>
        <body>
        <div id="page-header">{title}</div>
        <div id="page-footer">
            Page <pdf:pagenumber /> of <pdf:pagecount /> &mdash; CMS India
        </div>
        {html}
        </body>
        </html>
        """
        pisa.CreatePDF(enhanced_html, dest=result)
        return result.getvalue()

    @property
    def is_available(self) -> bool:
        """Check if PDF generation is available."""
        return self._backend != "none"


# Module-level singleton
pdf_service = PDFService()
