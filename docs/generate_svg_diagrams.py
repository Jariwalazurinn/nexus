import os

os.makedirs('docs/img', exist_ok=True)

def write_svg(filename, content):
    path = os.path.join('docs/img', filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"Generated: {path} ({len(content)} bytes)")

print("Helper defined.")
def gen_fig_3_1():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 620" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569"/>
    </marker>
  </defs>
  <text x="460" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#0f172a">Fig. 3.1 Use Case Diagram — CommerceOS Platform</text>
  <rect x="230" y="50" width="460" height="550" rx="12" fill="#f8fafc" stroke="#2563eb" stroke-width="2" stroke-dasharray="6,4"/>
  <rect x="340" y="42" width="240" height="24" rx="5" fill="#2563eb"/>
  <text x="460" y="58" text-anchor="middle" font-size="12" font-weight="bold" fill="#ffffff">CommerceOS Autonomous Boundary</text>
  <g transform="translate(60, 100)">
    <circle cx="35" cy="20" r="14" fill="#e2e8f0" stroke="#0f172a" stroke-width="2"/>
    <line x1="35" y1="34" x2="35" y2="70" stroke="#0f172a" stroke-width="2"/>
    <line x1="15" y1="48" x2="55" y2="48" stroke="#0f172a" stroke-width="2"/>
    <line x1="35" y1="70" x2="18" y2="100" stroke="#0f172a" stroke-width="2"/>
    <line x1="35" y1="70" x2="52" y2="100" stroke="#0f172a" stroke-width="2"/>
    <text x="35" y="118" text-anchor="middle" font-size="11" font-weight="bold" fill="#0f172a">Operations Manager</text>
  </g>
  <g transform="translate(60, 270)">
    <circle cx="35" cy="20" r="14" fill="#e2e8f0" stroke="#0f172a" stroke-width="2"/>
    <line x1="35" y1="34" x2="35" y2="70" stroke="#0f172a" stroke-width="2"/>
    <line x1="15" y1="48" x2="55" y2="48" stroke="#0f172a" stroke-width="2"/>
    <line x1="35" y1="70" x2="18" y2="100" stroke="#0f172a" stroke-width="2"/>
    <line x1="35" y1="70" x2="52" y2="100" stroke="#0f172a" stroke-width="2"/>
    <text x="35" y="118" text-anchor="middle" font-size="11" font-weight="bold" fill="#0f172a">Domain Admin</text>
    <text x="35" y="132" text-anchor="middle" font-size="9" fill="#64748b">(Orders/Inventory/CS)</text>
  </g>
  <g transform="translate(60, 440)">
    <rect x="8" y="15" width="54" height="54" rx="8" fill="#e0f2fe" stroke="#0284c7" stroke-width="2"/>
    <polygon points="28,32 46,42 28,52" fill="#0284c7"/>
    <text x="35" y="86" text-anchor="middle" font-size="11" font-weight="bold" fill="#0369a1">Replay Engine</text>
    <text x="35" y="99" text-anchor="middle" font-size="9" fill="#64748b">(Simulated Clock T)</text>
  </g>
  <g transform="translate(790, 160)">
    <circle cx="35" cy="20" r="14" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
    <line x1="35" y1="34" x2="35" y2="70" stroke="#dc2626" stroke-width="2"/>
    <line x1="15" y1="48" x2="55" y2="48" stroke="#dc2626" stroke-width="2"/>
    <line x1="35" y1="70" x2="18" y2="100" stroke="#dc2626" stroke-width="2"/>
    <line x1="35" y1="70" x2="52" y2="100" stroke="#dc2626" stroke-width="2"/>
    <text x="35" y="118" text-anchor="middle" font-size="11" font-weight="bold" fill="#991b1b">Super Admin</text>
    <text x="35" y="132" text-anchor="middle" font-size="9" fill="#64748b">(HITL Approver)</text>
  </g>
  <g transform="translate(790, 370)">
    <circle cx="35" cy="20" r="14" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <line x1="35" y1="34" x2="35" y2="70" stroke="#d97706" stroke-width="2"/>
    <line x1="15" y1="48" x2="55" y2="48" stroke="#d97706" stroke-width="2"/>
    <line x1="35" y1="70" x2="18" y2="100" stroke="#d97706" stroke-width="2"/>
    <line x1="35" y1="70" x2="52" y2="100" stroke="#d97706" stroke-width="2"/>
    <text x="35" y="118" text-anchor="middle" font-size="11" font-weight="bold" fill="#b45309">Agent Swarm</text>
    <text x="35" y="132" text-anchor="middle" font-size="9" fill="#64748b">(LangGraph ReAct)</text>
  </g>
  <ellipse cx="460" cy="95" rx="140" ry="20" fill="#eff6ff" stroke="#2563eb" stroke-width="1.6"/>
  <text x="460" y="100" text-anchor="middle" font-size="11" font-weight="600" fill="#1e40af">Control Replay Clock &amp; Speed</text>
  <ellipse cx="360" cy="155" rx="115" ry="20" fill="#eff6ff" stroke="#2563eb" stroke-width="1.6"/>
  <text x="360" y="160" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">View 6-Domain Operations Grid</text>
  <ellipse cx="565" cy="155" rx="110" ry="20" fill="#eff6ff" stroke="#2563eb" stroke-width="1.6"/>
  <text x="565" y="160" text-anchor="middle" font-size="10.5" font-weight="600" fill="#1e40af">Trigger Domain Sweep</text>
  <ellipse cx="460" cy="215" rx="130" ry="20" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.6"/>
  <text x="460" y="220" text-anchor="middle" font-size="10.5" font-weight="600" fill="#166534">Audit Backlog &amp; RMA Eligibility</text>
  <ellipse cx="360" cy="275" rx="110" ry="20" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.6"/>
  <text x="360" y="280" text-anchor="middle" font-size="10.5" font-weight="600" fill="#166534">Monitor Stockouts &amp; ROP/EOQ</text>
  <ellipse cx="565" cy="275" rx="110" ry="20" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.6"/>
  <text x="565" y="280" text-anchor="middle" font-size="10.5" font-weight="600" fill="#166534">Detect Pricing &amp; Margin Leaks</text>
  <ellipse cx="460" cy="335" rx="135" ry="20" fill="#fef2f2" stroke="#dc2626" stroke-width="1.6"/>
  <text x="460" y="340" text-anchor="middle" font-size="10.5" font-weight="600" fill="#991b1b">Resolve Cross-Domain Conflicts</text>
  <ellipse cx="360" cy="395" rx="115" ry="20" fill="#fef2f2" stroke="#dc2626" stroke-width="1.6"/>
  <text x="360" y="400" text-anchor="middle" font-size="10.5" font-weight="600" fill="#991b1b">Evaluate HITL Action Policy</text>
  <ellipse cx="565" cy="395" rx="110" ry="20" fill="#fffbeb" stroke="#d97706" stroke-width="1.6"/>
  <text x="565" y="400" text-anchor="middle" font-size="10.5" font-weight="600" fill="#92400e">Approve / Reject Action Queue</text>
  <ellipse cx="460" cy="460" rx="130" ry="20" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.6"/>
  <text x="460" y="465" text-anchor="middle" font-size="10.5" font-weight="600" fill="#5b21b6">Query Natural Language Text-to-SQL</text>
  <ellipse cx="460" cy="525" rx="130" ry="20" fill="#faf5ff" stroke="#9333ea" stroke-width="1.6"/>
  <text x="460" y="530" text-anchor="middle" font-size="10.5" font-weight="600" fill="#6b21a8">Generate In-Memory PDF Invoices</text>
  <line x1="140" y1="150" x2="330" y2="100" stroke="#64748b" stroke-width="1.4"/>
  <line x1="140" y1="150" x2="250" y2="155" stroke="#64748b" stroke-width="1.4"/>
  <line x1="140" y1="150" x2="340" y2="215" stroke="#64748b" stroke-width="1.4"/>
  <line x1="140" y1="320" x2="255" y2="275" stroke="#64748b" stroke-width="1.4"/>
  <line x1="140" y1="320" x2="340" y2="460" stroke="#64748b" stroke-width="1.4"/>
  <line x1="140" y1="320" x2="340" y2="525" stroke="#64748b" stroke-width="1.4"/>
  <line x1="130" y1="480" x2="340" y2="105" stroke="#0284c7" stroke-width="1.4"/>
  <line x1="130" y1="480" x2="255" y2="285" stroke="#0284c7" stroke-width="1.4"/>
  <line x1="785" y1="210" x2="675" y2="395" stroke="#dc2626" stroke-width="1.4"/>
  <line x1="785" y1="210" x2="590" y2="525" stroke="#dc2626" stroke-width="1.4"/>
  <line x1="785" y1="420" x2="595" y2="335" stroke="#d97706" stroke-width="1.4"/>
  <line x1="785" y1="420" x2="675" y2="275" stroke="#d97706" stroke-width="1.4"/>
  <line x1="785" y1="420" x2="590" y2="215" stroke="#d97706" stroke-width="1.4"/>
  <line x1="785" y1="420" x2="675" y2="155" stroke="#d97706" stroke-width="1.4"/>
</svg>"""
    write_svg("fig_3_1_use_case.svg", svg)

gen_fig_3_1()
def gen_fig_3_2():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 540" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="sar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#1e293b"/>
    </marker>
    <marker id="sret" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
    </marker>
    <marker id="sws" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
  </defs>
  <text x="460" y="28" text-anchor="middle" font-size="17" font-weight="bold" fill="#0f172a">Fig. 3.2 Sequence Diagram — Agent Analysis &amp; WebSocket Fan-Out</text>
  <rect x="25" y="45" width="105" height="32" rx="6" fill="#3b82f6"/>
  <text x="77" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#ffffff">User (SPA)</text>
  <line x1="77" y1="77" x2="77" y2="500" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <rect x="175" y="45" width="115" height="32" rx="6" fill="#0284c7"/>
  <text x="232" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#ffffff">FastAPI API</text>
  <line x1="232" y1="77" x2="232" y2="500" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <rect x="330" y="45" width="125" height="32" rx="6" fill="#8b5cf6"/>
  <text x="392" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#ffffff">LangGraph Agent</text>
  <line x1="392" y1="77" x2="392" y2="500" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <rect x="495" y="45" width="115" height="32" rx="6" fill="#059669"/>
  <text x="552" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#ffffff">PostgreSQL DB</text>
  <line x1="552" y1="77" x2="552" y2="500" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <rect x="650" y="45" width="115" height="32" rx="6" fill="#d97706"/>
  <text x="707" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#ffffff">Guarded LLM</text>
  <line x1="707" y1="77" x2="707" y2="500" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <rect x="800" y="45" width="105" height="32" rx="6" fill="#dc2626"/>
  <text x="852" y="66" text-anchor="middle" font-size="11.5" font-weight="bold" fill="#ffffff">Redis Bus</text>
  <line x1="852" y1="77" x2="852" y2="500" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <rect x="72" y="95" width="10" height="380" fill="#e2e8f0"/>
  <rect x="227" y="100" width="10" height="365" fill="#bae6fd"/>
  <rect x="387" y="140" width="10" height="280" fill="#ddd6fe"/>
  <rect x="547" y="160" width="10" height="55" fill="#a7f3d0"/>
  <rect x="702" y="235" width="10" height="45" fill="#fde68a"/>
  <rect x="547" y="360" width="10" height="35" fill="#a7f3d0"/>
  <rect x="847" y="405" width="10" height="70" fill="#fecaca"/>
  <line x1="82" y1="105" x2="227" y2="105" stroke="#1e293b" stroke-width="1.8" marker-end="url(#sar)"/>
  <text x="155" y="98" text-anchor="middle" font-size="10" font-weight="600" fill="#1e293b">1: POST /analyze (JWT)</text>
  <path d="M 237 120 C 265 115, 265 135, 237 137" stroke="#0284c7" stroke-width="1.5" fill="none" marker-end="url(#sar)"/>
  <text x="270" y="130" font-size="9.5" fill="#0369a1">2: Verify RBAC</text>
  <line x1="237" y1="145" x2="387" y2="145" stroke="#1e293b" stroke-width="1.8" marker-end="url(#sar)"/>
  <text x="310" y="138" text-anchor="middle" font-size="10" font-weight="600" fill="#1e293b">3: run_analysis(exec_id)</text>
  <line x1="397" y1="165" x2="547" y2="165" stroke="#1e293b" stroke-width="1.8" marker-end="url(#sar)"/>
  <text x="470" y="158" text-anchor="middle" font-size="10" font-weight="600" fill="#1e293b">4: SELECT orders WHERE ts &lt;= T</text>
  <line x1="547" y1="205" x2="397" y2="205" stroke="#64748b" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#sret)"/>
  <text x="470" y="198" text-anchor="middle" font-size="9.5" fill="#475569">5: Return Raw Telemetry Data</text>
  <line x1="397" y1="240" x2="702" y2="240" stroke="#1e293b" stroke-width="1.8" marker-end="url(#sar)"/>
  <text x="550" y="233" text-anchor="middle" font-size="10" font-weight="600" fill="#1e293b">6: Triage Intent &amp; Extract Entities</text>
  <line x1="702" y1="275" x2="397" y2="275" stroke="#64748b" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#sret)"/>
  <text x="550" y="268" text-anchor="middle" font-size="9.5" fill="#475569">7: Structured Plan &amp; Parameters</text>
  <path d="M 397 300 C 435 290, 435 330, 397 335" stroke="#8b5cf6" stroke-width="1.8" fill="none" marker-end="url(#sar)"/>
  <text x="440" y="315" font-size="9.5" font-weight="bold" fill="#6d28d9">8: Compute Z-Score, MAD,</text>
  <text x="440" y="330" font-size="9.5" font-weight="bold" fill="#6d28d9">Tukey Fences &amp; ROP/EOQ</text>
  <line x1="397" y1="365" x2="547" y2="365" stroke="#1e293b" stroke-width="1.8" marker-end="url(#sar)"/>
  <text x="470" y="358" text-anchor="middle" font-size="10" font-weight="600" fill="#1e293b">9: INSERT agent_runs, findings</text>
  <line x1="397" y1="410" x2="847" y2="410" stroke="#dc2626" stroke-width="1.8" marker-end="url(#sar)"/>
  <text x="620" y="403" text-anchor="middle" font-size="10" font-weight="600" fill="#b91c1c">10: PUBLISH commerceos:events</text>
  <line x1="387" y1="430" x2="237" y2="430" stroke="#64748b" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#sret)"/>
  <text x="310" y="423" text-anchor="middle" font-size="9.5" fill="#475569">11: Return Agent Snapshot</text>
  <line x1="227" y1="455" x2="82" y2="455" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#sar)"/>
  <text x="155" y="448" text-anchor="middle" font-size="10" font-weight="bold" fill="#15803d">12: 200 OK + Findings JSON</text>
  <path d="M 847 470 C 780 490, 240 500, 82 480" stroke="#2563eb" stroke-width="2" fill="none" marker-end="url(#sws)"/>
  <text x="460" y="495" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#1d4ed8">13: WebSocket Live Stream Push to Connected Clients</text>
</svg>"""
    write_svg("fig_3_2_sequence.svg", svg)

gen_fig_3_2()
def gen_fig_3_3():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 620" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="aar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155"/>
    </marker>
  </defs>
  <text x="460" y="28" text-anchor="middle" font-size="17" font-weight="bold" fill="#0f172a">Fig. 3.3 Activity Diagram — Autonomous Operations Pipeline</text>
  <circle cx="460" cy="58" r="13" fill="#0f172a"/>
  <rect x="350" y="95" width="220" height="34" rx="7" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.8"/>
  <text x="460" y="117" text-anchor="middle" font-size="11" font-weight="600" fill="#0369a1">Synchronize Simulated Clock T</text>
  <line x1="460" y1="71" x2="460" y2="95" stroke="#334155" stroke-width="1.8" marker-end="url(#aar)"/>
  <rect x="140" y="150" width="640" height="6" rx="3" fill="#0f172a"/>
  <line x1="460" y1="129" x2="460" y2="150" stroke="#334155" stroke-width="1.8" marker-end="url(#aar)"/>
  <rect x="120" y="178" width="115" height="40" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="177" y="195" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#1e293b">Orders Agent</text>
  <text x="177" y="210" text-anchor="middle" font-size="9" fill="#64748b">Backlog &amp; RMA</text>
  <line x1="177" y1="156" x2="177" y2="178" stroke="#334155" stroke-width="1.5" marker-end="url(#aar)"/>
  <rect x="255" y="178" width="115" height="40" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="312" y="195" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#1e293b">Inventory Agent</text>
  <text x="312" y="210" text-anchor="middle" font-size="9" fill="#64748b">Stock &amp; ROP/EOQ</text>
  <line x1="312" y1="156" x2="312" y2="178" stroke="#334155" stroke-width="1.5" marker-end="url(#aar)"/>
  <rect x="390" y="178" width="115" height="40" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="447" y="195" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#1e293b">Logistics Agent</text>
  <text x="447" y="210" text-anchor="middle" font-size="9" fill="#64748b">Transit &amp; SLA</text>
  <line x1="447" y1="156" x2="447" y2="178" stroke="#334155" stroke-width="1.5" marker-end="url(#aar)"/>
  <rect x="525" y="178" width="115" height="40" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="582" y="195" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#1e293b">Pricing Agent</text>
  <text x="582" y="210" text-anchor="middle" font-size="9" fill="#64748b">Margin Leakage</text>
  <line x1="582" y1="156" x2="582" y2="178" stroke="#334155" stroke-width="1.5" marker-end="url(#aar)"/>
  <rect x="660" y="178" width="115" height="40" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="717" y="195" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#1e293b">Marketing Agent</text>
  <text x="717" y="210" text-anchor="middle" font-size="9" fill="#64748b">RFM Segments</text>
  <line x1="717" y1="156" x2="717" y2="178" stroke="#334155" stroke-width="1.5" marker-end="url(#aar)"/>
  <rect x="140" y="238" width="640" height="6" rx="3" fill="#0f172a"/>
  <line x1="177" y1="218" x2="177" y2="238" stroke="#334155" stroke-width="1.5"/>
  <line x1="312" y1="218" x2="312" y2="238" stroke="#334155" stroke-width="1.5"/>
  <line x1="447" y1="218" x2="447" y2="238" stroke="#334155" stroke-width="1.5"/>
  <line x1="582" y1="218" x2="582" y2="238" stroke="#334155" stroke-width="1.5"/>
  <line x1="717" y1="218" x2="717" y2="238" stroke="#334155" stroke-width="1.5"/>
  <rect x="340" y="265" width="240" height="36" rx="7" fill="#fef3c7" stroke="#d97706" stroke-width="1.8"/>
  <text x="460" y="287" text-anchor="middle" font-size="11" font-weight="600" fill="#92400e">Run Modified Z-Score &amp; MAD Profiler</text>
  <line x1="460" y1="244" x2="460" y2="265" stroke="#334155" stroke-width="1.8" marker-end="url(#aar)"/>
  <polygon points="460,320 520,348 460,376 400,348" fill="#ffffff" stroke="#d97706" stroke-width="1.8"/>
  <text x="460" y="352" text-anchor="middle" font-size="10" font-weight="bold" fill="#78350f">Anomaly?</text>
  <line x1="460" y1="301" x2="460" y2="320" stroke="#334155" stroke-width="1.8" marker-end="url(#aar)"/>
  <line x1="520" y1="348" x2="630" y2="348" stroke="#16a34a" stroke-width="1.8" marker-end="url(#aar)"/>
  <text x="560" y="341" font-size="9.5" font-weight="bold" fill="#15803d">[No]</text>
  <rect x="630" y="330" width="150" height="36" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
  <text x="705" y="352" text-anchor="middle" font-size="10" font-weight="600" fill="#166534">Log Clean Telemetry</text>
  <line x1="460" y1="376" x2="460" y2="405" stroke="#dc2626" stroke-width="1.8" marker-end="url(#aar)"/>
  <text x="475" y="394" font-size="10" font-weight="bold" fill="#b91c1c">[Yes]</text>
  <rect x="330" y="405" width="260" height="36" rx="7" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.8"/>
  <text x="460" y="427" text-anchor="middle" font-size="10.5" font-weight="600" fill="#4c1d95">Cross-Domain Correlation &amp; Conflict Resolver</text>
  <polygon points="460,465 520,492 460,519 400,492" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8"/>
  <text x="460" y="496" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#4c1d95">Policy Mode?</text>
  <line x1="460" y1="441" x2="460" y2="465" stroke="#334155" stroke-width="1.8" marker-end="url(#aar)"/>
  <line x1="400" y1="492" x2="250" y2="492" stroke="#2563eb" stroke-width="1.8" marker-end="url(#aar)"/>
  <text x="310" y="485" font-size="9.5" font-weight="bold" fill="#1d4ed8">[Mode == AUTO]</text>
  <rect x="115" y="474" width="135" height="36" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
  <text x="182" y="491" text-anchor="middle" font-size="10" font-weight="bold" fill="#1e40af">Self-Execute Action</text>
  <text x="182" y="504" text-anchor="middle" font-size="8.5" fill="#3b82f6">(Reservation Rebalance)</text>
  <line x1="520" y1="492" x2="650" y2="492" stroke="#ea580c" stroke-width="1.8" marker-end="url(#aar)"/>
  <text x="540" y="485" font-size="9.5" font-weight="bold" fill="#c2410c">[Mode == HITL]</text>
  <rect x="650" y="474" width="150" height="36" rx="6" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5"/>
  <text x="725" y="491" text-anchor="middle" font-size="10" font-weight="bold" fill="#9a3412">Queue for Approval</text>
  <text x="725" y="504" text-anchor="middle" font-size="8.5" fill="#ea580c">(Admin Authorization)</text>
  <line x1="182" y1="510" x2="182" y2="560" stroke="#334155" stroke-width="1.5"/>
  <line x1="725" y1="510" x2="725" y2="560" stroke="#334155" stroke-width="1.5"/>
  <line x1="705" y1="366" x2="705" y2="560" stroke="#334155" stroke-width="1.5"/>
  <line x1="182" y1="560" x2="725" y2="560" stroke="#334155" stroke-width="1.5"/>
  <line x1="460" y1="560" x2="460" y2="585" stroke="#334155" stroke-width="1.5" marker-end="url(#aar)"/>
  <circle cx="460" cy="597" r="11" fill="#ffffff" stroke="#0f172a" stroke-width="2"/>
  <circle cx="460" cy="597" r="6" fill="#0f172a"/>
</svg>"""
    write_svg("fig_3_3_activity.svg", svg)

gen_fig_3_3()
