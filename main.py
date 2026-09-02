import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Pointer Lock Edition", layout="centered")

st.title("🎯 3D Web AimLab (Pointer Lock Edition)")
st.caption("마우스 조작 시 화면과 총이 함께 움직이며, [E] 키를 누르면 메인 화면으로 나갑니다.")

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
            display: none;
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
            font-size: 22px;
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
            background: rgba(26, 29, 36, 0.95);
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
            box-shadow: 0 4px 15px rgba(139, 69, 19, 0.5);
            margin-top: 20px;
            cursor: pointer;
        }
        .start-btn:hover {
            transform: scale(1.05);
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="ui-panel">
        <button class="main-menu-btn" onclick="goToMainMenu()">🏠 메인으로 (E)</button>
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
        <p style="color: #a0a7b5; margin-bottom: 15px; font-size: 14px;">화면 클릭 시 마우스가 고정되며, 게임 중 <b style="color:#00ff88">[E]</b> 키를 누르면 메뉴로 나갑니다.</p>

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
        let audioCtx = null;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function playGunSound(type) {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const bufferSize = audioCtx.sampleRate * 0.5;
            const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const output = buffer.getChannelData(0);

            for (let i = 0; i < bufferSize; i++) {
                output[i] = Math.random() * 2 - 1;
            }

            const noise = audioCtx.createBufferSource();
            noise.buffer = buffer;

            const filter = audioCtx.createBiquadFilter();
            const gain = audioCtx.createGain();

            if (type === 'ak47') {
                filter.type = 'bandpass';
                filter.frequency.setValueAtTime(800, now);
                filter.frequency.exponentialRampToValueAtTime(100, now + 0.35);
                gain.gain.setValueAtTime(1.2, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
            } else if (type === 'kar98k') {
                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(3000, now);
                filter.frequency.exponentialRampToValueAtTime(80, now + 0.5);
                gain.gain.setValueAtTime(1.6, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
            } else if (type === 'famas') {
                filter.type = 'highpass';
                filter.frequency.setValueAtTime(1200, now);
                filter.frequency.exponentialRampToValueAtTime(200, now + 0.22);
                gain.gain.setValueAtTime(1.0, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
            }

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start(now);

            const osc = audioCtx.createOscillator();
            const oscGain = audioCtx.createGain();
            osc.type = 'triangle';
            
            if (type === 'kar98k') {
                osc.frequency.setValueAtTime(150, now);
                osc.frequency.exponentialRampToValueAtTime(30, now + 0.4);
                oscGain.gain.setValueAtTime(0.8, now);
                oscGain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
            } else {
                osc.frequency.setValueAtTime(120, now);
                osc.frequency.exponentialRampToValueAtTime(40, now + 0.2);
                oscGain.gain.setValueAtTime(0.5, now);
                oscGain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
            }

            osc.connect(oscGain);
            oscGain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.4);
        }

        function playEmptyClick() {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'square';
            osc.frequency.setValueAtTime(800, now);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.05);
        }

        function playReloadSound() {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(400, now);
            osc.frequency.exponentialRampToValueAtTime(150, now + 0.15);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.15);
        }

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

        let weaponGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        // 카메라 회전 및 포인터 락 제어 변수
        let yaw = 0, pitch = 0;
        let mouseDeltaX = 0, mouseDeltaY = 0;
        const sensitivity = 0.0022;

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

        function requestLock() {
            if (renderer && renderer.domElement) {
                renderer.domElement.requestPointerLock();
            }
        }

        function initGame() {
            initAudio();
            document.getElementById('startOverlay').style.display = 'none';
            document.getElementById('crosshair').style.display = 'block';
            
            score = 0;
            totalShots = 0;
            hits = 0;
            ammo = maxAmmo;
            isReloading = false;
            yaw = 0;
            pitch = 0;
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

                // 마우스 이동 제어 (Pointer Lock)
                document.addEventListener('mousemove', (e) => {
                    if (document.pointerLockElement === renderer.domElement && isGameStarted) {
                        mouseDeltaX = e.movementX || 0;
                        mouseDeltaY = e.movementY || 0;

                        yaw -= mouseDeltaX * sensitivity;
                        pitch -= mouseDeltaY * sensitivity;

                        // 상하 회전각 제한 (-80도 ~ 80도)
                        pitch = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, pitch));
                    }
                });

                // 사격 이벤트
                window.addEventListener('mousedown', (e) => {
                    if (e.button === 0 && isGameStarted) {
                        if (document.pointerLockElement !== renderer.domElement) {
                            requestLock();
                        } else {
                            shoot();
                        }
                    }
                });

                // 키보드 입력 (E: 메인메뉴, R: 재장전)
                window.addEventListener('keydown', (e) => {
                    if (isGameStarted) {
                        if (e.key === 'e' || e.key === 'E') {
                            goToMainMenu();
                        } else if (e.key === 'r' || e.key === 'R') {
                            reload();
                        }
                    }
                });

                // Pointer Lock 해제 감지 (Esc 포함)
                document.addEventListener('pointerlockchange', () => {
                    if (document.pointerLockElement !== renderer.domElement && isGameStarted) {
                        goToMainMenu();
                    }
                });

                animate();
            }

            requestLock();

            if (weaponGroup) camera.remove(weaponGroup);
            buildWeaponModel(selectedWeapon);

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
            if (document.pointerLockElement) {
                document.exitPointerLock();
            }
            if (flashInterval) clearInterval(flashInterval);
            document.getElementById('warningText').innerText = "";
            document.getElementById('crosshair').style.display = 'none';
            document.getElementById('startOverlay').style.display = 'flex';
        }

        function buildWeaponModel(type) {
            weaponGroup = new THREE.Group();

            const steelMat = new THREE.MeshStandardMaterial({ color: 0x4a4e57, roughness: 0.25, metalness: 0.9 });
            const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x1d2026, roughness: 0.3, metalness: 0.95 });
            const woodMat = new THREE.MeshStandardMaterial({ color: 0x8b4513, roughness: 0.4, metalness: 0.05 });
            const magMat = new THREE.MeshStandardMaterial({ color: 0x2b2e36, roughness: 0.35, metalness: 0.8 });
            const goldMat = new THREE.MeshStandardMaterial({ color: 0xd4a359, roughness: 0.2, metalness: 0.9 });

            if (type === 'ak47') {
                const mainBody = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.09, 0.44), steelMat);
                weaponGroup.add(mainBody);

                const topCover = new THREE.Mesh(new THREE.CylinderGeometry(0.033, 0.033, 0.42, 12, 1, false, 0, Math.PI), steelMat);
                topCover.rotation.z = Math.PI / 2;
                topCover.rotation.y = Math.PI / 2;
                topCover.position.set(0, 0.045, 0.01);
                weaponGroup.add(topCover);

                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.12, 0.38), woodMat);
                stock.position.set(0, -0.03, 0.39);
                stock.rotation.x = -0.15;
                weaponGroup.add(stock);

                const grip = new THREE.Mesh(new THREE.BoxGeometry(0.042, 0.15, 0.065), woodMat);
                grip.position.set(0, -0.12, 0.11);
                grip.rotation.x = 0.38;
                weaponGroup.add(grip);

                const lowerHandguard = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.07, 0.28), woodMat);
                lowerHandguard.position.set(0, -0.01, -0.34);
                weaponGroup.add(lowerHandguard);

                const upperHandguard = new THREE.Mesh(new THREE.CylinderGeometry(0.028, 0.028, 0.26, 12), woodMat);
                upperHandguard.rotation.x = Math.PI / 2;
                upperHandguard.position.set(0, 0.035, -0.33);
                weaponGroup.add(upperHandguard);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.78, 12), darkSteelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.6);
                weaponGroup.add(barrel);

                const rearSightBase = new THREE.Mesh(new THREE.BoxGeometry(0.032, 0.035, 0.09), darkSteelMat);
                rearSightBase.position.set(0, 0.062, -0.18);
                const rearSightLeaf = new THREE.Mesh(new THREE.BoxGeometry(0.024, 0.012, 0.06), steelMat);
                rearSightLeaf.position.set(0, 0.078, -0.18);
                weaponGroup.add(rearSightBase);
                weaponGroup.add(rearSightLeaf);

                const gasBlock = new THREE.Mesh(new THREE.BoxGeometry(0.032, 0.065, 0.06), darkSteelMat);
                gasBlock.position.set(0, 0.035, -0.62);
                weaponGroup.add(gasBlock);

                const frontSightBase = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.08, 0.04), darkSteelMat);
                frontSightBase.position.set(0, 0.05, -0.9);
                
                const frontSightPin = new THREE.Mesh(new THREE.CylinderGeometry(0.003, 0.003, 0.03, 8), goldMat);
                frontSightPin.position.set(0, 0.085, -0.9);
                
                const frontSightRing = new THREE.Mesh(new THREE.TorusGeometry(0.018, 0.004, 8, 16), darkSteelMat);
                frontSightRing.position.set(0, 0.085, -0.9);

                weaponGroup.add(frontSightBase);
                weaponGroup.add(frontSightPin);
                weaponGroup.add(frontSightRing);

                const triggerGuard = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.005, 8, 12, Math.PI), darkSteelMat);
                triggerGuard.rotation.y = Math.PI / 2;
                triggerGuard.position.set(0, -0.06, 0.05);
                weaponGroup.add(triggerGuard);

                const boltHandle = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.06, 8), steelMat);
                boltHandle.rotation.z = Math.PI / 2;
                boltHandle.position.set(0.04, 0.03, -0.05);
                weaponGroup.add(boltHandle);

                magazineMesh = new THREE.Group();
                const magTop = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.18, 0.085), magMat);
                magTop.position.set(0, -0.13, -0.02);
                magTop.rotation.x = -0.3;
                magazineMesh.add(magTop);
                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.09, 0.98), woodMat);
                stock.position.set(0, -0.03, -0.1);
                weaponGroup.add(stock);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.15, 12), darkSteelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.02, -0.48);
                weaponGroup.add(barrel);

                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.38, 16), darkSteelMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.082, -0.1);
                weaponGroup.add(scopeBody);

                const scopeFrontRing = new THREE.Mesh(new THREE.CylinderGeometry(0.028, 0.028, 0.05, 16), steelMat);
                scopeFrontRing.rotation.x = Math.PI / 2;
                scopeFrontRing.position.set(0, 0.082, -0.27);
                weaponGroup.add(scopeFrontRing);

                const scopeMount1 = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.04, 0.03), steelMat);
                scopeMount1.position.set(0, 0.05, -0.22);
                const scopeMount2 = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.04, 0.03), steelMat);
                scopeMount2.position.set(0, 0.05, 0.02);
                weaponGroup.add(scopeMount1);
                weaponGroup.add(scopeMount2);

                const boltAction = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.22, 12), steelMat);
                boltAction.rotation.x = Math.PI / 2;
                boltAction.position.set(0, 0.03, 0.12);
                weaponGroup.add(boltAction);

                const boltHandleStem = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.08, 8), steelMat);
                boltHandleStem.rotation.z = Math.PI / 3;
                boltHandleStem.position.set(0.04, 0.02, 0.16);
                
                const boltKnob = new THREE.Mesh(new THREE.SphereGeometry(0.018, 10, 10), darkSteelMat);
                boltKnob.position.set(0.075, -0.01, 0.16);

                weaponGroup.add(boltHandleStem);
                weaponGroup.add(boltKnob);

                const frontSight = new THREE.Mesh(new THREE.ConeGeometry(0.008, 0.03, 4), darkSteelMat);
                frontSight.position.set(0, 0.05, -1.02);
                weaponGroup.add(frontSight);

                magazineMesh = new THREE.Group();
                weaponGroup.add(magazineMesh);

            } else if (type === 'famas') {
                const body = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.13, 0.65), darkSteelMat);
                weaponGroup.add(body);

                const handleTop = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.025, 0.52), darkSteelMat);
                handleTop.position.set(0, 0.13, -0.05);
                weaponGroup.add(handleTop);

                const handleSuppL = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.085, 0.04), darkSteelMat);
                handleSuppL.position.set(0, 0.08, -0.29);
                weaponGroup.add(handleSuppL);

                const handleSuppR = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.085, 0.04), darkSteelMat);
                handleSuppR.position.set(0, 0.08, 0.19);
                weaponGroup.add(handleSuppR);

                const internalRearSight = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.03, 0.02), steelMat);
                internalRearSight.position.set(0, 0.08, 0.12);
                const internalFrontSight = new THREE.Mesh(new THREE.CylinderGeometry(0.003, 0.003, 0.025, 8), goldMat);
                internalFrontSight.position.set(0, 0.08, -0.24);

                weaponGroup.add(internalRearSight);
                weaponGroup.add(internalFrontSight);

                const grip = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.14, 0.065), magMat);
                grip.position.set(0, -0.11, -0.05);
                grip.rotation.x = 0.3;
                weaponGroup.add(grip);

                const triggerGuard = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.06, 0.12), darkSteelMat);
                triggerGuard.position.set(0, -0.09, -0.08);
                weaponGroup.add(triggerGuard);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.42, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.5);
                weaponGroup.add(barrel);

                const flashHider = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.016, 0.08, 12), darkSteelMat);
                flashHider.rotation.x = Math.PI / 2;
                flashHider.position.set(0, 0.01, -0.69);
                weaponGroup.add(flashHider);

                magazineMesh = new THREE.Group();
                const mag = new THREE.Mesh(new THREE.BoxGeometry(0.042, 0.19, 0.08), magMat);
                mag.position.set(0, -0.13, 0.21);
                magazineMesh.add(mag);
                weaponGroup.add(magazineMesh);
            }

            const flashGeo = new THREE.OctahedronGeometry(0.12, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            
            if (type === 'kar98k') muzzleFlashMesh.position.set(0, 0.02, -1.08);
            else if (type === 'famas') muzzleFlashMesh.position.set(0, 0.01, -0.74);
            else muzzleFlashMesh.position.set(0, 0.01, -1.0);

            weaponGroup.add(muzzleFlashMesh);

            weaponGroup.position.set(0.22, -0.22, -0.52);
            camera.add(weaponGroup);
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
            targetGroup.position.y = Math.random() * 2.8 + 0.9;
            targetGroup.position.z = -Math.random() * 8 - 4;

            scene.add(targetGroup);
            targets.push(targetGroup);
        }

        function shoot() {
            if (isReloading || !isGameStarted) return;

            if (ammo <= 0) {
                playEmptyClick();
                document.getElementById('reloadMsg').style.display = 'block';
                return;
            }

            playGunSound(selectedWeapon);

            ammo--;
            totalShots++;
            updateUI();

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

            // 중앙 화면 고정 레이캐스팅
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);

            const intersects = raycaster.intersectObjects(scene.children, true);

            for (let i = 0; i < intersects.length; i++) {
                let hitParent = intersects[i].object.parent;
                if (targets.includes(hitParent)) {
                    scene.remove(hitParent);
                    targets = targets.filter(t => t !== hitParent);
                    
                    score += (selectedWeapon === 'kar98k') ? 150 : 100;
                    hits++;
                    updateUI();
                    createTarget();
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
            playReloadSound();
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
            document.getElementById('warningText').innerText = "⚠️ FLASHBANG INCOMING! (고개를 빠르게 돌리세요!)";

            setTimeout(() => {
                document.getElementById('warningText').innerText = "";
                // 고개를 충분히 돌리지 않은 경우(정면을 보고 있을 때) 뱅 효과
                if (Math.abs(yaw % (Math.PI * 2)) < 0.8 && isGameStarted) {
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
                // 카메라 회전 적용 (Euler 오더: YXZ)
                camera.rotation.order = 'YXZ';
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;

                // 총기 마우스 움직임 반사 (Weapon Sway)
                weaponGroup.position.x = 0.22 - mouseDeltaX * 0.0003;
                weaponGroup.position.y = -0.22 + mouseDeltaY * 0.0003;

                mouseDeltaX *= 0.85;
                mouseDeltaY *= 0.85;

                // 반동 감쇄
                if (recoilZ > 0) {
                    recoilZ -= 0.02;
                    if (recoilZ < 0) recoilZ = 0;
                }
                if (recoilRotX > 0) {
                    recoilRotX -= 0.015;
                    if (recoilRotX < 0) recoilRotX = 0;
                }

                weaponGroup.position.z = -0.52 + recoilZ;
                weaponGroup.rotation.x = recoilRotX;
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
