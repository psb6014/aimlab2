import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Cursor Follow Edition", layout="centered")

st.title("🎯 3D Web AimLab (Mouse Cursor Follow)")
st.caption("마우스 커서의 위치를 따라 글록 권총과 화면 시점이 부드럽게 움직입니다! (탄약 10발 / 재장전: R 키)")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #000;
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
            color: #00d2ff;
            font-size: 28px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 10px rgba(0,210,255,0.5);
            pointer-events: none;
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
            background: rgba(10, 10, 12, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 30;
            color: white;
        }
        .start-btn {
            background: linear-gradient(135deg, #007acc, #00d2ff);
            color: white;
            border: none;
            padding: 14px 40px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
            margin-top: 20px;
        }
    </style>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="ui-panel">
        점수: <span id="score" style="color:#00d2ff">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">10</span> / 10 <span id="reloadMsg" style="font-size:16px; color:#ff3333; display:none;"><br>[R] 키를 눌러 재장전!</span>
    </div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #00d2ff; text-shadow: 0 0 10px rgba(0,210,255,0.5);">GLOCK AIMLAB (CURSOR AIM)</h1>
        <p style="color: #aaa; margin-top: -10px;">마우스 커서를 움직이면 총과 시점이 커서를 따라 움직입니다.</p>
        <button class="start-btn" onclick="initGame()">게임 시작하기</button>
    </div>

    <script>
        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        let ammo = 10;
        let isReloading = false;
        let isGameStarted = false;

        // 마우스 규격화 좌표 (-1 ~ +1)
        let mouse = new THREE.Vector2();
        let targetCameraRotation = new THREE.Euler();

        // 3D 글록 모델 및 반동
        let gunGroup;
        let recoilZ = 0;

        // 섬광탄 위치
        let flashPos = new THREE.Vector3(0, 2, -10);

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            isGameStarted = true;

            // 1. 씬 및 카메라 세팅
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x141419);
            scene.fog = new THREE.FogExp2(0x141419, 0.015);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
            camera.position.set(0, 1.6, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, 500);
            document.body.appendChild(renderer.domElement);

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(5, 10, 7);
            scene.add(dirLight);

            // 격자 바닥
            const gridHelper = new THREE.GridHelper(60, 30, 0x00d2ff, 0x333344);
            gridHelper.position.y = 0;
            scene.add(gridHelper);

            // 2. 3D 글록 권총 추가
            create3DGlock();

            // 3. 타겟 5개 생성
            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            // 4. 마우스 이동에 따라 좌표 추적 (-1 ~ +1)
            window.addEventListener('mousemove', (e) => {
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            });

            // 5. 클릭 사격 & R키 재장전
            window.addEventListener('mousedown', (e) => {
                if (e.button === 0 && isGameStarted) shoot();
            });

            window.addEventListener('keydown', (e) => {
                if (e.key === 'r' || e.key === 'R') reload();
            });

            // 섬광탄 타이머
            setInterval(triggerFlash, 10000);

            animate();
        }

        function create3DGlock() {
            gunGroup = new THREE.Group();

            // 슬라이드
            const slideGeo = new THREE.BoxGeometry(0.12, 0.12, 0.45);
            const slideMat = new THREE.MeshStandardMaterial({ color: 0x222225, roughness: 0.3 });
            const slide = new THREE.Mesh(slideGeo, slideMat);
            slide.position.set(0, 0, 0);
            gunGroup.add(slide);

            // 프레임 및 그립
            const gripGeo = new THREE.BoxGeometry(0.1, 0.28, 0.15);
            const gripMat = new THREE.MeshStandardMaterial({ color: 0x111113, roughness: 0.8 });
            const grip = new THREE.Mesh(gripGeo, gripMat);
            grip.position.set(0, -0.15, 0.1);
            grip.rotation.x = 0.2;
            gunGroup.add(grip);

            // 야광 가늠쇠
            const sightGeo = new THREE.BoxGeometry(0.015, 0.02, 0.015);
            const sightMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
            const sight = new THREE.Mesh(sightGeo, sightMat);
            sight.position.set(0, 0.07, -0.2);
            gunGroup.add(sight);

            // 카메라 앞쪽에 배치
            gunGroup.position.set(0.2, -0.2, -0.5);
            camera.add(gunGroup);
            scene.add(camera);
        }

        function createTarget() {
            const radius = 0.5;
            const geo = new THREE.SphereGeometry(radius, 32, 32);
            const mat = new THREE.MeshStandardMaterial({
                color: 0x00a8ff,
                emissive: 0x004488,
                roughness: 0.2
            });
            const target = new THREE.Mesh(geo, mat);

            target.position.x = (Math.random() - 0.5) * 12;
            target.position.y = Math.random() * 3 + 1;
            target.position.z = -Math.random() * 8 - 4;

            target.userData = {
                dx: (Math.random() - 0.5) * 0.03,
                dy: (Math.random() - 0.5) * 0.03
            };

            scene.add(target);
            targets.push(target);
        }

        // 마우스 커서 위치 기반 레이캐스트 사격
        function shoot() {
            if (isReloading) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            recoilZ = 0.12; // 반동

            const raycaster = new THREE.Raycaster();
            // 화면 상의 마우스 커서 지점으로 광선을 쏨
            raycaster.setFromCamera(mouse, camera);

            const intersects = raycaster.intersectObjects(targets);

            if (intersects.length > 0) {
                const hitObj = intersects[0].object;
                scene.remove(hitObj);
                targets = targets.filter(t => t !== hitObj);
                
                score += 100;
                hits++;
                updateUI();
                createTarget();
            }

            if (ammo === 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
            }
        }

        function reload() {
            if (isReloading || ammo === 10) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            let reloadTimer = 0;
            const reloadInterval = setInterval(() => {
                reloadTimer += 0.05;
                gunGroup.position.y = -0.2 - Math.sin(reloadTimer * Math.PI) * 0.2;

                if (reloadTimer >= 1.0) {
                    clearInterval(reloadInterval);
                    ammo = 10;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    document.getElementById('reloadMsg').innerText = "[R] 키를 눌러 재장전!";
                    updateUI();
                }
            }, 50);
        }

        function updateUI() {
            document.getElementById('score').innerText = score;
            document.getElementById('ammo').innerText = ammo;
            const acc = totalShots > 0 ? ((hits / totalShots) * 100).toFixed(1) : 100;
            document.getElementById('accuracy').innerText = acc;
        }

        function triggerFlash() {
            if (!isGameStarted) return;
            document.getElementById('warningText').innerText = "⚠️ FLASHBANG INCOMING! (마우스를 구석으로 피하세요!)";

            setTimeout(() => {
                detonateFlash();
            }, 1400);
        }

        function detonateFlash() {
            document.getElementById('warningText').innerText = "";

            // 마우스 커서가 화면 중앙 부근(mouse.x, mouse.y가 0 근처)에 있으면 눈뽕 적용
            if (Math.hypot(mouse.x, mouse.y) < 0.7) {
                const flashOverlay = document.getElementById('flashOverlay');
                flashOverlay.style.opacity = '1';
                setTimeout(() => {
                    flashOverlay.style.opacity = '0';
                }, 1800);
            }
        }

        // 프레임 루프
        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                // 1. 마우스 커서 위치에 따라 시점 및 총 위치 부드럽게 추종 (Lerp 적용)
                camera.rotation.y += (-mouse.x * 0.5 - camera.rotation.y) * 0.1;
                camera.rotation.x += (mouse.y * 0.3 - camera.rotation.x) * 0.1;

                // 2. 권총 위치 미세 관성 회전
                gunGroup.position.x = 0.2 + mouse.x * 0.05;
                gunGroup.position.y = -0.2 + mouse.y * 0.05;

                // 3. 반동 복귀
                if (recoilZ > 0) {
                    recoilZ -= 0.015;
                    if (recoilZ < 0) recoilZ = 0;
                }
                gunGroup.position.z = -0.5 + recoilZ;

                // 4. 타겟 애니메이션
                targets.forEach(t => {
                    t.position.x += t.userData.dx;
                    t.position.y += t.userData.dy;

                    if (Math.abs(t.position.x) > 8) t.userData.dx *= -1;
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
