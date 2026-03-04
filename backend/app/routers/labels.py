"""Label generation: POST /labels/generate returns PDF of QR labels for given asset IDs."""
import io
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Asset, LabelBatch
from app.schemas import LabelGenerateRequest, LabelBatchResponse
from app.utils.dependencies import CurrentUser, DBSession

router = APIRouter()
settings = get_settings()


def _make_qr_pdf(asset_tags: list[str]) -> bytes:
    """Generate a simple PDF with one QR (as text placeholder) per label. Uses reportlab if available."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.graphics.barcode import qr
        from reportlab.graphics.shapes import Drawing
    except ImportError:
        # Fallback: minimal PDF with text only (no QR graphic)
        import struct
        buf = io.BytesIO()
        lines = []
        for tag in asset_tags:
            lines.append(f"Asset: {tag}")
        text = "\n".join(lines)
        # Minimal PDF content
        buf.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        buf.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        buf.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n")
        buf.write(b"4 0 obj\n<< /Length %d >>\nstream\n" % (len(text) + 50))
        buf.write(b"BT /F1 12 Tf 72 720 Td (" + text.encode("latin-1", errors="replace") + b") Tj ET\nendstream\nendobj\n")
        buf.write(b"xref\n0 5\n0000000000 65535 f \n")
        buf.write(b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n")
        return buf.getvalue()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    labels_per_row = 3
    label_w = width / labels_per_row
    label_h = 40 * mm
    row = 0
    col = 0
    for tag in asset_tags:
        x = col * label_w + 15 * mm
        y = height - (row + 1) * label_h - 10 * mm
        try:
            qr_code = qr.QrCodeWidget(tag)
            bounds = qr_code.getBounds()
            d = Drawing(30 * mm, 30 * mm)
            d.add(qr_code)
            d.drawOn(c, x, y)
        except Exception:
            c.drawString(x, y + 10 * mm, f"QR: {tag}")
        c.drawString(x, y - 5 * mm, tag)
        col += 1
        if col >= labels_per_row:
            col = 0
            row += 1
            if (row + 1) * label_h > height - 20 * mm:
                c.showPage()
                row = 0
    c.save()
    return buf.getvalue()


@router.post("/generate", response_model=LabelBatchResponse)
async def generate_labels(
    data: LabelGenerateRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """Generate PDF with QR labels for the given asset IDs. Returns batch record; PDF can be downloaded via GET."""
    if not data.asset_ids:
        raise HTTPException(400, "asset_ids cannot be empty")
    result = await db.execute(select(Asset).where(Asset.id.in_(data.asset_ids)))
    assets = list(result.scalars().all())
    if len(assets) != len(data.asset_ids):
        found = {a.id for a in assets}
        missing = set(data.asset_ids) - found
        raise HTTPException(404, f"Assets not found: {missing}")
    asset_tags = [a.asset_tag for a in assets]
    pdf_bytes = _make_qr_pdf(asset_tags)
    out_dir = Path(settings.upload_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"labels_{uuid.uuid4().hex}.pdf"
    file_path = out_dir / safe_name
    file_path.write_bytes(pdf_bytes)
    batch = LabelBatch(
        name=safe_name,
        file_path=safe_name,
        asset_count=len(assets),
        created_by=current_user.id,
    )
    db.add(batch)
    await db.flush()
    await db.refresh(batch)
    return batch


@router.get("/{batch_id}/download")
async def download_labels(
    batch_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """Stream the generated PDF for a label batch."""
    from sqlalchemy import select
    r = await db.execute(select(LabelBatch).where(LabelBatch.id == batch_id))
    batch = r.scalar_one_or_none()
    if not batch or not batch.file_path:
        raise HTTPException(404, "Label batch not found")
    path = Path(settings.upload_dir) / batch.file_path
    if not path.exists():
        raise HTTPException(404, "File no longer available")
    pdf_bytes = path.read_bytes()
    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{batch.name or "labels.pdf"}"'},
    )
