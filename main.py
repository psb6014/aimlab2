import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Fixed Edition", layout="centered")

st.title("⚡ 3D Cyberpunk AimLab (Performance Fixed)")
st.caption("화면 클릭 시 시선이 회전하며, 마우스 클릭 시 총알이 발사됩니다. (R: 포탈 장전 | E: 메인)")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #0b0d17;
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
<body>
    <div id="ui-panel">
        <button class="main-menu-btn" onclick="goToMainMenu()">🏠 메인으로 (E)</button>
        <div>점수: <span id="score" style="color:#00f0ff">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%</div>
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">30</span> / <span id="maxAmmo">30</span>
        <div id="reloadMsg">[R] 키를 눌러 차원 재장전!</div>
    </div>
    <div id="crosshair"></div>

    <div id="startOverlay">
        <h1 style="color: #00f0ff; text-shadow: 0 0 20px rgba(0,240,255,0.8); margin-bottom: 2px; font-size: 32px;">CYBERPUNK AIMLAB</h1>
        <p style="color: #a0b0d0; margin-bottom: 15px; font-size: 14px;">화면 클릭: 마우스 조작 시작 | 좌클릭: 사격 | R: 포탈 장전</p>

        <div class="section-title">GUN SELECT</div>
        <div class="btn-container">
            <button class="option-btn selected" onclick="selectWeapon('ak47', this)">CYBER AK-47</button>
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
            filter.frequency.setValueAtTime(type === 'kar98k' ? 800 : 1300, now);
            filter.frequency.exponentialRampToValueAtTime(100, now + 0.22);
            gain.gain.setValueAtTime(1.4, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.22);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start(now);
        }

        function playPortalReloadSound() {
            if (!audioCtx) return;
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(250, now);
            osc.frequency.exponentialRampToValueAtTime(1200, now + 0.5);
            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.55);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.55);
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
        let portalGroup, portalRingMesh;
        let recoilZ = 0, recoilRotX = 0;

        let yaw = 0, pitch = 0;
        const sensitivity = 0.0022;

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
            yaw = 0;
            pitch = 0;
            updateUI();
            document.getElementById('reloadMsg').style.display = 'none';

            if (!scene) {
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0e111a);
                scene.fog = new THREE.FogExp2(0x0e111a, 0.015);

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
                camera.position.set(0, 1.6, 5);

                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, 500);
                document.body.appendChild(renderer.domElement);

                // 💡 최적의 맵 조명
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                scene.add(ambientLight);

                const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
                dirLight.position.set(10, 20, 10);
                scene.add(dirLight);

                const cyanLight = new THREE.PointLight(0x00f0ff, 2.0, 30);
                cyanLight.position.set(0, 6, 0);
                scene.add(cyanLight);

                // 바닥 및 벽면
                const floorGeo = new THREE.PlaneGeometry(80, 80);
                const floorMat = new THREE.MeshStandardMaterial({ color: 0x141824, roughness: 0.2 });
                const floor = new THREE.Mesh(floorGeo, floorMat);
                floor.rotation.x = -Math.PI / 2;
                scene.add(floor);

                const gridHelper = new THREE.GridHelper(80, 40, 0x00f0ff, 0x27334d);
                gridHelper.position.y = 0.01;
                scene.add(gridHelper);

                // 마우스 시선 회전
                document.addEventListener('mousemove', (e) => {
                    if (document.pointerLockElement === renderer.domElement && isGameStarted) {
                        yaw -= (e.movementX || 0) * sensitivity;
                        pitch -= (e.movementY || 0) * sensitivity;
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
                            renderer.domElement.requestPointerLock();
                        } else {
                            shoot();
                        }
                    }
                });

                animate();
            }

            camera.position.set(0, 1.6, 5);
            try { renderer.domElement.requestPointerLock(); } catch(e){}

            if (weaponGroup) camera.remove(weaponGroup);
            buildWeaponModel(selectedWeapon);
            buildPortalModel();

            targets.forEach(t => scene.remove(t));
            targets = [];
            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            isGameStarted = true;
        }

        function goToMainMenu() {
            isGameStarted = false;
            if (document.pointerLockElement) {
                document.exitPointerLock();
            }
            document.getElementById('crosshair').style.display = 'none';
            document.getElementById('startOverlay').style.display = 'flex';
        }

        function buildPortalModel() {
            portalGroup = new THREE.Group();
            
            const ringGeo = new THREE.TorusGeometry(0.18, 0.025, 16, 32);
            const ringMat = new THREE.MeshBasicMaterial({ color: 0xa800ff, wireframe: true });
            portalRingMesh = new THREE.Mesh(ringGeo, ringMat);
            portalGroup.add(portalRingMesh);

            const coreGeo = new THREE.CircleGeometry(0.16, 32);
            const coreMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.8 });
            const core = new THREE.Mesh(coreGeo, coreMat);
            portalGroup.add(core);

            portalGroup.position.set(0.42, -0.05, -0.45);
            portalGroup.scale.set(0.001, 0.001, 0.001);
            
            weaponGroup.add(portalGroup);
        }

        // 🔫 디테일 총기 3종 복원
        function buildWeaponModel(type) {
            weaponGroup = new THREE.Group();

            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x222838, roughness: 0.3, metalness: 0.7 });
            const neonCyanMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
            const neonMagentaMat = new THREE.MeshBasicMaterial({ color: 0xff0055 });
            const magMat = new THREE.MeshStandardMaterial({ color: 0x333d54 });

            if (type === 'ak47') {
                const mainBody = new THREE.Mesh(new THREE.BoxGeometry(0.065, 0.09, 0.44), bodyMat);
                weaponGroup.add(mainBody);

                const stripe = new THREE.Mesh(new THREE.BoxGeometry(0.068, 0.018, 0.28), neonCyanMat);
                stripe.position.set(0, 0.02, -0.05);
                weaponGroup.add(stripe);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.75, 12), bodyMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.58);
                weaponGroup.add(barrel);

                const gasTube = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.35, 12), bodyMat);
                gasTube.rotation.x = Math.PI / 2;
                gasTube.position.set(0, 0.04, -0.42);
                weaponGroup.add(gasTube);

                const frontSight = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.06, 0.025), neonMagentaMat);
                frontSight.position.set(0, 0.06, -0.88);
                weaponGroup.add(frontSight);

                magazineMesh = new THREE.Group();
                const magTop = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.18, 0.085), magMat);
                magTop.position.set(0, -0.13, -0.02);
                magTop.rotation.x = -0.32;
                magazineMesh.add(magTop);

                const magNeon = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.02, 0.088), neonCyanMat);
                magNeon.position.set(0, -0.18, -0.04);
                magNeon.rotation.x = -0.32;
                magazineMesh.add(magNeon);

                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.075, 0.95), bodyMat);
                stock.position.set(0, -0.03, -0.1);
                weaponGroup.add(stock);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.1, 12), bodyMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.02, -0.65);
                weaponGroup.add(barrel);

                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.42, 16), bodyMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.085, -0.1);
                weaponGroup.add(scopeBody);

                const scopeGlow = new THREE.Mesh(new THREE.CylinderGeometry(0.023, 0.023, 0.02, 16), neonCyanMat);
                scopeGlow.rotation.x = Math.PI / 2;
                scopeGlow.position.set(0, 0.085, -0.3);
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

            targetGroup.position.x = (Math.random() - 0.5) * 14;
            targetGroup.position.y = Math.random() * 3.2 + 0.8;
            targetGroup.position.z = -Math.random() * 10 - 5;

            scene.add(targetGroup);
            targets.push(targetGroup);
        }

        // 💥 클릭 시 총알 발사 처리
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

            // 총알 수평 레이저 가시화 연출
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
        }

        function reload() {
            if (isReloading || ammo === maxAmmo || !isGameStarted) return;
            isReloading = true;
            playPortalReloadSound();

            let progress = 0;
            const reloadInterval = setInterval(() => {
                progress += 0.03;

                if (progress <= 0.3) {
                    const p = progress / 0.3;
                    portalGroup.scale.set(p, p, p);
                    portalRingMesh.rotation.z = p * Math.PI * 2;
                    magazineMesh.position.x = 0.15 * p;
                } else if (progress <= 0.7) {
                    portalRingMesh.rotation.z += 0.2;
                } else if (progress <= 1.0) {
                    const p = (progress - 0.7) / 0.3;
                    portalGroup.scale.set(1 - p, 1 - p, 1 - p);
                    magazineMesh.position.set(0, 0, 0);
                } else {
                    clearInterval(reloadInterval);
                    portalGroup.scale.set(0.001, 0.001, 0.001);
                    magazineMesh.position.set(0, 0, 0);
                    ammo = maxAmmo;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
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

        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                const moveVector = new THREE.Vector3(0, 0, 0);
                if (keys.w) moveVector.z -= 1;
                if (keys.s) moveVector.z += 1;
                if (keys.a) moveVector.x -= 1;
                if (keys.d) moveVector.x += 1;

                if (moveVector.lengthSq() > 0) {
                    moveVector.normalize();
                    moveVector.applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
                    camera.position.addScaledVector(moveVector, moveSpeed);

                    camera.position.x = Math.max(-12, Math.min(12, camera.position.x));
                    camera.position.z = Math.max(-8, Math.min(14, camera.position.z));
                }

                camera.rotation.order = 'YXZ';
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;

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
