import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Cyber Portal Edition", layout="centered")

st.title("⚡ 3D Cyberpunk AimLab (Portal Reload Edition)")
st.caption("WASD 자유 이동, 총기 옆 차원 포탈 장전 애니메이션, 사이버 맵 디자인이 모두 통합되었습니다.")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #080911;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
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
            background: rgba(10, 15, 30, 0.8);
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
            box-shadow: 0 0 6px #00f0ff;
        }
        #crosshair::before {
            top: 5px; left: -8px; width: 28px; height: 2px;
        }
        #crosshair::after {
            top: -8px; left: 5px; width: 2px; height: 28px;
        }
        #warningText {
            position: absolute;
            top: 60px;
            width: 100%;
            text-align: center;
            color: #ff0055;
            font-size: 22px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 10px rgba(255, 0, 85, 0.9);
            pointer-events: none;
        }
        #flashOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: cyan;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.1s;
            z-index: 20;
        }
        #startOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(8, 9, 17, 0.94);
            backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 30;
            color: white;
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
            background: #121526;
            color: #a0b0d0;
            border: 2px solid #202744;
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
<body>
    <div id="ui-panel">
        <button class="main-menu-btn" onclick="goToMainMenu()">🏠 메인으로 (E)</button>
        <div>점수: <span id="score" style="color:#00f0ff">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%</div>
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">30</span> / <span id="maxAmmo">30</span>
        <div id="reloadMsg" style="font-size:16px; color:#ff0055; display:none;">[R] 키를 눌러 차원 재장전!</div>
    </div>
    <div id="crosshair"></div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #00f0ff; text-shadow: 0 0 20px rgba(0,240,255,0.8); margin-bottom: 2px; font-size: 34px;">CYBER AIMLAB 3D</h1>
        <p style="color: #8a9bbd; margin-bottom: 15px; font-size: 14px;">WASD로 이동 | 마우스로 사격 | R: 차원 포탈 장전 | E: 메인 메뉴</p>

        <div class="section-title">GUN SELECT</div>
        <div class="btn-container">
            <button class="option-btn selected" onclick="selectWeapon('ak47', this)">CYBER AK</button>
            <button class="option-btn" onclick="selectWeapon('kar98k', this)">NEON SNIPER</button>
            <button class="option-btn" onclick="selectWeapon('famas', this)">PLASMA FAMAS</button>
        </div>

        <div class="section-title">TARGET SIZE</div>
        <div class="btn-container">
            <button class="option-btn" onclick="selectDiff('easy', this)">LARGE</button>
            <button class="option-btn selected" onclick="selectDiff('normal', this)">NORMAL</button>
            <button class="option-btn" onclick="selectDiff('hard', this)">SMALL</button>
        </div>

        <button class="start-btn" onclick="initGame()">시 작 하 기</button>
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
            const bufferSize = audioCtx.sampleRate * 0.4;
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
                filter.frequency.setValueAtTime(1000, now);
                filter.frequency.exponentialRampToValueAtTime(120, now + 0.3);
                gain.gain.setValueAtTime(1.3, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
            } else if (type === 'kar98k') {
                filter.type = 'lowpass';
                filter.frequency.setValueAtTime(3500, now);
                filter.frequency.exponentialRampToValueAtTime(60, now + 0.45);
                gain.gain.setValueAtTime(1.7, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
            } else if (type === 'famas') {
                filter.type = 'highpass';
                filter.frequency.setValueAtTime(1500, now);
                filter.frequency.exponentialRampToValueAtTime(250, now + 0.2);
                gain.gain.setValueAtTime(1.1, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
            }

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start(now);
        }

        function playPortalReloadSound() {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            
            // 차원 포탈 오픈 라이징 사운드
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(150, now);
            osc.frequency.exponentialRampToValueAtTime(1200, now + 0.6);
            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.8);
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.8);
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
        let portalGroup, portalRingMesh;
        let recoilZ = 0, recoilRotX = 0;

        // 마우스 & 카메라 제어
        let yaw = 0, pitch = 0;
        let mouseDeltaX = 0, mouseDeltaY = 0;
        const sensitivity = 0.0022;

        // WASD 이동 변수
        const keys = { w: false, a: false, s: false, d: false };
        const moveSpeed = 0.12;
        let walkTimer = 0;

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
                scene.background = new THREE.Color(0x06070c);
                scene.fog = new THREE.FogExp2(0x06070c, 0.02);

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
                camera.position.set(0, 1.6, 5);

                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, 500);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);

                // 라이팅 설정
                const ambientLight = new THREE.AmbientLight(0x1a2035, 1.2);
                scene.add(ambientLight);

                const cyanLight = new THREE.PointLight(0x00f0ff, 2, 25);
                cyanLight.position.set(0, 6, 0);
                scene.add(cyanLight);

                const magentaLight = new THREE.PointLight(0xff0055, 2, 25);
                magentaLight.position.set(0, 3, -10);
                scene.add(magentaLight);

                // 사이버 바닥 (그리드)
                const floorGeo = new THREE.PlaneGeometry(80, 80);
                const floorMat = new THREE.MeshStandardMaterial({ color: 0x090b14, roughness: 0.2, metalness: 0.8 });
                const floor = new THREE.Mesh(floorGeo, floorMat);
                floor.rotation.x = -Math.PI / 2;
                scene.add(floor);

                const gridHelper = new THREE.GridHelper(80, 40, 0x00f0ff, 0x182035);
                gridHelper.position.y = 0.01;
                scene.add(gridHelper);

                // 네온 정면 벽면
                const wallGeo = new THREE.PlaneGeometry(80, 35);
                const wallMat = new THREE.MeshStandardMaterial({ color: 0x0b0d18, roughness: 0.5 });
                const backWall = new THREE.Mesh(wallGeo, wallMat);
                backWall.position.set(0, 17.5, -25);
                scene.add(backWall);

                const wallGrid = new THREE.GridHelper(80, 30, 0xff0055, 0x201530);
                wallGrid.rotation.x = Math.PI / 2;
                wallGrid.position.set(0, 17.5, -24.9);
                scene.add(wallGrid);

                // 이벤트 리스너 등록
                document.addEventListener('mousemove', (e) => {
                    if (document.pointerLockElement === renderer.domElement && isGameStarted) {
                        mouseDeltaX = e.movementX || 0;
                        mouseDeltaY = e.movementY || 0;

                        yaw -= mouseDeltaX * sensitivity;
                        pitch -= mouseDeltaY * sensitivity;
                        pitch = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, pitch));
                    }
                });

                window.addEventListener('keydown', (e) => {
                    const k = e.key.toLowerCase();
                    if (k in keys) keys[k] = true;

                    if (isGameStarted) {
                        if (k === 'e') goToMainMenu();
                        if (k === 'r') reload();
                    }
                });

                window.addEventListener('keyup', (e) => {
                    const k = e.key.toLowerCase();
                    if (k in keys) keys[k] = false;
                });

                window.addEventListener('mousedown', (e) => {
                    if (e.button === 0 && isGameStarted) {
                        if (document.pointerLockElement !== renderer.domElement) {
                            requestLock();
                        } else {
                            shoot();
                        }
                    }
                });

                document.addEventListener('pointerlockchange', () => {
                    if (document.pointerLockElement !== renderer.domElement && isGameStarted) {
                        goToMainMenu();
                    }
                });

                animate();
            }

            camera.position.set(0, 1.6, 5);
            requestLock();

            if (weaponGroup) camera.remove(weaponGroup);
            buildWeaponModel(selectedWeapon);
            buildPortalModel();

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

        // 🌀 차원 포탈 생성
        function buildPortalModel() {
            portalGroup = new THREE.Group();
            
            const ringGeo = new THREE.TorusGeometry(0.18, 0.025, 16, 32);
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x9900ff, wireframe: true });
            portalRingMesh = new THREE.Mesh(ringGeo, ringMat);
            portalGroup.add(portalRingMesh);

            const coreGeo = new THREE.CircleGeometry(0.16, 32);
            const coreMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.7, side: THREE.DoubleSide });
            const core = new THREE.Mesh(coreGeo, coreMat);
            portalGroup.add(core);

            portalGroup.position.set(0.42, -0.05, -0.45);
            portalGroup.scale.set(0.001, 0.001, 0.001); // 초기 숨김 상태
            
            weaponGroup.add(portalGroup);
        }

        function buildWeaponModel(type) {
            weaponGroup = new THREE.Group();

            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x151822, roughness: 0.2, metalness: 0.9 });
            const neonCyanMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
            const neonMagentaMat = new THREE.MeshBasicMaterial({ color: 0xff0055 });
            const magMat = new THREE.MeshStandardMaterial({ color: 0x22283a, roughness: 0.3, metalness: 0.8 });

            if (type === 'ak47') {
                const mainBody = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.09, 0.44), bodyMat);
                weaponGroup.add(mainBody);

                const stripe1 = new THREE.Mesh(new THREE.BoxGeometry(0.068, 0.02, 0.3), neonCyanMat);
                stripe1.position.set(0, 0.02, -0.05);
                weaponGroup.add(stripe1);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.75, 12), bodyMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.58);
                weaponGroup.add(barrel);

                const frontSight = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.06, 0.03), neonMagentaMat);
                frontSight.position.set(0, 0.06, -0.88);
                weaponGroup.add(frontSight);

                magazineMesh = new THREE.Group();
                const magTop = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.18, 0.085), magMat);
                magTop.position.set(0, -0.13, -0.02);
                magTop.rotation.x = -0.3;
                
                const magNeon = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.02, 0.088), neonCyanMat);
                magNeon.position.set(0, -0.18, -0.04);
                magNeon.rotation.x = -0.3;

                magazineMesh.add(magTop);
                magazineMesh.add(magNeon);
                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.08, 0.95), bodyMat);
                stock.position.set(0, -0.03, -0.1);
                weaponGroup.add(stock);

                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.4, 16), bodyMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.085, -0.1);
                weaponGroup.add(scopeBody);

                const scopeGlow = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.02, 16), neonCyanMat);
                scopeGlow.rotation.x = Math.PI / 2;
                scopeGlow.position.set(0, 0.085, -0.29);
                weaponGroup.add(scopeGlow);

                magazineMesh = new THREE.Group();
                weaponGroup.add(magazineMesh);

            } else if (type === 'famas') {
                const body = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.13, 0.65), bodyMat);
                weaponGroup.add(body);

                const handleTop = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.025, 0.52), bodyMat);
                handleTop.position.set(0, 0.13, -0.05);
                weaponGroup.add(handleTop);

                const neonLine = new THREE.Mesh(new THREE.BoxGeometry(0.072, 0.015, 0.48), neonMagentaMat);
                neonLine.position.set(0, 0.02, -0.05);
                weaponGroup.add(neonLine);

                magazineMesh = new THREE.Group();
                const mag = new THREE.Mesh(new THREE.BoxGeometry(0.042, 0.19, 0.08), magMat);
                mag.position.set(0, -0.13, 0.21);
                magazineMesh.add(mag);
                weaponGroup.add(magazineMesh);
            }

            const flashGeo = new THREE.OctahedronGeometry(0.12, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.position.set(0, 0.01, -0.9);
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

            ctx.fillStyle = '#06070c';
            ctx.fillRect(0,0,256,256);

            const colors = ['#ff0055', '#00f0ff', '#ffffff', '#ff0055'];
            const radii = [120, 90, 60, 30];

            radii.forEach((r, idx) => {
                ctx.beginPath();
                ctx.arc(128, 128, r, 0, Math.PI * 2);
                ctx.fillStyle = colors[idx];
                ctx.fill();
            });

            const texture = new THREE.CanvasTexture(canvas);
            
            const discGeo = new THREE.CylinderGeometry(targetRadius, targetRadius, 0.06, 32);
            const discMat = [
                new THREE.MeshStandardMaterial({ color: 0x111525 }),
                new THREE.MeshStandardMaterial({ map: texture, roughness: 0.2 }),
                new THREE.MeshStandardMaterial({ color: 0x05070e })
            ];

            const disc = new THREE.Mesh(discGeo, discMat);
            disc.rotation.x = Math.PI / 2;
            targetGroup.add(disc);

            targetGroup.position.x = (Math.random() - 0.5) * 14;
            targetGroup.position.y = Math.random() * 3.2 + 0.8;
            targetGroup.position.z = -Math.random() * 10 - 5;

            scene.add(targetGroup);
            targets.push(targetGroup);
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

            recoilZ = 0.18;
            recoilRotX = 0.16;

            muzzleFlashMesh.material.opacity = 1.0;
            setTimeout(() => {
                muzzleFlashMesh.material.opacity = 0;
            }, 35);

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);

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
                document.getElementById('reloadMsg').style.display = 'block';
            }
        }

        // 🌀 차원 포탈 재장전 로직
        function reload() {
            if (isReloading || ammo === maxAmmo || !isGameStarted) return;
            isReloading = true;
            playPortalReloadSound();
            document.getElementById('reloadMsg').innerText = "차원 포탈 탄창 생성 중...";

            let progress = 0;
            const reloadInterval = setInterval(() => {
                progress += 0.02;

                // 1단계: 포탈 열림 & 총기 기울임
                if (progress <= 0.25) {
                    const p = progress / 0.25;
                    portalGroup.scale.set(p, p, p);
                    portalRingMesh.rotation.z = p * Math.PI * 2;
                    weaponGroup.rotation.z = -0.25 * p;
                    magazineMesh.position.x = 0.15 * p; // 기존 탄창 제거 연출
                } 
                // 2단계: 포탈에서 새 탄창 등장
                else if (progress > 0.25 && progress <= 0.7) {
                    const p = (progress - 0.25) / 0.45;
                    portalRingMesh.rotation.z += 0.2;
                    magazineMesh.position.x = 0.25 * (1 - p);
                    magazineMesh.position.y = -0.2 * (1 - p);
                } 
                // 3단계: 포탈 닫힘 및 탄창 체결
                else if (progress > 0.7 && progress <= 1.0) {
                    const p = (progress - 0.7) / 0.3;
                    portalGroup.scale.set(1 - p, 1 - p, 1 - p);
                    weaponGroup.rotation.z = -0.25 * (1 - p);
                    magazineMesh.position.set(0, 0, 0);
                } else {
                    clearInterval(reloadInterval);
                    portalGroup.scale.set(0.001, 0.001, 0.001);
                    weaponGroup.rotation.z = 0;
                    magazineMesh.position.set(0, 0, 0);
                    
                    ammo = maxAmmo;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    document.getElementById('reloadMsg').innerText = "[R] 키를 눌러 차원 재장전!";
                    updateUI();
                }
            }, 18);
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
            document.getElementById('warningText').innerText = "⚠️ CYBER FLASH! (고개를 빠르게 피하세요!)";

            setTimeout(() => {
                document.getElementById('warningText').innerText = "";
                if (Math.abs(yaw % (Math.PI * 2)) < 0.8 && isGameStarted) {
                    const flashOverlay = document.getElementById('flashOverlay');
                    flashOverlay.style.opacity = '1';
                    setTimeout(() => {
                        flashOverlay.style.opacity = '0';
                    }, 1500);
                }
            }, 1200);
        }

        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                // WASD 이동 조작
                const moveVector = new THREE.Vector3(0, 0, 0);
                if (keys.w) moveVector.z -= 1;
                if (keys.s) moveVector.z += 1;
                if (keys.a) moveVector.x -= 1;
                if (keys.d) moveVector.x += 1;

                if (moveVector.lengthSq() > 0) {
                    moveVector.normalize();
                    moveVector.applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
                    camera.position.addScaledVector(moveVector, moveSpeed);

                    // 바운더리 제한
                    camera.position.x = Math.max(-12, Math.min(12, camera.position.x));
                    camera.position.z = Math.max(-8, Math.min(14, camera.position.z));

                    // 걷기 흔들림 (Head Bobbing)
                    walkTimer += 0.15;
                    weaponGroup.position.y = -0.22 + Math.sin(walkTimer) * 0.012;
                }

                // 시선 회전
                camera.rotation.order = 'YXZ';
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;

                // Gun Sway
                weaponGroup.position.x = 0.22 - mouseDeltaX * 0.0003;
                mouseDeltaX *= 0.85;
                mouseDeltaY *= 0.85;

                // 반동 회복
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
