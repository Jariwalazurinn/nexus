import re
import os

md_path = r"d:\nexusHackathon\nexus\CommerceOS\docs\CommerceOS_Capstone_Project_Report.md"
html_path = r"d:\nexusHackathon\nexus\CommerceOS\docs\CommerceOS_Capstone_Project_Report.html"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

def fmt(s):
    s = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.*?)\*", r"<i>\1</i>", s)
    s = re.sub(r"`(.*?)`", r"<code>\1</code>", s)
    return s

css_styles = """
<style>
  @page {
    size: A4;
    margin: 22mm 18mm 18mm 22mm;
    @bottom-right {
      content: counter(page);
    }
  }
  @media print {
    .page-break { page-break-before: always; }
    body { font-size: 10.5pt; }
    a { text-decoration: none; color: #111; }
  }
  body {
    font-family: "Times New Roman", Times, Georgia, serif;
    font-size: 11.5pt;
    line-height: 1.55;
    color: #111;
    background-color: #fff;
    margin: 0 auto;
    padding: 30px 45px;
    max-width: 860px;
    text-align: justify;
  }
  h1, h2, h3, h4 {
    font-family: "Times New Roman", Times, serif;
    color: #000;
    margin-top: 24px;
    margin-bottom: 12px;
    line-height: 1.3;
  }
  h1 { font-size: 19pt; text-align: center; text-transform: uppercase; font-weight: bold; border-bottom: 1px solid #ddd; padding-bottom: 6px; }
  h2 { font-size: 15pt; text-align: center; font-weight: bold; }
  h3 { font-size: 12.5pt; text-align: left; font-weight: bold; }
  h4 { font-size: 11.5pt; text-align: left; font-weight: bold; font-style: italic; }
  p { margin-bottom: 12px; }
  .center { text-align: center; }
  .bold { font-weight: bold; }
  hr { border: 0; border-top: 1px solid #ccc; margin: 30px 0; }
  .page-break { page-break-before: always; }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 9.5pt;
  }
  th, td {
    border: 1px solid #333;
    padding: 6px 10px;
    text-align: left;
    vertical-align: top;
  }
  th {
    background-color: #f1f3f5;
    font-weight: bold;
    text-align: center;
  }
  
  pre {
    background-color: #f8f9fa;
    border: 1px solid #aaa;
    border-radius: 4px;
    padding: 12px;
    margin: 16px 0;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.5pt;
    line-height: 1.3;
    white-space: pre-wrap;
    overflow-x: auto;
  }
  code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9.5pt;
    background-color: #f4f4f4;
    padding: 1px 4px;
    border-radius: 3px;
  }
  pre code {
    background-color: transparent;
    padding: 0;
  }
</style>
"""

lines = text.split("\n")
html_out = ["<!DOCTYPE html>", "<html>", "<head>", "<meta charset='utf-8'>", "<title>CommerceOS Capstone Project-II Report</title>", css_styles, "</head>", "<body>"]

in_code = False
code_buf = []
in_table = False
table_buf = []

for line in lines:
    if line.startswith("```"):
        if in_code:
            html_out.append("<pre><code>" + "\n".join(code_buf).replace("<", "&lt;").replace(">", "&gt;") + "</code></pre>")
            code_buf = []
            in_code = False
        else:
            in_code = True
            code_buf = []
        continue
    if in_code:
        code_buf.append(line)
        continue
    
    if line.strip().startswith("|") and line.strip().endswith("|"):
        table_buf.append(line.strip())
        in_table = True
        continue
    else:
        if in_table:
            if len(table_buf) >= 2:
                html_out.append("<table>")
                header = [fmt(c.strip()) for c in table_buf[0].split("|")[1:-1]]
                html_out.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in header) + "</tr></thead>")
                html_out.append("<tbody>")
                for row_str in table_buf[2:]:
                    row_cols = [fmt(c.strip()) for c in row_str.split("|")[1:-1]]
                    html_out.append("<tr>" + "".join(f"<td>{c}</td>" for c in row_cols) + "</tr>")
                html_out.append("</tbody></table>")
            table_buf = []
            in_table = False

    if line.strip() == "---" or "\\pagebreak" in line:
        html_out.append("<div class='page-break'></div>")
        continue

    if line.startswith("# "):
        html_out.append(f"<h1>{fmt(line[2:].strip())}</h1>")
    elif line.startswith("## "):
        html_out.append(f"<h2>{fmt(line[3:].strip())}</h2>")
    elif line.startswith("### "):
        html_out.append(f"<h3>{fmt(line[4:].strip())}</h3>")
    elif line.startswith("#### "):
        html_out.append(f"<h4>{fmt(line[5:].strip())}</h4>")
    elif line.startswith("- "):
        html_out.append(f"<li style='margin-left: 20px;'>{fmt(line[2:].strip())}</li>")
    elif line.strip() == "" or line.strip() == "<br>":
        continue
    elif line.strip().startswith("<div") or line.strip().startswith("</div>") or line.strip().startswith("<h"):
        html_out.append(line)
    else:
        html_out.append(f"<p>{fmt(line)}</p>")

if in_table and table_buf:
    html_out.append("<table>")
    header = [fmt(c.strip()) for c in table_buf[0].split("|")[1:-1]]
    html_out.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in header) + "</tr></thead>")
    html_out.append("<tbody>")
    for row_str in table_buf[2:]:
        row_cols = [fmt(c.strip()) for c in row_str.split("|")[1:-1]]
        html_out.append("<tr>" + "".join(f"<td>{c}</td>" for c in row_cols) + "</tr>")
    html_out.append("</tbody></table>")

html_out.extend(["</body>", "</html>"])

with open(html_path, "w", encoding="utf-8") as f:
    f.write("\n".join(html_out))

print(f"Generated clean HTML report at: {html_path} ({os.path.getsize(html_path)} bytes)")
