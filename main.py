import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - AK-47 Edition", layout="centered")

st.title("🎯 3D Web AimLab (Real AK-47 Edition)")
st.caption("클래식 AK-47과 함께하는 고속 에임 연습! (30발 탄창 / R키: 재장전)")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #0b0e14;
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
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .main-menu-btn {
            pointer-events: auto;
            background: #2b2e33;
            color: #d4a359;
            border: 1px solid #d4a359;
            padding: 5px 12px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: 0.2s;
        }
        .main-menu-btn:hover {
            background: #d4a359;
            color: #000;
        }
        #ammo-panel {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: #d4a359;
            font-size: 28px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 10px rgba(212,163,89,0.5);
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
            background: #00ff88;
            box-shadow: 0 0 4px #00ff88;
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
            background: rgba(11, 14, 20, 0.95);
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
            background: #1f232d;
            color: #ece8e1;
            border: 2px solid #363c4a;
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: 0.2s;
        }
        .diff-btn.selected {
            background: #b87333;
            color: #fff;
            border-color: #d4a359;
            box-shadow: 0 0 15px rgba(212,163,89,0.5);
        }
        .start-btn {
            background: linear-gradient(135deg, #b87333, #8b4513);
            color: white;
            border: none;
            padding: 14px 45px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(139, 69, 19, 0.5);
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
        <button class="main-menu-btn" onclick="goToMainMenu()">🏠 메인으로</button>
        <div>점수: <span id="score" style="color:#d4a359">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%</div>
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">30</span> / 30 <span id="reloadMsg" style="font-size:16px; color:#ff4655; display:none;"><br>[R] 키를 눌러 재장전!</span>
    </div>
    <div id="crosshair"></div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #d4a359; text-shadow: 0 0 12px rgba(212,163,89,0.6); margin-bottom: 5px; font-size: 36px;">REAL AK-47 AIMLAB</h1>
        <p style="color: #8b929a; margin-bottom: 10px;">AK-47 소총으로 고속 이동 표적지를 정밀 타격하세요.</p>
        
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
        
        const MAX_AMMO = 30;
        let ammo = MAX_AMMO;
        let isReloading = false;
        let isGameStarted = false;
        let flashInterval = null;

        let currentDiff = 'normal';
        // Normal 모드 속도 살짝 다운 (기존 0.085 -> 0.065)
        let targetSpeed = 0.065;
        let targetRadius = 0.48;

        let mouse = new THREE.Vector2();

        let akGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        function selectDiff(diff, btn) {
            currentDiff = diff;
            document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (diff === 'easy') {
                targetSpeed = 0.04;
                targetRadius = 0.6;
            } else if (diff === 'normal') {
                targetSpeed = 0.065;
                targetRadius = 0.48;
            } else if (diff === 'hard') {
                targetSpeed = 0.13;
                targetRadius = 0.35;
            }
        }

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            
            score = 0;
            totalShots = 0;
            hits = 0;
            ammo = MAX_AMMO;
            isReloading = false;
            updateUI();
            document.getElementById('reloadMsg').style.display = 'none';

            if (!scene) {
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0a0c10);
                scene.fog = new THREE.FogExp2(0x0a0c10, 0.015);

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
                camera.position.set(0, 1.6, 0);

                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, 500);
                document.body.appendChild(renderer.domElement);

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
                scene.add(ambientLight);
                const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
                dirLight.position.set(5, 12, 7);
                scene.add(dirLight);

                const gridHelper = new THREE.GridHelper(60, 30, 0x555555, 0x1f232d);
                gridHelper.position.y = 0;
                scene.add(gridHelper);

                createAK47();

                window.addEventListener('mousemove', (e) => {
                    const rect = renderer.domElement.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
                });

                window.addEventListener('mousedown', (e) => {
                    if (e.button === 0 && isGameStarted) shoot();
                });

                window.addEventListener('keydown', (e) => {
                    if ((e.key === 'r' || e.key === 'R') && isGameStarted) reload();
                });

                animate();
            }

            targets.forEach(t => scene.remove(t));
            targets = [];
            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            if (flashInterval) clearInterval(flashInterval);
            flashInterval = setInterval(triggerFlash, 10000);

            isGameStarted = true;
        }

        function goToMainMenu() {
            isGameStarted = false;
            if (flashInterval) clearInterval(flashInterval);
            document.getElementById('warningText').innerText = "";
            document.getElementById('startOverlay').style.display = 'flex';
        }

        function createAK47() {
            akGroup = new THREE.Group();

            const steelMat = new THREE.MeshStandardMaterial({ color: 0x2b2e33, roughness: 0.35, metalness: 0.85 });
            const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x1c1e22, roughness: 0.4, metalness: 0.9 });
            const woodMat = new THREE.MeshStandardMaterial({ color: 0x5c2c16, roughness: 0.6, metalness: 0.1 });
            const magMat = new THREE.MeshStandardMaterial({ color: 0x22252a, roughness: 0.4, metalness: 0.8 });

            const bodyGeo = new THREE.BoxGeometry(0.065, 0.085, 0.42);
            const mainBody = new THREE.Mesh(bodyGeo, steelMat);
            akGroup.add(mainBody);

            const stockGeo = new THREE.BoxGeometry(0.05, 0.11, 0.36);
            const stock = new THREE.Mesh(stockGeo, woodMat);
            stock.position.set(0, -0.03, 0.38);
            stock.rotation.x = -0.15;
            akGroup.add(stock);

            const gripGeo = new THREE.BoxGeometry(0.045, 0.14, 0.06);
            const grip = new THREE.Mesh(gripGeo, woodMat);
            grip.position.set(0, -0.11, 0.1);
            grip.rotation.x = 0.35;
            akGroup.add(grip);

            const lowerHandguard = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.065, 0.28), woodMat);
            lowerHandguard.position.set(0, -0.01, -0.34);
            akGroup.add(lowerHandguard);

            const upperHandguard = new THREE.Mesh(new THREE.CylinderGeometry(0.028, 0.028, 0.26, 12), woodMat);
            upperHandguard.rotation.x = Math.PI / 2;
            upperHandguard.position.set(0, 0.032, -0.33);
            akGroup.add(upperHandguard);

            const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.75, 12), darkSteelMat);
            barrel.rotation.x = Math.PI / 2;
            barrel.position.set(0, 0.01, -0.58);
            akGroup.add(barrel);

            const gasBlock = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.06, 0.05), steelMat);
            gasBlock.position.set(0, 0.03, -0.65);
            akGroup.add(gasBlock);

            const frontSight = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.065, 0.03), darkSteelMat);
            frontSight.position.set(0, 0.06, -0.88);
            akGroup.add(frontSight);

            const rearSight = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.035, 0.08), darkSteelMat);
            rearSight.position.set(0, 0.06, -0.18);
            akGroup.add(rearSight);

            magazineMesh = new THREE.Group();
            const magTop = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.16, 0.08), magMat);
            magTop.position.set(0, -0.12, -0.02);
            magTop.rotation.x = -0.28;

            const magBottom = new THREE.Mesh(new THREE.BoxGeometry(0.043, 0.18, 0.075), magMat);
            magBottom.position.set(0, -0.25, -0.07);
            magBottom.rotation.x = -0.55;

            magazineMesh.add(magTop);
            magazineMesh.add(magBottom);
            akGroup.add(magazineMesh);

            const flashGeo = new THREE.OctahedronGeometry(0.11, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.position.set(0, 0.01, -0.98);
            akGroup.add(muzzleFlashMesh);

            akGroup.position.set(0.24, -0.24, -0.55);
            camera.add(akGroup);
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
                new THREE.MeshStandardMaterial({ color: 0x333333 }),
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
            if (isReloading || !isGameStarted) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            recoilZ = 0.18;
            recoilRotX = 0.16;

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

        // 탄창 공중 360도 회전(Flip) 재장전 모션
        function reload() {
            if (isReloading || ammo === MAX_AMMO || !isGameStarted) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            let progress = 0;
            const reloadInterval = setInterval(() => {
                progress += 0.025; // 애니메이션 진행도

                if (progress <= 0.3) {
                    // 1단계: 탄창 탈착 및 아래로 떨구기
                    const p = progress / 0.3;
                    magazineMesh.position.y = -0.35 * p;
                    magazineMesh.position.z = 0.05 * p;
                    akGroup.rotation.z = 0.2 * p; // 총을 약간 기움
                } else if (progress > 0.3 && progress <= 0.75) {
                    // 2단계: 공중에서 탄창 360도 돌리기 (360 Flip)
                    const p = (progress - 0.3) / 0.45;
                    magazineMesh.position.y = -0.35 - Math.sin(p * Math.PI) * 0.08;
                    magazineMesh.rotation.x = -p * Math.PI * 2; // X축 360도 회전
                } else if (progress > 0.75 && progress <= 1.0) {
                    // 3단계: 새 탄창 빠르게 장착
                    const p = (progress - 0.75) / 0.25;
                    magazineMesh.position.y = -0.35 * (1 - p);
                    magazineMesh.position.z = 0.05 * (1 - p);
                    magazineMesh.rotation.x = 0;
                    akGroup.rotation.z = 0.2 * (1 - p);
                } else {
                    // 완료
                    clearInterval(reloadInterval);
                    magazineMesh.position.set(0, 0, 0);
                    magazineMesh.rotation.set(0, 0, 0);
                    akGroup.rotation.z = 0;
                    
                    ammo = MAX_AMMO;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    document.getElementById('reloadMsg').innerText = "[R] 키를 눌러 재장전!";
                    updateUI();
                }
            }, 20);
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
                if (Math.hypot(mouse.x, mouse.y) < 0.65 && isGameStarted) {
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

                akGroup.position.x = 0.24 + mouse.x * 0.04;
                akGroup.position.y = -0.24 + mouse.y * 0.04;

                if (recoilZ > 0) {
                    recoilZ -= 0.02;
                    if (recoilZ < 0) recoilZ = 0;
                }
                if (recoilRotX > 0) {
                    recoilRotX -= 0.015;
                    if (recoilRotX < 0) recoilRotX = 0;
                }

                akGroup.position.z = -0.55 + recoilZ;
                akGroup.rotation.x = recoilRotX;

                targets.forEach(t => {
                    t.position.x += t.userData.dx;
                    t.position.y += t.userData.dy;

                    t.rotation.z += 0.02;

                    if (Math.abs(t.position.x) > 7.5) t.userData.dx *= -1;
                    if (t.position.y < 0.8 || t.position.y > 4.2) t.userData.dy *= -1;
                });
            }

            if (renderer && scene && camera) {
                renderer.render(scene, camera);
            }
        }
    </script>
</body>
</html>
"""

components.html(game_code, height=540)
