import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D AimLab - Realistic Guns & Moving Human Targets", layout="centered")

st.title("⚡ 3D AimLab (리얼 총기 & 이동 사람 타겟 & 원형 과녁)")
st.caption("현실적인 총기 모델링, 움직이는 사람 타겟, 원형 과녁 및 마우스 커서 추적 십자선이 적용되었습니다.")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #0e111a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
            cursor: none; /* 게임 내 마우스 커서 숨김 */
        }
        #ui-panel {
            position: absolute;
            top: 15px;
            left: 20px;
            color: #00f0ff;
            font-size: 18px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.8);
            pointer-events: none;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .main-menu-btn {
            pointer-events: auto;
            background: rgba(20, 30, 50, 0.9);
            color: #ff0055;
            border: 1px solid #ff0055;
            padding: 6px 14px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: 0.2s;
            box-shadow: 0 0 8px rgba(255, 0, 85, 0.4);
        }
        .main-menu-btn:hover {
            background: #ff0055;
            color: #fff;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.8);
        }
        #ammo-panel {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: #00f0ff;
            font-size: 28px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 12px rgba(0, 240, 255, 0.8);
            pointer-events: none;
            text-align: right;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 12px;
            height: 12px;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 15;
            display: none;
        }
        #crosshair::before, #crosshair::after {
            content: '';
            position: absolute;
            background: #00f0ff;
            box-shadow: 0 0 8px #00f0ff;
        }
        #crosshair::before {
            top: 5px; left: -8px; width: 28px; height: 2px;
        }
        #crosshair::after {
            top: -8px; left: 5px; width: 2px; height: 28px;
        }
        #reloadMsg {
            font-size: 16px;
            color: #ff0055;
            display: none;
        }
        #startOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(11, 13, 23, 0.95);
            backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 30;
            color: white;
            cursor: default;
        }
        .section-title {
            color: #00f0ff;
            font-size: 14px;
            font-weight: bold;
            margin-top: 14px;
            margin-bottom: 6px;
            letter-spacing: 1.5px;
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
        }
        .btn-container {
            display: flex;
            gap: 12px;
        }
        .option-btn {
            background: #1c2338;
            color: #a0b0d0;
            border: 2px solid #2d3859;
            padding: 8px 18px;
            font-size: 15px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: 0.2s;
        }
        .option-btn.selected {
            background: #00f0ff;
            color: #080911;
            border-color: #00f0ff;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.6);
        }
        .start-btn {
            background: linear-gradient(135deg, #ff0055, #9900ff);
            color: white;
            border: none;
            padding: 12px 45px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 4px;
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.6);
            margin-top: 22px;
            cursor: pointer;
            transition: 0.2s;
        }
        .start-btn:hover {
            transform: scale(1.06);
            box-shadow: 0 0 30px rgba(255, 0, 85, 0.9);
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body oncontextmenu="return false;">
    <div id="ui-panel">
        <button class="main-menu-btn" onclick="goToMainMenu()">🏠 메인으로 (E)</button>
        <div>점수: <span id="score" style="color:#00f0ff">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%</div>
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">30</span> / <span id="maxAmmo">30</span>
        <div id="reloadMsg">[R] 키를 눌러 탄창 교체!</div>
    </div>
    <div id="crosshair"></div>

    <div id="startOverlay">
        <h1 style="color: #00f0ff; text-shadow: 0 0 20px rgba(0,240,255,0.8); margin-bottom: 2px; font-size: 32px;">CYBERPUNK AIMLAB</h1>
        <p style="color: #a0b0d0; margin-bottom: 15px; font-size: 14px;">마우스 이동: 시선/총기 조준 | <b>[F] 키 또는 좌클릭: 사격</b> | [R]: 장전</p>

        <div class="section-title">GUN SELECT</div>
        <div class="btn-container">
            <button class="option-btn selected" onclick="selectWeapon('ak47', this)">REAL AK-47</button>
            <button class="option-btn" onclick="selectWeapon('kar98k', this)">REAL KAR98K</button>
            <button class="option-btn" onclick="selectWeapon('famas', this)">REAL FAMAS</button>
        </div>

        <button class="start-btn" onclick="initGame()">시 작 하 기</button>
    </div>

    <script>
        let audioCtx = null;

        function initAudio() {
            try {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
                if (audioCtx.state === 'suspended') {
                    audioCtx.resume();
                }
            } catch(e){}
        }

        function playGunSound(type) {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const bufferSize = audioCtx.sampleRate * 0.25;
            const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const output = buffer.getChannelData(0);

            for (let i = 0; i < bufferSize; i++) {
                output[i] = Math.random() * 2 - 1;
            }

            const noise = audioCtx.createBufferSource();
            noise.buffer = buffer;

            const filter = audioCtx.createBiquadFilter();
            const gain = audioCtx.createGain();

            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(type === 'kar98k' ? 700 : (type === 'ak47' ? 1100 : 1400), now);
            filter.frequency.exponentialRampToValueAtTime(80, now + 0.25);
            gain.gain.setValueAtTime(1.5, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start(now);
        }

        function playReloadSound() {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(450, now);
            osc.frequency.linearRampToValueAtTime(180, now + 0.3);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.35);
        }

        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        let selectedWeapon = 'ak47';
        let maxAmmo = 30;
        let ammo = 30;

        let isReloading = false;
        let isGameStarted = false;

        let weaponGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        let targetYaw = 0, targetPitch = 0;
        let currentYaw = 0, currentPitch = 0;

        let mouseNDC = new THREE.Vector2(0, 0); // 마우스 커서 Raycast용 NDC 좌표

        const keys = { w: false, a: false, s: false, d: false };
        const moveSpeed = 0.12;

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

        function initGame() {
            initAudio();
            document.getElementById('startOverlay').style.display = 'none';
            document.getElementById('crosshair').style.display = 'block';
            
            score = 0;
            totalShots = 0;
            hits = 0;
            ammo = maxAmmo;
            isReloading = false;
            targetYaw = 0;
            targetPitch = 0;
            currentYaw = 0;
            currentPitch = 0;
            updateUI();
            document.getElementById('reloadMsg').style.display = 'none';

            if (!scene) {
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0e111a);
                scene.fog = new THREE.FogExp2(0x0e111a, 0.005);

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 5000);
                camera.position.set(0, 1.6, 5);

                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, 500);
                document.body.appendChild(renderer.domElement);

                const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(ambientLight);

                const dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
                dirLight.position.set(10, 20, 10);
                scene.add(dirLight);

                const cyanLight = new THREE.PointLight(0x00f0ff, 2.0, 40);
                cyanLight.position.set(0, 6, 0);
                scene.add(cyanLight);

                const floorGeo = new THREE.PlaneGeometry(200, 200);
                const floorMat = new THREE.MeshStandardMaterial({ color: 0x141824, roughness: 0.2 });
                const floor = new THREE.Mesh(floorGeo, floorMat);
                floor.rotation.x = -Math.PI / 2;
                scene.add(floor);

                const gridHelper = new THREE.GridHelper(200, 100, 0x00f0ff, 0x27334d);
                gridHelper.position.y = 0.01;
                scene.add(gridHelper);

                // 마우스 커서 따라다니는 십자선 & 조준 처리
                window.addEventListener('mousemove', (e) => {
                    if (!isGameStarted) return;
                    const rect = renderer.domElement.getBoundingClientRect();
                    
                    // 십자선을 마우스 위치로 이동
                    const crosshair = document.getElementById('crosshair');
                    crosshair.style.left = e.clientX + 'px';
                    crosshair.style.top = e.clientY + 'px';

                    const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    const mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                    mouseNDC.set(mouseX, mouseY);

                    targetYaw = -mouseX * 1.35;
                    targetPitch = mouseY * 0.75;
                });

                window.addEventListener('keydown', (e) => {
                    const k = e.key.toLowerCase();
                    if (k in keys) keys[k] = true;

                    if (isGameStarted) {
                        if (k === 'e') goToMainMenu();
                        if (k === 'r') reload();
                        if (k === 'f') shoot();
                    }
                });

                window.addEventListener('keyup', (e) => {
                    const k = e.key.toLowerCase();
                    if (k in keys) keys[k] = false;
                });

                window.addEventListener('mousedown', (e) => {
                    if (e.button === 0 && isGameStarted) {
                        shoot();
                    }
                });

                animate();
            }

            camera.position.set(0, 1.6, 5);

            if (weaponGroup) camera.remove(weaponGroup);
            buildWeaponModel(selectedWeapon);

            targets.forEach(t => scene.remove(t.group));
            targets = [];
            
            // 움직이는 사람 타겟 4명 생성
            for (let i = 0; i < 4; i++) {
                createHumanTarget();
            }

            // 원형 과녁 타겟 4개 생성
            for (let i = 0; i < 4; i++) {
                createDiscTarget();
            }

            isGameStarted = true;
        }

        function goToMainMenu() {
            isGameStarted = false;
            document.getElementById('crosshair').style.display = 'none';
            document.getElementById('startOverlay').style.display = 'flex';
        }

        function buildWeaponModel(type) {
            weaponGroup = new THREE.Group();

            const steelMat = new THREE.MeshStandardMaterial({ color: 0x22262e, roughness: 0.3, metalness: 0.9 });
            const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x111317, roughness: 0.4, metalness: 0.95 });
            const woodMat = new THREE.MeshStandardMaterial({ color: 0x6e3319, roughness: 0.5, metalness: 0.05 });
            const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x421e0f, roughness: 0.6, metalness: 0.05 });
            const famasMat = new THREE.MeshStandardMaterial({ color: 0x1f232b, roughness: 0.6, metalness: 0.2 });

            if (type === 'ak47') {
                // 리얼 AK-47
                const receiver = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.08, 0.42), steelMat);
                weaponGroup.add(receiver);

                const topCover = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.4, 12, 1, false, 0, Math.PI), steelMat);
                topCover.rotation.x = Math.PI / 2;
                topCover.rotation.z = Math.PI;
                topCover.position.set(0, 0.04, -0.01);
                weaponGroup.add(topCover);

                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.11, 0.35), woodMat);
                stock.position.set(0, -0.02, 0.35);
                stock.rotation.x = -0.15;
                weaponGroup.add(stock);

                const handguardLower = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.06, 0.28), woodMat);
                handguardLower.position.set(0, -0.01, -0.32);
                weaponGroup.add(handguardLower);

                const handguardUpper = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.25, 12), woodMat);
                handguardUpper.rotation.x = Math.PI / 2;
                handguardUpper.position.set(0, 0.035, -0.32);
                weaponGroup.add(handguardUpper);

                const grip = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.12, 0.05), woodMat);
                grip.position.set(0, -0.1, 0.12);
                grip.rotation.x = -0.4;
                weaponGroup.add(grip);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.65, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.015, -0.62);
                weaponGroup.add(barrel);

                const gasTube = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.35, 12), darkSteelMat);
                gasTube.rotation.x = Math.PI / 2;
                gasTube.position.set(0, 0.045, -0.45);
                weaponGroup.add(gasTube);

                const frontSight = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.06, 0.03), steelMat);
                frontSight.position.set(0, 0.055, -0.88);
                weaponGroup.add(frontSight);

                // 리얼 곡선 탄창
                magazineMesh = new THREE.Group();
                const m1 = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.12, 0.07), darkSteelMat);
                m1.position.set(0, 0, 0);
                m1.rotation.x = -0.35;
                const m2 = new THREE.Mesh(new THREE.BoxGeometry(0.036, 0.12, 0.065), darkSteelMat);
                m2.position.set(0, -0.09, -0.035);
                m2.rotation.x = -0.65;
                magazineMesh.add(m1);
                magazineMesh.add(m2);
                magazineMesh.position.set(0, -0.1, -0.05);
                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                // 리얼 KAR98K
                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.068, 1.25), darkWoodMat);
                stock.position.set(0, -0.02, -0.2);
                weaponGroup.add(stock);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.011, 1.1, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.022, -0.72);
                weaponGroup.add(barrel);

                const boltReceiver = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.25, 12), steelMat);
                boltReceiver.rotation.x = Math.PI / 2;
                boltReceiver.position.set(0, 0.025, 0.05);
                weaponGroup.add(boltReceiver);

                const boltHandle = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.08, 8), darkSteelMat);
                boltHandle.rotation.z = Math.PI / 3;
                boltHandle.position.set(0.04, 0.02, 0.08);
                weaponGroup.add(boltHandle);

                const boltKnob = new THREE.Mesh(new THREE.SphereGeometry(0.014, 8, 8), darkSteelMat);
                boltKnob.position.set(0.075, -0.01, 0.08);
                weaponGroup.add(boltKnob);

                // 스코프 및 마운트
                const scopeMount = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.04, 0.15), darkSteelMat);
                scopeMount.position.set(0, 0.065, -0.12);
                weaponGroup.add(scopeMount);

                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.42, 16), darkSteelMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.09, -0.12);
                weaponGroup.add(scopeBody);

                const triggerGuard = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.05, 0.12), steelMat);
                triggerGuard.position.set(0, -0.06, 0.05);
                weaponGroup.add(triggerGuard);

                magazineMesh = new THREE.Group();
                const dummy = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.04, 0.08), steelMat);
                magazineMesh.add(dummy);
                magazineMesh.position.set(0, -0.04, -0.08);
                weaponGroup.add(magazineMesh);

            } else if (type === 'famas') {
                // 리얼 FAMAS Bullpup
                const mainBody = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.12, 0.68), famasMat);
                weaponGroup.add(mainBody);

                const carryHandle = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.1, 0.52), famasMat);
                carryHandle.position.set(0, 0.1, -0.02);
                weaponGroup.add(carryHandle);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.013, 0.45, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.52);
                weaponGroup.add(barrel);

                const flashHider = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.08, 12), darkSteelMat);
                flashHider.rotation.x = Math.PI / 2;
                flashHider.position.set(0, 0.01, -0.72);
                weaponGroup.add(flashHider);

                const handguardGrip = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.1, 0.06), famasMat);
                handguardGrip.position.set(0, -0.08, -0.18);
                handguardGrip.rotation.x = -0.2;
                weaponGroup.add(handguardGrip);

                // 불펍 후방 탄창
                magazineMesh = new THREE.Group();
                const mag = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.16, 0.07), darkSteelMat);
                magazineMesh.add(mag);
                magazineMesh.position.set(0, -0.12, 0.22);
                weaponGroup.add(magazineMesh);
            }

            const flashGeo = new THREE.OctahedronGeometry(0.12, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.position.set(0, 0.01, -0.92);
            weaponGroup.add(muzzleFlashMesh);

            weaponGroup.position.set(0.22, -0.22, -0.52);
            camera.add(weaponGroup);
            scene.add(camera);
        }

        // 원형 과녁 타겟 생성 함수
        function createDiscTarget() {
            const discGroup = new THREE.Group();

            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 256;
            const ctx = canvas.getContext('2d');

            ctx.fillStyle = '#1c2338';
            ctx.fillRect(0, 0, 256, 256);

            const colors = ['#ff0055', '#00f0ff', '#ffffff', '#ff0055'];
            const radii = [120, 90, 60, 30];

            radii.forEach((r, idx) => {
                ctx.beginPath();
                ctx.arc(128, 128, r, 0, Math.PI * 2);
                ctx.fillStyle = colors[idx];
                ctx.fill();
            });

            const texture = new THREE.CanvasTexture(canvas);
            const discGeo = new THREE.CylinderGeometry(0.48, 0.48, 0.06, 32);
            const discMat = [
                new THREE.MeshStandardMaterial({ color: 0x2b3552 }),
                new THREE.MeshStandardMaterial({ map: texture, roughness: 0.1 }),
                new THREE.MeshStandardMaterial({ color: 0x181e30 })
            ];

            const disc = new THREE.Mesh(discGeo, discMat);
            disc.rotation.x = Math.PI / 2;
            disc.userData = { type: 'disc' };
            discGroup.add(disc);

            discGroup.position.x = (Math.random() - 0.5) * 16;
            discGroup.position.y = Math.random() * 3.2 + 0.8;
            discGroup.position.z = -Math.random() * 20 - 5;

            const targetObj = {
                type: 'disc',
                group: discGroup,
                hp: 1, // 과녁은 1발에 즉시 파괴
                speed: 0
            };

            scene.add(discGroup);
            targets.push(targetObj);
        }

        // 사람 마네킹 생성 함수 (머리 1발 / 몸통 4발 판정)
        function createHumanTarget() {
            const humanGroup = new THREE.Group();
            const skinMat = new THREE.MeshStandardMaterial({ color: 0x3a4b6e, roughness: 0.5 });
            const headMat = new THREE.MeshStandardMaterial({ color: 0xff0055, roughness: 0.3 }); // 머리 강조

            // 머리 (Head) - 1발 분량
            const headGeo = new THREE.SphereGeometry(0.22, 16, 16);
            const headMesh = new THREE.Mesh(headGeo, headMat);
            headMesh.position.y = 1.65;
            headMesh.userData = { type: 'head' };
            humanGroup.add(headMesh);

            // 몸통 (Body) - 4발 분량
            const bodyGeo = new THREE.BoxGeometry(0.5, 0.75, 0.28);
            const bodyMesh = new THREE.Mesh(bodyGeo, skinMat);
            bodyMesh.position.y = 1.05;
            bodyMesh.userData = { type: 'body' };
            humanGroup.add(bodyMesh);

            // 팔 (Arms)
            const armGeo = new THREE.BoxGeometry(0.14, 0.65, 0.14);
            const leftArm = new THREE.Mesh(armGeo, skinMat);
            leftArm.position.set(-0.36, 1.05, 0);
            leftArm.userData = { type: 'body' };
            humanGroup.add(leftArm);

            const rightArm = new THREE.Mesh(armGeo, skinMat);
            rightArm.position.set(0.36, 1.05, 0);
            rightArm.userData = { type: 'body' };
            humanGroup.add(rightArm);

            // 다리 (Legs)
            const legGeo = new THREE.BoxGeometry(0.18, 0.7, 0.18);
            const leftLeg = new THREE.Mesh(legGeo, skinMat);
            leftLeg.position.set(-0.16, 0.35, 0);
            leftLeg.userData = { type: 'body' };
            humanGroup.add(leftLeg);

            const rightLeg = new THREE.Mesh(legGeo, skinMat);
            rightLeg.position.set(0.16, 0.35, 0);
            rightLeg.userData = { type: 'body' };
            humanGroup.add(rightLeg);

            // 위치 및 이동 데이터 초기화
            const posX = (Math.random() - 0.5) * 14;
            const posZ = -Math.random() * 15 - 6;
            humanGroup.position.set(posX, 0, posZ);

            const targetObj = {
                type: 'human',
                group: humanGroup,
                hp: 4, // 기본 몸통 HP = 4
                speed: (Math.random() * 0.04 + 0.03) * (Math.random() > 0.5 ? 1 : -1),
                minX: posX - 4,
                maxX: posX + 4
            };

            scene.add(humanGroup);
            targets.push(targetObj);
        }

        function shoot() {
            if (isReloading || !isGameStarted) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'block';
                return;
            }

            playGunSound(selectedWeapon);

            ammo--;
            totalShots++;
            updateUI();

            recoilZ = 0.16;
            recoilRotX = 0.14;

            muzzleFlashMesh.material.opacity = 1.0;
            setTimeout(() => { muzzleFlashMesh.material.opacity = 0; }, 35);

            const raycaster = new THREE.Raycaster();
            raycaster.far = Infinity;
            // 마우스 커서 위치를 향해 사격 (마우스 추적 사격)
            raycaster.setFromCamera(mouseNDC, camera);

            const intersects = raycaster.intersectObjects(scene.children, true);

            for (let i = 0; i < intersects.length; i++) {
                const hitMesh = intersects[i].object;
                
                // 피격 타겟 확인 (사람 또는 과녁)
                let hitTargetIndex = -1;
                for (let t = 0; t < targets.length; t++) {
                    if (targets[t].group === hitMesh.parent || targets[t].group === hitMesh.parent?.parent) {
                        hitTargetIndex = t;
                        break;
                    }
                }

                if (hitTargetIndex !== -1) {
                    const target = targets[hitTargetIndex];
                    hits++;

                    if (target.type === 'disc') {
                        target.hp = 0; // 과녁은 1발에 파괴
                    } else if (target.type === 'human') {
                        // 머리 피격 시 즉시 사망(HP 4 감소), 몸통/팔다리 피격 시 HP 1 감소
                        if (hitMesh.userData.type === 'head') {
                            target.hp -= 4;
                        } else {
                            target.hp -= 1;
                        }
                    }

                    // 피격 반사 피드백
                    if (hitMesh.material && hitMesh.material.emissive) {
                        hitMesh.material.emissive = new THREE.Color(0xff0000);
                        setTimeout(() => {
                            if (hitMesh.material) hitMesh.material.emissive = new THREE.Color(0x000000);
                        }, 60);
                    }

                    // HP 모두 소모 시 타겟 제거 및 동일 타입 재생성
                    if (target.hp <= 0) {
                        scene.remove(target.group);
                        const targetType = target.type;
                        targets.splice(hitTargetIndex, 1);
                        score += 100;

                        if (targetType === 'human') {
                            createHumanTarget();
                        } else if (targetType === 'disc') {
                            createDiscTarget();
                        }
                    }

                    updateUI();
                    break;
                }
            }
        }

        function reload() {
            if (isReloading || ammo === maxAmmo || !isGameStarted) return;
            isReloading = true;
            playReloadSound();

            const initY = magazineMesh.position.y;
            let progress = 0;

            const reloadInterval = setInterval(() => {
                progress += 0.04;

                if (progress <= 0.4) {
                    const p = progress / 0.4;
                    magazineMesh.position.y = initY - p * 0.25;
                    magazineMesh.rotation.y = 0;
                } else if (progress <= 0.7) {
                    const p = (progress - 0.4) / 0.3;
                    magazineMesh.rotation.y = p * Math.PI;
                } else if (progress <= 1.0) {
                    const p = (progress - 0.7) / 0.3;
                    magazineMesh.position.y = (initY - 0.25) + p * 0.25;
                    magazineMesh.rotation.y = Math.PI * (1 + p);
                } else {
                    clearInterval(reloadInterval);
                    magazineMesh.position.y = initY;
                    magazineMesh.rotation.y = 0;
                    ammo = maxAmmo;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
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

        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                // 플레이어 이동 조작
                const moveVector = new THREE.Vector3(0, 0, 0);
                if (keys.w) moveVector.z -= 1;
                if (keys.s) moveVector.z += 1;
                if (keys.a) moveVector.x -= 1;
                if (keys.d) moveVector.x += 1;

                if (moveVector.lengthSq() > 0) {
                    moveVector.normalize();
                    moveVector.applyAxisAngle(new THREE.Vector3(0, 1, 0), currentYaw);
                    camera.position.addScaledVector(moveVector, moveSpeed);

                    camera.position.x = Math.max(-15, Math.min(15, camera.position.x));
                    camera.position.z = Math.max(-10, Math.min(20, camera.position.z));
                }

                currentYaw += (targetYaw - currentYaw) * 0.15;
                currentPitch += (targetPitch - currentPitch) * 0.15;

                camera.rotation.order = 'YXZ';
                camera.rotation.y = currentYaw;
                camera.rotation.x = currentPitch;

                // 총기 반동
                if (recoilZ > 0) recoilZ -= 0.02;
                if (recoilRotX > 0) recoilRotX -= 0.015;

                weaponGroup.position.z = -0.52 + Math.max(0, recoilZ);
                weaponGroup.rotation.x = Math.max(0, recoilRotX);

                // 사람 타겟 좌우 왕복 이동 애니메이션
                targets.forEach(t => {
                    if (t.type === 'human') {
                        t.group.position.x += t.speed;
                        if (t.group.position.x > t.maxX || t.group.position.x < t.minX) {
                            t.speed *= -1; // 방향 전환
                        }
                    }
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

components.html(game_code, height=540
