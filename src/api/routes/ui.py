# src/api/routes/ui.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()  # 可在 main.py 掛載時指定 prefix="/ui", tags=["ui"]

@router.get("/ui", response_class=HTMLResponse)
def upload_ui():
    return """
    <html>
      <head><title>AutoQM Upload</title></head>
      <body>
        <h1>AutoQM 簡易上傳介面</h1>
        <h2>預算匯入</h2>
        <form action="/budget/import" method="post" enctype="multipart/form-data">
          <input type="file" name="file" />
          <button type="submit">上傳預算</button>
        </form>
        <h2>技術規格匯入</h2>
        <form action="/specs/import" method="post" enctype="multipart/form-data">
          <input type="file" name="file" />
          <button type="submit">上傳規格</button>
        </form>
        <p>Swagger 互動文件：<a href="/docs" target="_blank">/docs</a></p>
      </body>
    </html>
    """
