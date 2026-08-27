import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Web AimLab", layout="centered")

st.title("🎯 Web AimLab (Streamlit Edition)")
st.caption("화면에 나타나는 타겟을 클릭하세요! 중간에 나오는 섬광탄(Flash)은 고개를 돌리거나(마우스 이탈) 회피해야 합니다.")

# HTML5 / JavaScript 기반 에임 연습 게임 코드
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            user-select: none;
        }
        #gameCanvas {
            background-color: #2b2b2b;
            border: 3px solid #444;
            cursor: crosshair;
            display: block;
            margin: 10px auto;
        }
        .info-panel {
            font-size: 18px;
            margin-bottom: 5px;
        }
        #flashOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: white;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.1s;
        }
        #warningText {
            color: #ffcc00;
            font-weight: bold;
            font-size: 24px;
            height: 30px;
        }
    </style>
</head>
<body>
    <div class="info-panel">
        점수: <span id="score">0</span> | 명중률: <span id="accuracy">100</span>%
    </div>
    <div id="warningText"></div>
    <div style="position: relative; display: inline-block;">
        <canvas id="gameCanvas" width="700" height="450"></canvas>
        <div id="flashOverlay"></div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const accuracyEl = document.getElementById('accuracy');
        const warningEl = document.getElementById('warningText');
        const flashOverlay = document.getElementById('flashOverlay');

        let score = 0;
        let totalShots = 0;
        let hits = 0;

        // 타겟 설정
        let targets = [];
        const targetCount = 3;

        // 섬광탄 설정
        let flashActive = false;
        let flashWarning = false;
        let isMouseOverCanvas = false;

        class Target {
            constructor() {
                this.radius = 20;
                this.x = Math.random() * (canvas.width - this.radius * 2) + this.radius;
                this.y = Math.random() * (canvas.height - this.radius * 2) + this.radius;
                this.dx = (Math.random() - 0.5) * 4;
                this.dy = (Math.random() - 0.5) * 4;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = '#00d2ff';
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#ffffff';
                ctx.stroke();
                ctx.closePath();
            }

            update() {
                this.x += this.dx;
                this.y += this.dy;

                if (this.x - this.radius < 0 || this.x + this.radius > canvas.width) this.dx *= -1;
                if (this.y - this.radius < 0 || this.y + this.radius > canvas.height) this.dy *= -1;

                this.draw();
            }
        }

        // 초기 타겟 생성
        for (let i = 0; i < targetCount; i++) {
            targets.push(new Target());
        }

        // 사격 클릭 이벤트
        canvas.addEventListener('mousedown', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            totalShots++;
            let hit = false;

            for (let i = 0; i < targets.length; i++) {
                const t = targets[i];
                const dist = Math.hypot(mouseX - t.x, mouseY - t.y);

                if (dist < t.radius) {
                    score += 100;
                    hits++;
                    hit = true;
                    targets[i] = new Target(); // 맞춘 타겟 재생성
                    break;
                }
            }

            updateStats();
        });

        canvas.addEventListener('mouseenter', () => isMouseOverCanvas = true);
        canvas.addEventListener('mouseleave', () => isMouseOverCanvas = false);

        function updateStats() {
            scoreEl.innerText = score;
            const acc = totalShots > 0 ? ((hits / totalShots) * 100).toFixed(1) : 100;
            accuracyEl.innerText = acc;
        }

        // 주기적 섬광탄 이벤트 (8초마다 발생)
        setInterval(() => {
            triggerFlashWarning();
        }, 8000);

        function triggerFlashWarning() {
            if (flashActive) return;
            flashWarning = true;
            warningEl.innerText = "⚠️ FLASHBANG INCOMING! (캔버스 밖으로 마우스를 피하세요!)";

            setTimeout(() => {
                detonateFlash();
            }, 1200);
        }

        function detonateFlash() {
            warningEl.innerText = "";
            flashWarning = false;

            // 마우스가 게임 화면(Canvas) 안에 있으면 섬광에 걸림
            if (isMouseOverCanvas) {
                flashOverlay.style.opacity = '1';
                setTimeout(() => {
                    flashOverlay.style.opacity = '0';
                }, 1500);
            }
        }

        // 메인 게임 루프
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            targets.forEach(t => t.update());
            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>
"""

# Streamlit에 HTML 게임 임베드
components.html(game_code, height=580)
