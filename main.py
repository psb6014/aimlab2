import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Kuronami Vandal", layout="centered")

st.title("🎯 3D Web AimLab (Kuronami Vandal Edition)")
st.caption("발로란트 '쿠로나미 밴달'스킨과 함께하는 최고속 에임 연습! (25발 / R키: 재장전)")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #080a0f;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
        }
        #ui-panel {
            position: absolute;
            top: 15px;
            left: 20px;
            color: #fff;
            font-size: 18px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 5px rgba(0,0,0,0.8);
            pointer-events: none;
        }
        #ammo-panel {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: #ffaa00;
            font-size: 28px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 12px rgba(255,170,0,0.6);
            pointer-events: none;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 10px;
            height: 10px;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 15;
        }
        #crosshair::before, #crosshair::after {
            content: '';
            position: absolute;
            background: #00ffcc;
            box-shadow: 0 0 4px #00ffcc;
        }
        #crosshair::before {
            top: 4px; left: -6px; width: 22px; height: 2px;
        }
        #crosshair::after {
            top: -6px; left: 4px; width: 2px; height: 22px;
        }
        #warningText {
            position: absolute;
            top: 60px;
            width: 100%;
            text-align: center;
            color: #ffcc00;
            font-size: 24px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 8px rgba(255,204,0,0.8);
            pointer-events: none;
        }
        #flashOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: white;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.1s;
            z-index: 20;
        }
        #startOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(8, 10, 15, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 30;
            color: white;
        }
        .diff-container {
            margin: 20px 0;
            display: flex;
            gap: 15px;
        }
        .diff-btn {
            background: #121620;
            color: #ece8e1;
            border: 2px solid #2a3245;
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: 0.2s;
        }
        .diff-btn.selected {
            background: #ffaa00;
            color: #000;
            border-color: #ffaa00;
            box-shadow: 0 0 15px rgba(255,170,0,0.6);
        }
        .start-btn {
            background: linear-gradient(135deg, #ffaa00, #ff5500);
            color: white;
            border: none;
            padding: 14px 45px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 170, 0, 0.4);
            margin-top: 10px;
        }
        .start-btn:hover {
            transform: scale(1.05);
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="ui-panel">
        점수: <span id="score" style="color:#ffaa00">0</span> | 명중률: <span id="accuracy" style="color:#00ffcc">100</span>%
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">25</span> / 25 <span id="reloadMsg" style="font-size:16px; color:#ff4655; display:none;"><br>[R] 키를 눌러 재장전!</span>
    </div>
    <div id="crosshair"></div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #ffaa00; text-shadow: 0 0 12px rgba(255,170,0,0.6); margin-bottom: 5px; font-size: 36px;">KURONAMI VANDAL AIMLAB</h1>
        <p style="color: #8b929a; margin-bottom: 10px;">쿠로나미 밴달 스킨과 함께 조준 연습을 시작하세요.</p>
        
        <div class="diff-container">
            <button class="diff-btn" onclick="selectDiff('easy', this)">EASY</button>
            <button class="diff-btn selected" onclick="selectDiff('normal', this)">NORMAL</button>
            <button class="diff-btn" onclick="selectDiff('hard', this)">HARD (FAST)</button>
        </div>

        <button class="start-btn" onclick="initGame()">게 임 시 작</button>
    </div>

    <script>
        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        
        const MAX_AMMO = 25;
        let ammo = MAX_AMMO;
        let isReloading = false;
        let isGameStarted = false;

        let currentDiff = 'normal';
        let targetSpeed = 0.085;
        let targetRadius = 0.48;

        let mouse = new THREE.Vector2();

        // 쿠로나미 밴달 모델 파츠
        let kuronamiGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        function selectDiff(diff, btn) {
            currentDiff = diff;
            document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (diff === 'easy') {
                targetSpeed = 0.045;
                targetRadius = 0.6;
            } else if (diff === 'normal') {
                targetSpeed = 0.085;
                targetRadius = 0.48;
            } else if (diff === 'hard') {
                targetSpeed = 0.14;
                targetRadius = 0.35;
            }
        }

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            isGameStarted = true;

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0c12);
            scene.fog = new THREE.FogExp2(0x0a0c12, 0.015);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
            camera.position.set(0, 1.6, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, 500);
            document.body.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
            dirLight.position.set(5, 12, 7);
            scene.add(dirLight);

            // 사이버펑크 네온 하단 그리드
            const gridHelper = new THREE.GridHelper(60, 30, 0x00ffcc, 0x1f2738);
            gridHelper.position.y = 0;
            scene.add(gridHelper);

            // 쿠로나미 밴달 스킨 조립
            createKuronamiVandal();

            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            window.addEventListener('mousemove', (e) => {
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            });

            window.addEventListener('mousedown', (e) => {
                if (e.button === 0 && isGameStarted) shoot();
            });

            window.addEventListener('keydown', (e) => {
                if (e.key === 'r' || e.key === 'R') reload();
            });

            setInterval(triggerFlash, 10000);

            animate();
        }

        // 쿠로나미 밴달(Kuronami Vandal) 3D 조형
        function createKuronamiVandal() {
            kuronamiGroup = new THREE.Group();

            const darkMetal = new THREE.MeshStandardMaterial({ color: 0x111318, roughness: 0.25, metalness: 0.9 });
            const goldAccent = new THREE.MeshStandardMaterial({ color: 0xd4af37, roughness: 0.3, metalness: 0.8 });
            const neonCyan = new THREE.MeshBasicMaterial({ color: 0x00ffcc });
            const neonAmber = new THREE.MeshBasicMaterial({ color: 0xffaa00 });

            // 1. 메인 수신기 (Sharp Vandal Body)
            const bodyGeo = new THREE.ConeGeometry(0.08, 0.65, 4);
            const mainBody = new THREE.Mesh(bodyGeo, darkMetal);
            mainBody.rotation.z = -Math.PI / 2;
            kuronamiGroup.add(mainBody);

            // 2. 날카로운 상부 레이저 가이드
            const topSpineGeo = new THREE.BoxGeometry(0.03, 0.04, 0.5);
            const topSpine = new THREE.Mesh(topSpineGeo, goldAccent);
            topSpine.position.set(0, 0.06, -0.1);
            kuronamiGroup.add(topSpine);

            // 3. 쿠로나미 특유의 뾰족한 총열 (Spiked Barrel)
            const barrelGeo = new THREE.CylinderGeometry(0.018, 0.025, 0.65, 6);
            const barrel = new THREE.Mesh(barrelGeo, darkMetal);
            barrel.rotation.x = Math.PI / 2;
            barrel.position.set(0, 0.01, -0.6);
            kuronamiGroup.add(barrel);

            // 총구 소멸기 팁 (Spiked Muzzle Tip)
            const muzzleTipGeo = new THREE.ConeGeometry(0.03, 0.15, 6);
            const muzzleTip = new THREE.Mesh(muzzleTipGeo, goldAccent);
            muzzleTip.rotation.x = -Math.PI / 2;
            muzzleTip.position.set(0, 0.01, -0.92);
            kuronamiGroup.add(muzzleTip);

            // 4. 발광 라인 (Cyan Mana/Energy Line)
            const lineGeo = new THREE.BoxGeometry(0.01, 0.015, 0.55);
            const line = new THREE.Mesh(lineGeo, neonCyan);
            line.position.set(0, 0.02, -0.3);
            kuronamiGroup.add(line);

            // 5. 유선형 각진 개머리판 (Angular Stock)
            const stockGeo = new THREE.BoxGeometry(0.04, 0.14, 0.38);
            const stock = new THREE.Mesh(stockGeo, darkMetal);
            stock.position.set(0, -0.03, 0.42);
            stock.rotation.x = -0.2;
            kuronamiGroup.add(stock);

            // 개머리판 골드 프레임
            const stockFrame = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.03, 0.35), goldAccent);
            stockFrame.position.set(0, 0.02, 0.42);
            stockFrame.rotation.x = -0.2;
            kuronamiGroup.add(stockFrame);

            // 6. 조준경 (Kuronami Holographic Scope)
            const scopeGeo = new THREE.BoxGeometry(0.035, 0.06, 0.12);
            const scope = new THREE.Mesh(scopeGeo, goldAccent);
            scope.position.set(0, 0.09, -0.05);
            kuronamiGroup.add(scope);

            const scopeCore = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.03, 0.08), neonCyan);
            scopeCore.position.set(0, 0.095, -0.05);
            kuronamiGroup.add(scopeCore);

            // 7. 뾰족한 사선 엠버 탄창 (Curved Mag)
            magazineMesh = new THREE.Group();
            const magBox = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.32, 0.09), darkMetal);
            magBox.position.set(0, -0.18, -0.05);
            magBox.rotation.x = -0.4;

            const magEdge = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.3, 0.02), goldAccent);
            magEdge.position.set(0, -0.18, -0.01);
            magEdge.rotation.x = -0.4;

            magazineMesh.add(magBox);
            magazineMesh.add(magEdge);
            kuronamiGroup.add(magazineMesh);

            // 8. 총구 화염 (Amber Muzzle Flash)
            const flashGeo = new THREE.OctahedronGeometry(0.1, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.position.set(0, 0.01, -1.02);
            kuronamiGroup.add(muzzleFlashMesh);

            kuronamiGroup.position.set(0.24, -0.24, -0.55);
            camera.add(kuronamiGroup);
            scene.add(camera);
        }

        function createTarget() {
            const targetGroup = new THREE.Group();

            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 256;
            const ctx = canvas.getContext('2d');

            const rings = [
                { r: 128, color: '#ff2233' },
                { r: 100, color: '#ffffff' },
                { r: 72,  color: '#ff2233' },
                { r: 44,  color: '#ffffff' },
                { r: 20,  color: '#ff1122' }
            ];

            rings.forEach(ring => {
                ctx.beginPath();
                ctx.arc(128, 128, ring.r, 0, Math.PI * 2);
                ctx.fillStyle = ring.color;
                ctx.fill();
            });

            const texture = new THREE.CanvasTexture(canvas);
            
            const discGeo = new THREE.CylinderGeometry(targetRadius, targetRadius, 0.06, 32);
            const discMat = [
                new THREE.MeshStandardMaterial({ color: 0x222222 }),
                new THREE.MeshStandardMaterial({ map: texture, roughness: 0.3 }),
                new THREE.MeshStandardMaterial({ color: 0x111111 })
            ];

            const disc = new THREE.Mesh(discGeo, discMat);
            disc.rotation.x = Math.PI / 2;
            targetGroup.add(disc);

            targetGroup.position.x = (Math.random() - 0.5) * 11;
            targetGroup.position.y = Math.random() * 3.2 + 0.8;
            targetGroup.position.z = -Math.random() * 8 - 4;

            targetGroup.userData = {
                dx: (Math.random() - 0.5) * targetSpeed * 2.5,
                dy: (Math.random() - 0.5) * targetSpeed * 2.5
            };

            scene.add(targetGroup);
            targets.push(targetGroup);
        }

        function shoot() {
            if (isReloading) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            recoilZ = 0.17;
            recoilRotX = 0.15;

            muzzleFlashMesh.material.opacity = 1.0;
            setTimeout(() => {
                muzzleFlashMesh.material.opacity = 0;
            }, 35);

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, camera);

            const intersects = raycaster.intersectObjects(scene.children, true);

            for (let i = 0; i < intersects.length; i++) {
                let hitParent = intersects[i].object.parent;
                if (targets.includes(hitParent)) {
                    scene.remove(hitParent);
                    targets = targets.filter(t => t !== hitParent);
                    
                    score += 100;
                    hits++;
                    updateUI();
                    createTarget();
                    break;
                }
            }

            if (ammo === 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
            }
        }

        function reload() {
            if (isReloading || ammo === MAX_AMMO) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            let step = 0;
            const reloadInterval = setInterval(() => {
                step += 0.04;

                if (step < 0.4) {
                    magazineMesh.position.y -= 0.035;
                    magazineMesh.position.z += 0.01;
                    kuronamiGroup.rotation.z = 0.25;
                } else if (step >= 0.4 && step < 0.5) {
                    magazineMesh.position.set(0, -0.5, -0.05);
                } else if (step >= 0.5 && step < 0.9) {
                    magazineMesh.position.y += 0.035;
                } else {
                    clearInterval(reloadInterval);
                    magazineMesh.position.set(0, 0, 0);
                    kuronamiGroup.rotation.z = 0;
                    ammo = MAX_AMMO;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    document.getElementById('reloadMsg').innerText = "[R] 키를 눌러 재장전!";
                    updateUI();
                }
            }, 25);
        }

        function updateUI() {
            document.getElementById('score').innerText = score;
            document.getElementById('ammo').innerText = ammo;
            const acc = totalShots > 0 ? ((hits / totalShots) * 100).toFixed(1) : 100;
            document.getElementById('accuracy').innerText = acc;
        }

        function triggerFlash() {
            if (!isGameStarted) return;
            document.getElementById('warningText').innerText = "⚠️ FLASHBANG INCOMING! (구석으로 커서를 피하세요!)";

            setTimeout(() => {
                document.getElementById('warningText').innerText = "";
                if (Math.hypot(mouse.x, mouse.y) < 0.65) {
                    const flashOverlay = document.getElementById('flashOverlay');
                    flashOverlay.style.opacity = '1';
                    setTimeout(() => {
                        flashOverlay.style.opacity = '0';
                    }, 1800);
                }
            }, 1200);
        }

        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                camera.rotation.y += (-mouse.x * 0.45 - camera.rotation.y) * 0.1;
                camera.rotation.x += (mouse.y * 0.28 - camera.rotation.x) * 0.1;

                kuronamiGroup.position.x = 0.24 + mouse.x * 0.04;
                kuronamiGroup.position.y = -0.24 + mouse.y * 0.04;

                if (recoilZ > 0) {
                    recoilZ -= 0.02;
                    if (recoilZ < 0) recoilZ = 0;
                }
                if (recoilRotX > 0) {
                    recoilRotX -= 0.015;
                    if (recoilRotX < 0) recoilRotX = 0;
                }

                kuronamiGroup.position.z = -0.55 + recoilZ;
                kuronamiGroup.rotation.x = recoilRotX;

                targets.forEach(t => {
                    t.position.x += t.userData.dx;
                    t.position.y += t.userData.dy;

                    t.rotation.z += 0.02;

                    if (Math.abs(t.position.x) > 7.5) t.userData.dx *= -1;
                    if (t.position.y < 0.8 || t.position.y > 4.2) t.userData.dy *= -1;
                });
            }

            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

components.html(game_code, height=540)
