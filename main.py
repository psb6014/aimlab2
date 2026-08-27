import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Web AimLab - Glock Edition", layout="centered")

st.title("🎯 Web AimLab (Glock & 3D Style)")
st.caption("글록 권총으로 타겟을 맞추세요! 상단에서 난이도를 조절할 수 있으며, 섬광탄이 오면 마우스를 게임 창 밖으로 피해야 합니다.")

# HTML5 / Canvas / JavaScript 기반 입체 에임랩
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

        // 난이도 기본값
        let targetRadius = 18;
        let targetSpeed = 3.0;

        let targets = [];
        const targetCount = 4;

        // 섬광탄 & 마우스 위치
        let flashActive = false;
        let isMouseOverCanvas = false;
        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;
        
        // 총 반동 애니메이션 변수
        let recoilY = 0;

        // 난이도 변경 함수
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

            // 기존 타겟 크기/속도 갱신
            targets.forEach(t => {
                t.radius = targetRadius;
                t.dx = (Math.random() - 0.5) * targetSpeed * 2;
                t.dy = (Math.random() - 0.5) * targetSpeed * 2;
            });
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
                // 입체 구체 3D 그라데이션
                let grad = ctx.createRadialGradient(
                    this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.1,
                    this.x, this.y, this.radius
                );
                grad.addColorStop(0, '#80e5ff');
                grad.addColorStop(0.5, '#00a8ff');
                grad.addColorStop(1, '#004488');

                // 그림자 효과
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

        // 초기 타겟 생성
        for (let i = 0; i < targetCount; i++) {
            targets.push(new Target());
        }

        // 입체 글록(Glock) 권총 그리기
        function drawGlock() {
            ctx.save();
            
            // 마우스 위치 따라 살짝 회전
            let gunBaseX = canvas.width / 2 + (mouseX - canvas.width / 2) * 0.15;
            let gunBaseY = canvas.height + recoilY;

            ctx.translate(gunBaseX, gunBaseY);

            // 1. 권총 손잡이 (Grip)
            ctx.fillStyle = '#1c1c1e';
            ctx.beginPath();
            ctx.moveTo(-20, -20);
            ctx.lineTo(-10, 60);
            ctx.lineTo(25, 60);
            ctx.lineTo(15, -20);
            ctx.closePath();
            ctx.fill();

            // 2. 권총 슬라이드 (Slide - 상부 3D 입체 표현)
            let slideGrad = ctx.createLinearGradient(-35, -70, 35, -70);
            slideGrad.addColorStop(0, '#2c2c2e');
            slideGrad.addColorStop(0.5, '#48484a');
            slideGrad.addColorStop(1, '#1c1c1e');

            ctx.fillStyle = slideGrad;
            ctx.fillRect(-30, -75, 60, 55);

            // 슬라이드 가늠자/가늠쇠 및 상단 바
            ctx.fillStyle = '#0a0a0a';
            ctx.fillRect(-6, -78, 12, 6); // 가늠자
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(-2, -78, 4, 3);  # 야광 도트

            // 반동 복귀 애니메이션
            if (recoilY < 0) {
                recoilY += 2;
            }

            ctx.restore();
        }

        // 마우스 이동 감지
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        });

        // 사격 클릭 이벤트
        canvas.addEventListener('mousedown', (e) => {
            totalShots++;
            recoilY = -15; // 반동 발생

            const rect = canvas.getBoundingClientRect();
            const mX = e.clientX - rect.left;
            const mY = e.clientY - rect.top;

            for (let i = 0; i < targets.length; i++) {
                const t = targets[i];
                const dist = Math.hypot(mX - t.x, mY - t.y);

                if (dist < t.radius) {
                    score += 100;
                    hits++;
                    targets[i] = new Target(); // 재생성
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

        // 9초마다 섬광탄 경고
        setInterval(() => {
            triggerFlashWarning();
        }, 9000);

        function triggerFlashWarning() {
            if (flashActive) return;
            warningEl.innerText = "⚠️ FLASHBANG INCOMING! (마우스를 창 밖으로 피하세요!)";

            setTimeout(() => {
                detonateFlash();
            }, 1300);
        }

        function detonateFlash() {
            warningEl.innerText = "";

            if (isMouseOverCanvas) {
                flashOverlay.style.opacity = '1';
                setTimeout(() => {
                    flashOverlay.style.opacity = '0';
                }, 1600);
            }
        }

        // 루프 렌더링
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 타겟 렌더링
            targets.forEach(t => t.update());
            
            // 글록 권총 렌더링
            drawGlock();

            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>
"""

# Streamlit 화면에 임베드
components.html(game_code, height=620)
