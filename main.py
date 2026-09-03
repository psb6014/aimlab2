import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D AimLab - Realistic Guns & Targets", layout="centered")

st.title("⚡ 3D AimLab (리얼 총기 & 이동 사람 타겟 & 원형 과녁)")
st.caption("마우스 커서를 따라다니는 십자선과 지속적으로 재생성되는 원형 과녁이 적용되었습니다.")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #0e111a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
            cursor: none;
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
            width: 12px;
            height: 12px;
            pointer-events: none;
            z-index: 20;
            display: none;
            transform: translate(-50%, -50%);
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
        <p style="color: #a0b0d0; margin-bottom: 15px; font-size: 14px;">마우스 이동: 조준 및 십자선 이동 | <b>좌클릭 또는 [F] 키: 사격</b> | [R]: 장전</p>

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
            try {
                const now = audioCtx.currentTime;
                const bufferSize = audioCtx.sampleRate * 0.2;
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
                filter.frequency.setValueAtTime(type === 'kar98k' ? 600 : (type === 'ak47' ? 1000 : 1300), now);
                filter.frequency.exponentialRampToValueAtTime(80, now + 0.2);
                gain.gain.setValueAtTime(1.2, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);

                noise.connect(filter);
                filter.connect(gain);
                gain.connect(audioCtx.destination);
                noise.start(now);
            } catch(e){}
        }

        function playReloadSound() {
            if (!audioCtx) return;
            try {
                const now = audioCtx.currentTime;
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(400, now);
                osc.frequency.linearRampToValueAtTime(150, now + 0.3);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.3);
            } catch(e){}
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

        let mouseNDC = new THREE.Vector2(0, 0);

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

                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
                camera.position.set(0, 1.6, 5);

                renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, 500);
                document.body.appendChild(renderer.domElement);

                const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(ambientLight);

                const dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
                dirLight.position.set(10, 20, 10);
                scene.add(dirLight);

                const floorGeo = new THREE.PlaneGeometry(200, 200);
                const floorMat = new THREE.MeshStandardMaterial({ color: 0x141824, roughness: 0.2 });
                const floor = new THREE.Mesh(floorGeo, floorMat);
                floor.rotation.x = -Math.PI / 2;
                scene.add(floor);

                const gridHelper = new THREE.GridHelper(200, 100, 0x00f0ff, 0x27334d);
                gridHelper.position.y = 0.01;
                scene.add(gridHelper);

                // 마우스 추적 및 조준 이벤트
                window.addEventListener('mousemove', (e) => {
                    if (!isGameStarted) return;
                    const rect = renderer.domElement.getBoundingClientRect();
                    
                    const crosshair = document.getElementById('crosshair');
                    crosshair.style.left = e.clientX + 'px';
                    crosshair.style.top = e.clientY + 'px';

                    const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    const mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                    mouseNDC.set(mouseX, mouseY);

                    targetYaw = -mouseX * 1.2;
                    targetPitch = mouseY * 0.6;
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

                renderer.domElement.addEventListener('mousedown', (e) => {
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
            
            // 사람 타겟 4명 생성
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

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.65, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.015, -0.62);
                weaponGroup.add(barrel);

                magazineMesh = new THREE.Group();
                const m1 = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.12, 0.07), darkSteelMat);
                m1.rotation.x = -0.35;
                magazineMesh.add(m1);
                magazineMesh.position.set(0, -0.1, -0.05);
                weaponGroup.add(magazineMesh);

            } else if (type === 'kar98k') {
                const stock = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.068, 1.25), darkWoodMat);
                stock.position.set(0, -0.02, -0.2);
                weaponGroup.add(stock);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.011, 1.1, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.022, -0.72);
                weaponGroup.add(barrel);

                const scopeBody = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.42, 16), darkSteelMat);
                scopeBody.rotation.x = Math.PI / 2;
                scopeBody.position.set(0, 0.09, -0.12);
                weaponGroup.add(scopeBody);

                magazineMesh = new THREE.Group();
                const dummy = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.04, 0.08), steelMat);
                magazineMesh.add(dummy);
                magazineMesh.position.set(0, -0.04, -0.08);
                weaponGroup.add(magazineMesh);

            } else if (type === 'famas') {
                const mainBody = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.12, 0.68), famasMat);
                weaponGroup.add(mainBody);

                const carryHandle = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.1, 0.52), famasMat);
                carryHandle.position.set(0, 0.1, -0.02);
                weaponGroup.add(carryHandle);

                const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.013, 0.45, 12), steelMat);
                barrel.rotation.x = Math.PI / 2;
                barrel.position.set(0, 0.01, -0.52);
                weaponGroup.add(barrel);

                magazineMesh = new THREE.Group();
                const mag = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.16, 0.07), darkSteelMat);
                magazineMesh.add(mag);
                magazineMesh.position.set(0, -0.12, 0.22);
                weaponGroup.add(magazineMesh);
            }

            const flashGeo = new THREE.OctahedronGeometry(0.1, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.position.set(0, 0.01, -0.9);
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
            const discGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.05, 32);
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
            discGroup.position.y = Math.random() * 3.0 + 0.8;
            discGroup.position.z = -Math.random() * 18 - 5;

            const targetObj = {
                type: 'disc',
                group: discGroup,
                hp: 1,
                speed: 0
            };

            scene.add(discGroup);
            targets.push(targetObj);
        }

        // 사람 마네킹 생성 함수
        function createHumanTarget() {
            const humanGroup = new THREE.Group();
            const skinMat = new THREE.MeshStandardMaterial({ color: 0x3a4b6e, roughness: 0.5 });
            const headMat = new THREE.MeshStandardMaterial({ color: 0xff0055, roughness: 0.3 });

            // 머리
            const headGeo = new THREE.SphereGeometry(0.2, 16, 16);
            const headMesh = new THREE.Mesh(headGeo, headMat);
            headMesh.position.y = 1.6;
            headMesh.userData = { type: 'head' };
            humanGroup.add(headMesh);

            // 몸통
            const bodyGeo = new THREE.BoxGeometry(0.48, 0.72, 0.26);
            const bodyMesh = new THREE.Mesh(bodyGeo, skinMat);
            bodyMesh.position.y = 1.0;
            bodyMesh.userData = { type: 'body' };
            humanGroup.add(bodyMesh);

            // 팔 & 다리
            const armGeo = new THREE.BoxGeometry(0.14, 0.6, 0.14);
            const leftArm = new THREE.Mesh(armGeo, skinMat);
            leftArm.position.set(-0.35, 1.0, 0);
            leftArm.userData = { type: 'body' };
            humanGroup.add(leftArm);

            const rightArm = new THREE.Mesh(armGeo, skinMat);
            rightArm.position.set(0.35, 1.0, 0);
            rightArm.userData = { type: 'body' };
            humanGroup.add(rightArm);

            const legGeo = new THREE.BoxGeometry(0.18, 0.65, 0.18);
            const leftLeg = new THREE.Mesh(legGeo, skinMat);
            leftLeg.position.set(-0.15, 0.32, 0);
            leftLeg.userData = { type: 'body' };
            humanGroup.add(leftLeg);

            const rightLeg = new THREE.Mesh(legGeo, skinMat);
            rightLeg.position.set(0.15, 0.32, 0);
            rightLeg.userData = { type: 'body' };
            humanGroup.add(rightLeg);

            const posX = (Math.random() - 0.5) * 14;
            const posZ = -Math.random() * 15 - 6;
            humanGroup.position.set(posX, 0, posZ);

            const targetObj = {
                type: 'human',
                group: humanGroup,
                hp: 4,
                speed: (Math.random() * 0.03 + 0.02) * (Math.random() > 0.5 ? 1 : -1),
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

            recoilZ = 0.14;
            recoilRotX = 0.12;

            if (muzzleFlashMesh) {
                muzzleFlashMesh.material.opacity = 1.0;
                setTimeout(() => { if (muzzleFlashMesh) muzzleFlashMesh.material.opacity = 0; }, 35);
            }

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouseNDC, camera);

            const intersects = raycaster.intersectObjects(scene.children, true);

            for (let i = 0; i < intersects.length; i++) {
                const hitMesh = intersects[i].object;
                
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
                        target.hp = 0;
                    } else if (target.type === 'human') {
                        if (hitMesh.userData && hitMesh.userData.type === 'head') {
                            target.hp -= 4;
                        } else {
                            target.hp -= 1;
                        }
                    }

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

            const initY = magazineMesh ? magazineMesh.position.y : 0;
            let progress = 0;

            const reloadInterval = setInterval(() => {
                progress += 0.05;

                if (magazineMesh) {
                    if (progress <= 0.4) {
                        magazineMesh.position.y = initY - (progress / 0.4) * 0.2;
                    } else if (progress <= 1.0) {
                        magazineMesh.position.y = initY;
                    }
                }

                if (progress >= 1.0) {
                    clearInterval(reloadInterval);
                    ammo = maxAmmo;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    updateUI();
                }
            }, 30);
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

                if (weaponGroup) {
                    weaponGroup.position.z = -0.52 + Math.max(0, recoilZ);
                    weaponGroup.rotation.x = Math.max(0, recoilRotX);
                }

                targets.forEach(t => {
                    if (t.type === 'human') {
                        t.group.position.x += t.speed;
                        if (t.group.position.x > t.maxX || t.group.position.x < t.minX) {
                            t.speed *= -1;
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

components.html(game_code, height=540)
