import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Web AimLab - Glock Edition", layout="centered")

st.title("🎯 Web AimLab (Glock Edition)")
st.caption("게임 시작 버튼을 누르면 입체 글록 권총과 함께 에임 연습이 시작됩니다!")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: #121212;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            margin: 0;
            user-select: none;
        }
        .controls {
            margin-bottom: 10px;
        }
        .btn {
            background-color: #333;
            color: white;
            border: 1px solid #555;
            padding: 6px 16px;
            font-size: 14px;
            cursor: pointer;
            border-radius: 4px;
            margin: 0 4px;
            transition: 0.2s;
        }
        .btn.active {
            background-color: #007acc;
            border-color: #0099ff;
            font-weight: bold;
        }
        #gameCanvas {
            background: radial-gradient(circle, #2a2d32 0%, #111215 100%);
            border: 2px solid #3a3d45;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            cursor: crosshair;
            display: block;
            margin: 0 auto;
            border-radius: 8px;
        }
        .info-panel {
            font-size: 18px;
            margin-bottom: 8px;
            font-weight: 500;
        }
        #flashOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: white;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.1s;
            border-radius: 8px;
        }
        #warningText {
            color: #ff3333;
            font-weight: bold;
            font-size: 20px;
            height: 28px;
            text-shadow: 0 0 8px rgba(255,0,0,0.6);
        }
        #startOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 15, 18, 0.85);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 8px;
            z-index: 10;
        }
        .start-btn {
            background: linear-gradient(135deg, #007acc, #00d2ff);
            color: white;
            border: none;
            padding: 14px 40px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .start-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0, 210, 255, 0.6);
        }
    </style>
</head>
<body>
    <div class="controls">
        <span>난이도 선택: </span>
        <button class="btn" onclick="setDifficulty('easy', this)">EASY</button>
        <button class="btn active" onclick="setDifficulty('medium', this)">MEDIUM</button>
        <button class="btn" onclick="setDifficulty('hard', this)">HARD</button>
    </div>

    <div class="info-panel">
        점수: <span id="score" style="color:#00d2ff">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%
    </div>
    
    <div id="warningText"></div>

    <div style="position: relative; display: inline-block;">
        <canvas id="gameCanvas" width="720" height="460"></canvas>
        <div id="flashOverlay"></div>
        <div id="startOverlay">
            <h1 style="margin-bottom: 20px; color: #00d2ff; text-shadow: 0 0 10px rgba(0,210,255,0.5);">AIMLAB GLOCK EDITION</h1>
            <button class="start-btn" onclick="startGame()">게임 시작하기</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const accuracyEl = document.getElementById('accuracy');
        const warningEl = document.getElementById('warningText');
        const flashOverlay = document.getElementById('flashOverlay');
        const startOverlay = document.getElementById('startOverlay');

        let isGameStarted = false;
        let score = 0;
        let totalShots = 0;
        let hits = 0;

        let targetRadius = 18;
        let targetSpeed = 3.2;
        let targets = [];
        const targetCount = 4;

        let flashActive = false;
        let flashInterval = null;
        let isMouseOverCanvas = false;
        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;
        let recoilY = 0;

        function setDifficulty(level, btnElement) {
            document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
            btnElement.classList.add('active');

            if (level === 'easy') {
                targetRadius = 24;
                targetSpeed = 1.5;
            } else if (level === 'medium') {
                targetRadius = 18;
                targetSpeed = 3.2;
            } else if (level === 'hard') {
                targetRadius = 12;
                targetSpeed = 5.5;
            }

            targets.forEach(t => {
                t.radius = targetRadius;
                t.dx = (Math.random() - 0.5) * targetSpeed * 2;
                t.dy = (Math.random() - 0.5) * targetSpeed * 2;
            });
        }

        function startGame() {
            startOverlay.style.display = 'none';
            isGameStarted = true;
            score = 0;
            totalShots = 0;
            hits = 0;
            updateStats();

            targets = [];
            for (let i = 0; i < targetCount; i++) {
                targets.push(new Target());
            }

            if (flashInterval) clearInterval(flashInterval);
            flashInterval = setInterval(() => {
                triggerFlashWarning();
            }, 9000);
        }

        class Target {
            constructor() {
                this.radius = targetRadius;
                this.x = Math.random() * (canvas.width - 100) + 50;
                this.y = Math.random() * (canvas.height - 200) + 50;
                this.dx = (Math.random() - 0.5) * targetSpeed * 2;
                this.dy = (Math.random() - 0.5) * targetSpeed * 2;
            }

            draw() {
                let grad = ctx.createRadialGradient(
                    this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.1,
                    this.x, this.y, this.radius
                );
                grad.addColorStop(0, '#80e5ff');
                grad.addColorStop(0.5, '#00a8ff');
                grad.addColorStop(1, '#004488');

                ctx.save();
                ctx.shadowColor = '#00a8ff';
                ctx.shadowBlur = 12;

                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();
                ctx.restore();
            }

            update() {
                this.x += this.dx;
                this.y += this.dy;

                if (this.x - this.radius < 10 || this.x + this.radius > canvas.width - 10) this.dx *= -1;
                if (this.y - this.radius < 10 || this.y + this.radius > canvas.height - 120) this.dy *= -1;

                this.draw();
            }
        }

        function drawGlock() {
            ctx.save();
            
            let gunBaseX = canvas.width / 2 + (mouseX - canvas.width / 2) * 0.12;
            let gunBaseY = canvas.height + recoilY;

            ctx.translate(gunBaseX, gunBaseY);

            // 1. 하부 프레임 및 그립 (Grip)
            let frameGrad = ctx.createLinearGradient(-25, 0, 25, 0);
            frameGrad.addColorStop(0, '#151516');
            frameGrad.addColorStop(0.5, '#28282b');
            frameGrad.addColorStop(1, '#111112');

            ctx.fillStyle = frameGrad;
            ctx.beginPath();
            ctx.moveTo(-18, -25);
            ctx.lineTo(-12, 70);
            ctx.lineTo(22, 70);
            ctx.lineTo(16, -25);
            ctx.closePath();
            ctx.fill();

            // 2. 상부 메탈 슬라이드 (Slide)
            let slideGrad = ctx.createLinearGradient(-35, -80, 35, -80);
            slideGrad.addColorStop(0, '#222326');
            slideGrad.addColorStop(0.3, '#4f5259');
            slideGrad.addColorStop(0.7, '#383a3f');
            slideGrad.addColorStop(1, '#191a1c');

            ctx.fillStyle = slideGrad;
            ctx.fillRect(-32, -80, 64, 58);

            // 3. 총열 구멍 (Muzzle Barrel)
            ctx.fillStyle = '#050505';
            ctx.beginPath();
            ctx.arc(0, -60, 9, 0, Math.PI * 2);
            ctx.fill();

            // 4. 조준기 (가늠자 & 야광 가늠쇠)
            ctx.fillStyle = '#0a0a0b';
            ctx.fillRect(-7, -84, 14, 5);
            
            ctx.fillStyle = '#39ff14'; // 야광 그린 도트
            ctx.fillRect(-2, -84, 4, 3);

            if (recoilY < 0) {
                recoilY += 2;
            }

            ctx.restore();
        }

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        canvas.addEventListener('mousedown', (e) => {
            if (!isGameStarted) return;

            totalShots++;
            recoilY = -14;

            const rect = canvas.getBoundingClientRect();
            const mX = e.clientX - rect.left;
            const mY = e.clientY - rect.top;

            for (let i = 0; i < targets.length; i++) {
                const t = targets[i];
                const dist = Math.hypot(mX - t.x, mY - t.y);

                if (dist < t.radius) {
                    score += 100;
                    hits++;
                    targets[i] = new Target();
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

        function triggerFlashWarning() {
            if (!isGameStarted || flashActive) return;
            warningEl.innerText = "⚠️ FLASHBANG INCOMING! (마우스를 창 밖으로 피하세요!)";

            setTimeout(() => {
                detonateFlash();
            }, 1300);
        }

        function detonateFlash() {
            warningEl.innerText = "";

            if (isMouseOverCanvas && isGameStarted) {
                flashOverlay.style.opacity = '1';
                setTimeout(() => {
                    flashOverlay.style.opacity = '0';
                }, 1600);
            }
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (isGameStarted) {
                targets.forEach(t => t.update());
                drawGlock();
            }

            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>
"""

components.html(game_code, height=620)
