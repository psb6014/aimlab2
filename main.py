import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Multi-Weapon Edition", layout="centered")

st.title("🎯 3D Web AimLab (Multi-Weapon Edition)")
st.caption("고정 표적 정밀 타격 연습! 원하는 총기를 선택해 에임을 연마하세요.")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #1a1d24;
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
            text-shadow: 0 0 10px rgba(0,0,0,0.8);
            pointer-events: none;
            text-align: right;
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
            color: #ff3344;
            font-size: 24px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 8px rgba(0,0,0,0.8);
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
            background: rgba(26, 29, 36, 0.94);
            backdrop-filter: blur(6px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 30;
            color: white;
        }
        .section-title {
            color: #d4a359;
            font-size: 14px;
            font-weight: bold;
            margin-top: 12px;
            margin-bottom: 6px;
            letter-spacing: 1px;
        }
        .btn-container {
            display: flex;
            gap: 12px;
        }
        .option-btn {
            background: #2b2f3a;
            color: #ece8e1;
            border: 2px solid #454c5e;
            padding: 8px 18px;
            font-size: 15px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: 0.2s;
        }
        .option-btn.selected {
            background: #b87333;
            color: #fff;
            border-color: #d4a359;
            box-shadow: 0 0 12px rgba(212,163,89,0.5);
        }
        .start-btn {
            background: linear-gradient(135deg, #b87333, #8b4513);
            color: white;
            border: none;
            padding: 12px 40px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(139, 69, 19, 0.5);
            margin-top: 20px;
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
        AMMO: <span id="ammo">30</span> / <span id="maxAmmo">30</span>
        <div id="reloadMsg" style="font-size:16px; color:#ff4655; display:none;">[R] 키를 눌러 재장전!</div>
    </div>
    <div id="crosshair"></div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #d4a359; text-shadow: 0 0 12px rgba(212,163,89,0.6); margin-bottom: 2px; font-size: 32px;">3D AIMLAB STUDIO</h1>
        <p style="color: #a0a7b5; margin-bottom: 15px; font-size: 14px;">표적을 조준하여 타격하세요. (맞출 때마다 과녁 위치가 이동합니다)</p>

        <div class="section-title">GUN SELECT</div>
        <div class="btn-container">
            <button class="option-btn selected" onclick="selectWeapon('ak47', this)">AK-47</button>
            <button class="option-btn" onclick="selectWeapon('kar98k', this)">Kar98k (Scope)</button>
            <button class="option-btn" onclick="selectWeapon('famas', this)">FAMAS</button>
        </div>

        <div class="section-title">TARGET SIZE</div>
        <div class="btn-container">
            <button class="option-btn" onclick="selectDiff('easy', this)">LARGE</button>
            <button class="option-btn selected" onclick="selectDiff('normal', this)">NORMAL</button>
            <button class="option-btn" onclick="selectDiff('hard', this)">SMALL</button>
        </div>

        <button class="start-btn" onclick="initGame()">게 임 시 작</button>
    </div>

    <script>
        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        
        let selectedWeapon = 'ak47';
        let maxAmmo = 30;
        let ammo = 30;

        let isReloading = false;
        let isGameStarted = false;
        let flashInterval = null;

        let targetRadius = 0.48;
        let mouse = new THREE.Vector2();

        let weaponGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        function selectWeapon(weapon, btn) {
            selectedWeapon = weapon;
            btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (weapon === 'ak47') maxAmmo = 30;
            else if (weapon === 'kar98k') maxAmmo = 5;
            else if (weapon === 'famas') maxAmmo = 25;
            
            ammo = maxAmmo;
            document.getElementById('maxAmmo').innerText = maxAmmo;
        }

        function selectDiff(diff, btn) {
            btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (diff === 'easy') targetRadius = 0.65;
            else if (diff === 'normal') targetRadius = 0.48;
            else if (diff === 'hard') targetRadius = 0.32;
        }

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            
            score = 0;
            totalShots = 0;
            hits = 0;
            ammo = maxAmmo;
            isReloading = false;
            updateUI();
            document.getElementById('reloadMsg').style.display = 'none';

            if (!scene) {
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x282c35);
                scene.fog = new THREE.FogExp2(0x282c35, 0.012);

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
                camera.position.set(0, 1.6, 0);

                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, 500);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
                scene.add(ambientLight);

                const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
                dirLight.position.set(6, 15, 8);
                scene.add(dirLight);

                const backLight = new THREE.DirectionalLight(0xd4a359, 0.5);
                backLight.position.set(-5, 5, -10);
                scene.add(backLight);

                // 3D 공간 배치
                const floorGeo = new THREE.PlaneGeometry(60, 60);
                const floorMat = new THREE.MeshStandardMaterial({ color: 0x323742, roughness: 0.8 });
                const floor = new THREE.Mesh(floorGeo, floorMat);
                floor.rotation.x = -Math.PI / 2;
                scene.add(floor);

                const gridHelper = new THREE.GridHelper(60, 30, 0xd4a359, 0x4a5160);
                gridHelper.position.y = 0.01;
                scene.add(gridHelper);

                const wallGeo = new THREE.PlaneGeometry(60, 30);
                const wallMat = new THREE.MeshStandardMaterial({ color: 0x21252d, roughness: 0.6 });
                const backWall = new THREE.Mesh(wallGeo, wallMat);
                backWall.position.set(0, 15, -25);
                scene.add(backWall);

                const wallGrid = new THREE.GridHelper(60, 20, 0x5a6375, 0x3a404d);
                wallGrid.rotation.x = Math.PI / 2;
                wallGrid.position.set(0, 15, -24.9);
                scene.add(wallGrid);

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

            // 선택된 총기 재생성
            if (weaponGroup) camera.remove(weaponGroup);
            buildWeaponModel(selectedWeapon);

            // 초기 타겟 생성
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

        // 총기 3D 모델링 생성자 (AK-47, Kar98k, FAMAS)
        function buildWeaponModel(type) {
            weaponGroup = new THREE.Group();

            const steelMat = new THREE.MeshStandardMaterial({ color: 0x3d414a, roughness: 0.3, metalness: 0.85 });
            const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x1f2228, roughness: 0.35, metalness: 0.9 });
            const woodMat = new THREE.MeshStandardMaterial({ color: 0x7a3a1d, roughness: 0.5, metalness: 0.1 });
            const magMat = new THREE.MeshStandardMaterial({ color: 0x2e323b, roughness: 0.35, metalness: 0.8 });

            if (type === 'ak47') {
                const mainBody = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.085, 0.42), steelMat);
                weaponGroup.add(mainBody);

                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.11, 0.36), woodMat);
                stock.position.set(0, -0.03, 0.38);
                stock.rotation.x = -0.15;
                weaponGroup.add(stock);

                const grip = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.14, 0.06), woodMat);
                grip.position.set(0, -0.11, 0.1);
                grip.rotation.x = 0.35;
                weaponGroup.add(grip);

                const lowerHandguard = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.065, 0.28), woodMat);
                lowerHandguard.position.set(0, -0.01, -0.34);
                weaponGroup.add(lowerHandguard);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.75, 12), darkSteelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.58);
                weaponGroup.add(barrel);

                magazineMesh = new THREE.Group();
                const magTop = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.16, 0.08), magMat);
                magTop.position.set(0, -0.12, -0.02);
                magTop.rotation.x = -0.28;
                magazineMesh.add(magTop);
                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                // Kar98k 일체형 우드 스톡
                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.085, 0.95), woodMat);
                stock.position.set(0, -0.03, -0.1);
                weaponGroup.add(stock);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.1, 12), darkSteelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.02, -0.45);
                weaponGroup.add(barrel);

                // 스코프 (Scope)
                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.32, 16), darkSteelMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.08, -0.1);
                weaponGroup.add(scopeBody);

                const scopeMount = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.04, 0.15), steelMat);
                scopeMount.position.set(0, 0.05, -0.1);
                weaponGroup.add(scopeMount);

                // 볼트 손잡이
                const boltHandle = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 8), darkSteelMat);
                boltHandle.position.set(0.05, 0.03, 0.1);
                weaponGroup.add(boltHandle);

                magazineMesh = new THREE.Group(); // 약실 패널
                weaponGroup.add(magazineMesh);

            } else if (type === 'famas') {
                // FAMAS 메인 메탈 바디
                const body = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.12, 0.62), darkSteelMat);
                weaponGroup.add(body);

                // 상부 대형 캐링 핸들 (운반 손잡이)
                const handleTop = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.025, 0.5), darkSteelMat);
                handleTop.position.set(0, 0.12, -0.05);
                weaponGroup.add(handleTop);

                const handleSuppL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.08, 0.04), darkSteelMat);
                handleSuppL.position.set(0, 0.07, -0.28);
                weaponGroup.add(handleSuppL);

                const handleSuppR = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.08, 0.04), darkSteelMat);
                handleSuppR.position.set(0, 0.07, 0.18);
                weaponGroup.add(handleSuppR);

                const grip = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.14, 0.06), magMat);
                grip.position.set(0, -0.11, -0.05);
                grip.rotation.x = 0.3;
                weaponGroup.add(grip);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.4, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.48);
                weaponGroup.add(barrel);

                // 불펍 탄창 (후방 배치)
                magazineMesh = new THREE.Group();
                const mag = new THREE.Mesh(new THREE.BoxGeometry(0.042, 0.18, 0.075), magMat);
                mag.position.set(0, -0.12, 0.2);
                magazineMesh.add(mag);
                weaponGroup.add(magazineMesh);
            }

            const flashGeo = new THREE.OctahedronGeometry(0.12, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            
            if (type === 'kar98k') muzzleFlashMesh.position.set(0, 0.02, -1.0);
            else if (type === 'famas') muzzleFlashMesh.position.set(0, 0.01, -0.68);
            else muzzleFlashMesh.position.set(0, 0.01, -0.98);

            weaponGroup.add(muzzleFlashMesh);

            weaponGroup.position.set(0.24, -0.24, -0.55);
            camera.add(weaponGroup);
            scene.add(camera);
        }

        // 고정 과녁 생성 (움직이지 않음)
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

            // 고정 무작위 위치 설정
            targetGroup.position.x = (Math.random() - 0.5) * 11;
            targetGroup.position.y = Math.random() * 2.8 + 0.9;
            targetGroup.position.z = -Math.random() * 8 - 4;

            scene.add(targetGroup);
            targets.push(targetGroup);
        }

        function shoot() {
            if (isReloading || !isGameStarted) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'block';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            // 총기별 반동 제어
            if (selectedWeapon === 'kar98k') {
                recoilZ = 0.32;
                recoilRotX = 0.28;
            } else {
                recoilZ = 0.18;
                recoilRotX = 0.16;
            }

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
                    // 맞춘 과녁 제거 후 위치가 다른 새 과녁 재배치
                    scene.remove(hitParent);
                    targets = targets.filter(t => t !== hitParent);
                    
                    score += (selectedWeapon === 'kar98k') ? 150 : 100;
                    hits++;
                    updateUI();
                    createTarget(); // 순간이동 효과 (새 위치에 재생성)
                    break;
                }
            }

            if (ammo === 0) {
                document.getElementById('reloadMsg').style.display = 'block';
            }
        }

        function reload() {
            if (isReloading || ammo === maxAmmo || !isGameStarted) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            let progress = 0;
            const reloadInterval = setInterval(() => {
                progress += 0.025;

                if (progress <= 0.3) {
                    const p = progress / 0.3;
                    magazineMesh.position.y = -0.35 * p;
                    weaponGroup.rotation.z = 0.2 * p;
                } else if (progress > 0.3 && progress <= 0.75) {
                    const p = (progress - 0.3) / 0.45;
                    magazineMesh.position.y = -0.35 - Math.sin(p * Math.PI) * 0.08;
                    magazineMesh.rotation.x = -p * Math.PI * 2;
                } else if (progress > 0.75 && progress <= 1.0) {
                    const p = (progress - 0.75) / 0.25;
                    magazineMesh.position.y = -0.35 * (1 - p);
                    magazineMesh.rotation.x = 0;
                    weaponGroup.rotation.z = 0.2 * (1 - p);
                } else {
                    clearInterval(reloadInterval);
                    magazineMesh.position.set(0, 0, 0);
                    magazineMesh.rotation.set(0, 0, 0);
                    weaponGroup.rotation.z = 0;
                    
                    ammo = maxAmmo;
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
            document.getElementById('maxAmmo').innerText = maxAmmo;
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

                weaponGroup.position.x = 0.24 + mouse.x * 0.04;
                weaponGroup.position.y = -0.24 + mouse.y * 0.04;

                if (recoilZ > 0) {
                    recoilZ -= 0.02;
                    if (recoilZ < 0) recoilZ = 0;
                }
                if (recoilRotX > 0) {
                    recoilRotX -= 0.015;
                    if (recoilRotX < 0) recoilRotX = 0;
                }

                weaponGroup.position.z = -0.55 + recoilZ;
                weaponGroup.rotation.x = recoilRotX;

                // 과녁의 자동 이동 루프 제거됨 (고정 상태 유지)
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
