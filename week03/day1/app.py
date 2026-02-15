from flask import Flask, render_template_string

app = Flask(__name__)

HOME_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kanishka Mahanama</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* --- Animated gradient background --- */
        body::before {
            content: '';
            position: fixed;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 20% 50%, rgba(56,189,248,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(139,92,246,0.08) 0%, transparent 50%),
                        radial-gradient(circle at 50% 80%, rgba(16,185,129,0.06) 0%, transparent 50%);
            animation: bgShift 12s ease-in-out infinite alternate;
            z-index: -1;
        }
        @keyframes bgShift {
            0%   { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(30px, -20px) rotate(3deg); }
        }

        /* --- Fade-up animation --- */
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .fade-up {
            opacity: 0;
            animation: fadeUp 0.7s ease-out forwards;
        }

        .container { max-width: 800px; margin: 0 auto; padding: 60px 24px; }

        .header { text-align: center; margin-bottom: 48px; }
        .header h1 {
            font-size: 2.5rem; color: #f8fafc; margin-bottom: 8px;
        }
        .header .tagline {
            font-size: 1.1rem; color: #94a3b8; margin-bottom: 16px;
        }
        .header .social a {
            color: #38bdf8; text-decoration: none;
            transition: color 0.3s, text-shadow 0.3s;
        }
        .header .social a:hover {
            color: #7dd3fc;
            text-shadow: 0 0 10px rgba(56,189,248,0.5);
        }

        .section {
            background: #1e293b; border-radius: 12px;
            padding: 32px; margin-bottom: 24px;
            border: 1px solid transparent;
            transition: border-color 0.4s, box-shadow 0.4s, transform 0.3s;
        }
        .section:hover {
            border-color: rgba(56,189,248,0.3);
            box-shadow: 0 0 24px rgba(56,189,248,0.1);
            transform: translateY(-4px);
        }
        .section h2 {
            font-size: 1.3rem; color: #38bdf8; margin-bottom: 16px;
            border-bottom: 2px solid #334155; padding-bottom: 8px;
        }
        .section p { line-height: 1.7; color: #cbd5e1; }

        .skills-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 12px;
        }

        /* --- Skill tag pop-in --- */
        @keyframes popIn {
            from { opacity: 0; transform: scale(0.7); }
            to   { opacity: 1; transform: scale(1); }
        }
        .skill-tag {
            background: #334155; padding: 10px 16px; border-radius: 8px;
            text-align: center; font-size: 0.95rem; color: #e2e8f0;
            opacity: 0;
            animation: popIn 0.4s ease-out forwards;
            transition: background 0.3s, transform 0.2s, box-shadow 0.3s;
            cursor: default;
        }
        .skill-tag:nth-child(1) { animation-delay: 0.8s; }
        .skill-tag:nth-child(2) { animation-delay: 0.9s; }
        .skill-tag:nth-child(3) { animation-delay: 1.0s; }
        .skill-tag:nth-child(4) { animation-delay: 1.1s; }
        .skill-tag:nth-child(5) { animation-delay: 1.2s; }
        .skill-tag:nth-child(6) { animation-delay: 1.3s; }
        .skill-tag:nth-child(7) { animation-delay: 1.4s; }
        .skill-tag:nth-child(8) { animation-delay: 1.5s; }
        .skill-tag:hover {
            background: #38bdf8;
            color: #0f172a;
            transform: scale(1.08);
            box-shadow: 0 0 16px rgba(56,189,248,0.4);
        }

        footer {
            text-align: center; padding: 32px 0; color: #475569; font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kanishka Mahanama</h1>
            <p class="tagline">Senior IT Professional | Network Engineer | DevOps Enthusiast</p>
            <p class="social">
                <a href="https://x.com/__kanishka__" target="_blank">@__kanishka__</a>
            </p>
        </div>
        <div class="section">
            <h2>About Me</h2>
            <p>
                Senior IT Professional with over 15 years of experience in the industry.
                Skilled in networks, security, and automation, with a proven track record
                of delivering strategic outcomes for clients. Strong stakeholder engagement
                and recognized as a trusted advisor. Currently leveraging deep networking
                expertise to transition into a DevOps role with a focus on automation and
                cloud-native practices.
            </p>
        </div>
        <div class="section">
            <h2>Networking Background</h2>
            <p>
                With extensive hands-on experience as a network engineer, I have designed,
                deployed, and managed enterprise-grade network infrastructures including
                routing &amp; switching, firewalls, VPNs, and load balancers. Proficient in
                troubleshooting complex network issues across LAN, WAN, and data centre
                environments. This deep networking foundation drives my approach to
                infrastructure-as-code, cloud networking, and building reliable automated
                pipelines.
            </p>
        </div>
        <div class="section">
            <h2>Skills</h2>
            <div class="skills-grid">
                <div class="skill-tag">Azure</div>
                <div class="skill-tag">Terraform</div>
                <div class="skill-tag">Red Hat Linux</div>
                <div class="skill-tag">Cisco</div>
                <div class="skill-tag">Routing &amp; Switching</div>
                <div class="skill-tag">Firewalls &amp; VPN</div>
                <div class="skill-tag">Network Security</div>
                <div class="skill-tag">Automation</div>
            </div>
        </div>
        <footer>&copy; 2026 Kanishka Mahanama</footer>
    </div>

</body>
</html>"""


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
