import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D AimLab - KAR98K Zoom & Closer Targets", layout="centered")

st.title("⚡ 3D AimLab (KAR98K Zoom 기능 적용)")
st.caption("과녁 배치가 가까워졌으며, KAR98K 선택 시 마우스 우클릭으로 줌인/줌아웃이 가능합니다.")

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
        <p style="color: #a0b0d0; margin-bottom: 15px; font-size: 14px;">마우스 이동: 시선/총기 조준 | <b>[F] 또는 좌클릭: 사격</b> | <b>[우클릭]: KAR98K Zoom</b> | [R]: 장전</p>

        <div class="section-title">GUN SELECT</div>
        <div class="btn-container">
            <button class="option-btn selected" onclick="selectWeapon('ak47', this)">REAL AK-47</button>
            <button class="option-btn" onclick="selectWeapon('kar98k', this)">REAL KAR98K</button>
            <button class="option-btn" onclick="selectWeapon('famas', this)">REAL FAMAS</button>
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
        let targetRadius = 0.48;

        let weaponGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        let targetYaw = 0, targetPitch = 0;
        let currentYaw = 0, currentPitch = 0;

        let isZoomed = false;
        const defaultFOV = 75;
        const zoomFOV = 30;

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

        function selectDiff(diff, btn) {
            btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (diff === 'easy') targetRadius = 0.65;
            else if (diff === 'normal') targetRadius = 0.48;
            else if (diff === 'hard') targetRadius = 0.32;
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
            isZoomed = false;
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

                camera = new THREE.PerspectiveCamera(defaultFOV, window.innerWidth / 500, 0.1, 5000);
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

                window.addEventListener('mousemove', (e) => {
                    if (!isGameStarted) return;
                    const rect = renderer.domElement.getBoundingClientRect();
                    const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    const mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

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
                    if (!isGameStarted) return;
                    if (e.button === 0) {
                        shoot();
                    } else if (e.button === 2) {
                        // KAR98K 전용 줌 기능
                        if (selectedWeapon === 'kar98k') {
                            isZoomed = !isZoomed;
                        }
                    }
                });

                animate();
            }

            camera.fov = defaultFOV;
            camera.updateProjectionMatrix();
            camera.position.set(0, 1.6, 5);

            if (weaponGroup) camera.remove(weaponGroup);
            buildWeaponModel(selectedWeapon);

            targets.forEach(t => scene.remove(t));
            targets = [];
            
            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            isGameStarted = true;
        }

        function goToMainMenu() {
            isGameStarted = false;
            isZoomed = false;
            if (camera) {
                camera.fov = defaultFOV;
                camera.updateProjectionMatrix();
            }
            document.getElementById('crosshair').style.display = 'none';
            document.getElementById('startOverlay').style.display = 'flex';
        }

        function buildWeaponModel(type) {
            weaponGroup = new THREE.Group();

            const steelMat = new THREE.MeshStandardMaterial({ color: 0x2e3440, roughness: 0.35, metalness: 0.85 });
            const darkSteelMat = new THREE.MeshStandardMaterial({ color: 0x1a1d24, roughness: 0.4, metalness: 0.9 });
            const woodMat = new THREE.MeshStandardMaterial({ color: 0x5c2c16, roughness: 0.65, metalness: 0.1 });
            const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x3d1c0e, roughness: 0.7, metalness: 0.05 });
            const neonCyanMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
            const famasPolymerMat = new THREE.MeshStandardMaterial({ color: 0x21252b, roughness: 0.5, metalness: 0.3 });

            if (type === 'ak47') {
                const receiver = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.085, 0.42), steelMat);
                weaponGroup.add(receiver);

                const topCover = new THREE.Mesh(new THREE.CylinderGeometry(0.033, 0.033, 0.4, 12), steelMat);
                topCover.rotation.x = Math.PI / 2;
                topCover.position.set(0, 0.045, -0.01);
                weaponGroup.add(topCover);

                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.11, 0.38), woodMat);
                stock.position.set(0, -0.03, 0.36);
                stock.rotation.x = -0.12;
                weaponGroup.add(stock);

                const handguard = new THREE.Mesh(new THREE.BoxGeometry(0.058, 0.07, 0.28), woodMat);
                handguard.position.set(0, 0.005, -0.32);
                weaponGroup.add(handguard);

                const grip = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.12, 0.055), woodMat);
                grip.position.set(0, -0.11, 0.12);
                grip.rotation.x = -0.38;
                weaponGroup.add(grip);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.65, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.015, -0.62);
                weaponGroup.add(barrel);

                const gasBlock = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.013, 0.32, 12), darkSteelMat);
                gasBlock.rotation.x = Math.PI / 2;
                gasBlock.position.set(0, 0.042, -0.42);
                weaponGroup.add(gasBlock);

                const sight = new THREE.Mesh(new THREE.BoxGeometry(0.015, 0.05, 0.02), steelMat);
                sight.position.set(0, 0.055, -0.88);
                weaponGroup.add(sight);

                magazineMesh = new THREE.Group();
                const magUpper = new THREE.Mesh(new THREE.BoxGeometry(0.042, 0.14, 0.08), darkSteelMat);
                magUpper.position.set(0, 0, 0);
                magUpper.rotation.x = -0.28;
                magazineMesh.add(magUpper);

                const magLower = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.14, 0.075), darkSteelMat);
                magLower.position.set(0, -0.1, -0.03);
                magLower.rotation.x = -0.55;
                magazineMesh.add(magLower);

                magazineMesh.position.set(0, -0.12, -0.05);
                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                const fullStock = new THREE.Mesh(new THREE.BoxGeometry(0.052, 0.072, 1.25), darkWoodMat);
                fullStock.position.set(0, -0.02, -0.22);
                weaponGroup.add(fullStock);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 1.15, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.02, -0.75);
                weaponGroup.add(barrel);

                const boltHandle = new THREE.Mesh(new THREE.SphereGeometry(0.022, 8, 8), darkSteelMat);
                boltHandle.position.set(0.05, 0.04, 0.05);
                weaponGroup.add(boltHandle);

                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.45, 16), darkSteelMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.088, -0.15);
                weaponGroup.add(scopeBody);

                const scopeLens = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.01, 16), neonCyanMat);
                scopeLens.rotation.x = Math.PI / 2;
                scopeLens.position.set(0, 0.088, -0.37);
                weaponGroup.add(scopeLens);

                magazineMesh = new THREE.Group();
                const dummyMag = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.06, 0.06), steelMat);
                magazineMesh.add(dummyMag);
                magazineMesh.position.set(0, -0.06, -0.12);
                weaponGroup.add(magazineMesh);

            } else if (type === 'famas') {
                const body = new THREE.Mesh(new THREE.BoxGeometry(0.068, 0.14, 0.72), famasPolymerMat);
                weaponGroup.add(body);

                const carryHandle = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.08, 0.58), famasPolymerMat);
                carryHandle.position.set(0, 0.11, -0.02);
                weaponGroup.add(carryHandle);

                const topRail = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.018, 0.52), steelMat);
                topRail.position.set(0, 0.155, -0.02);
                weaponGroup.add(topRail);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.45, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.55);
                weaponGroup.add(barrel);

                const flashHider = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.08, 12), darkSteelMat);
                flashHider.rotation.x = Math.PI / 2;
                flashHider.position.set(0, 0.01, -0.78);
                weaponGroup.add(flashHider);

                magazineMesh = new THREE.Group();
                const mag = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.18, 0.075), darkSteelMat);
                magazineMesh.add(mag);
                magazineMesh.position.set(0, -0.14, 0.22);
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

        function createTarget() {
            const targetGroup = new THREE.Group();

            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 256;
            const ctx = canvas.getContext('2d');

            ctx.fillStyle = '#1c2338';
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
                new THREE.MeshStandardMaterial({ color: 0x2b3552 }),
                new THREE.MeshStandardMaterial({ map: texture, roughness: 0.1 }),
                new THREE.MeshStandardMaterial({ color: 0x181e30 })
            ];

            const disc = new THREE.Mesh(discGeo, discMat);
            disc.rotation.x = Math.PI / 2;
            targetGroup.add(disc);

            targetGroup.position.x = (Math.random() - 0.5) * 10;
            targetGroup.position.y = Math.random() * 2.2 + 0.8;
            targetGroup.position.z = -Math.random() * 9 - 3; // 과녁 거리를 가깝게 조정 (-3 ~ -12 범위)

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

            recoilZ = 0.16;
            recoilRotX = 0.14;

            muzzleFlashMesh.material.opacity = 1.0;
            setTimeout(() => { muzzleFlashMesh.material.opacity = 0; }, 35);

            const raycaster = new THREE.Raycaster();
            raycaster.far = Infinity;
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
                // FOV 부드러운 전환 (줌인/줌아웃)
                const targetFOV = (selectedWeapon === 'kar98k' && isZoomed) ? zoomFOV : defaultFOV;
                if (Math.abs(camera.fov - targetFOV) > 0.1) {
                    camera.fov += (targetFOV - camera.fov) * 0.2;
                    camera.updateProjectionMatrix();
                }

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

                if (recoilZ > 0) recoilZ -= 0.02;
                if (recoilRotX > 0) recoilRotX -= 0.015;

                weaponGroup.position.z = -0.52 + Math.max(0, recoilZ);
                weaponGroup.rotation.x = Math.max(0, recoilRotX);
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
