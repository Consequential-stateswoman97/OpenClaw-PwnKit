import os
def generate_nginx_honeypot(payload_text: str, output_path: str = "./honeypot/"):
    os.makedirs(output_path, exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html><head><title>Python Optimization</title></head>
<body><h1>Python Guide</h1>
    <div style="color: #ffffff; font-size: 1px; opacity: 0; position: absolute; left: -9999px;">
        {payload_text}
    </div>
</body></html>"""
    with open(os.path.join(output_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[*] Honeypot generated at {output_path}index.html")