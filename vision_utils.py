import json
import html as _html
import secrets as _secrets
from IPython.display import HTML, display

def gcs_to_public_url(gcs_uri: str) -> str:
    """Convierte una URI de GCS (gs://...) a una URL pública de HTTPs."""
    if not gcs_uri or not gcs_uri.startswith('gs://'):
        return gcs_uri
    path = gcs_uri[len('gs://'):]
    return f'https://storage.googleapis.com/{path}'

def draw_boxes_html(img_uri: str, boxes, width=600):
    """Renderiza cajas sobre una imagen usando HTML/Canvas en Jupyter."""
    _img_url = gcs_to_public_url(img_uri)
    _uid = _secrets.token_hex(4)
    _style_width = '' if (width is None) else f'width:{int(width)}px;'
    _tpl = """
    <div id="viz-{UID}" style="position:relative; display:inline-block; border:1px solid #ddd;">
      <img id="img-{UID}" src="{IMG_URL}" style="display:block; {STYLE_W} max-width:100%; height:auto;"/>
      <canvas id="canvas-{UID}" style="position:absolute; left:0; top:0; pointer-events:none;"></canvas>
    </div>
    <script>
    (function(){{
      const boxes = {BOXES};
      const img = document.getElementById('img-{UID}');
      const canvas = document.getElementById('canvas-{UID}');
      function draw(){{
        const w = img.clientWidth || img.naturalWidth;
        const h = img.clientHeight || img.naturalHeight;
        if (!w || !h) {{ requestAnimationFrame(draw); return; }}
        canvas.width = w; canvas.height = h;
        canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, w, h);
        const srcW = img.naturalWidth || w; const srcH = img.naturalHeight || h;
        const sx = w / srcW; const sy = h / srcH;
        (boxes || []).forEach(b => {{
          const ptsRaw = b.points || [];
          if (!ptsRaw.length) return;
          const pts = ptsRaw.map(p => {{
            const px = (('x' in p) ? (p.x || 0) : 0);
            const py = (('y' in p) ? (p.y || 0) : 0);
            return [px * sx, py * sy];
          }});
          ctx.beginPath();
          ctx.moveTo(pts[0][0], pts[0][1]);
          for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
          if (pts.length >= 3) ctx.closePath();
          ctx.lineWidth = 3;
          ctx.strokeStyle = b.color || 'rgba(255, 0, 0, 0.9)';
          ctx.stroke();
          const parts = [];
          if (b.label) parts.push(b.label);
          if (b.score) parts.push('(' + (b.score*100).toFixed(1) + '%)');
          const txt = parts.join(' ');
          if (txt) {{
            const tx = Math.min(Math.max(pts[0][0] + 5, 2), w - 2);
            const ty = Math.max(16, pts[0][1] - 5);
            ctx.fillStyle = b.color || 'rgba(255, 0, 0, 0.9)';
            ctx.font = 'bold 14px sans-serif';
            ctx.fillText(txt, tx, ty);
          }}
        }});
      }}
      img.addEventListener('load', draw);
      window.addEventListener('resize', draw);
      if (img.complete) draw();
    }})();
    </script>
    """
    _html_out = (_tpl
        .replace('{{UID}}', _uid)
        .replace('{{IMG_URL}}', _html.escape(_img_url))
        .replace('{{STYLE_W}}', _style_width)
        .replace('{{BOXES}}', json.dumps(boxes)))
    display(HTML(_html_out))
