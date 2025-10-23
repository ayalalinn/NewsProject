import gradio as gr
import httpx

API_BASE = "http://127.0.0.1:8000"  # בפיתוח; בפרודקשן תעדכני לכתובת האמיתית

async def fetch_article(article_id: str):
    if not article_id:
        return "❌ אין מזהה ידיעה", "", "", None, "", ""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{API_BASE}/api/article/{article_id}")
    if r.status_code != 200:
        return f"❌ הידיעה {article_id} לא נמצאה", "", "", None, "", ""
    a = r.json()
    tags_html = " ".join([f"<span class='tag'>{t}</span>" for t in (a.get("entities") or [])])
    return a["title"], a["published_at"], a["category"], a["image_url"], a["content"], tags_html

def build_ui():
    with gr.Blocks(css="""
        body { direction: rtl; font-family: Arial, sans-serif; }
        .wrap { max-width: 900px; margin: auto; }
        .card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.06); }
        .meta { color:#555; margin:.5rem 0 1rem; }
        .tag { background:#eef; padding:6px 10px; border-radius:8px; margin:0 6px 6px 0; display:inline-block; font-size:14px; }
    """) as demo:
        gr.Markdown("## 📰 פירוט ידיעה", elem_classes="wrap")
        with gr.Group(elem_classes="wrap card"):
            with gr.Row():
                article_id = gr.Textbox(label="מזהה ידיעה (ID)", placeholder="למשל: 123", scale=3)
                load_btn = gr.Button("טעני ידיעה", scale=1)

            title = gr.Textbox(label="כותרת", interactive=False)
            with gr.Row():
                date = gr.Textbox(label="תאריך", interactive=False)
                category = gr.Textbox(label="נושא (Zero-Shot)", interactive=False)
            image = gr.Image(label="תמונה", interactive=False)
            content = gr.Textbox(label="תוכן הידיעה", lines=8, interactive=False)
            tags = gr.HTML(label="תגיות (NER)")

        # לחיצה על הכפתור
        load_btn.click(fetch_article, inputs=[article_id],
                       outputs=[title, date, category, image, content, tags])

        # טעינה אוטומטית אם הגיעו עם ?id= ב-URL (Deep-Link מהפיד)
        def on_load(req: gr.Request):
            return req.query_params.get("id", "") if req and req.query_params else ""
        demo.load(on_load, inputs=None, outputs=[article_id]).then(
            fetch_article, inputs=[article_id],
            outputs=[title, date, category, image, content, tags]
        )

    return demo

# הרצה עצמאית (לא חובה כשעובדים דרך FastAPI)
if __name__ == "__main__":
    build_ui().launch(server_name="127.0.0.1", server_port=7860)
