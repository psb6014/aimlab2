import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Glock Edition", layout="centered")

st.title("🎯 3D Web AimLab (360° FPS & Reload)")
st.caption("화면을 클릭하여 마우스를 잠그고 360도로 화면을 돌려보세요! (탄약 10발 / 재장전: R 키)")

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
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 8px;
            height: 8px;
            background-color: #ff3333;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
            pointer-events: none;
            box-shadow: 0 0 6px #ff0000;
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

    <!-- Three.js 3D 엔진 및 PointerLockControls 로드 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="ui-panel">
        점수: <span id="score" style="color:#00d2ff">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">10</span> / 10 <span id="reloadMsg" style="font-size:16px; color:#ff3333; display:none;"><br>[R] 키를 눌러 재장전!</span>
    </div>
    <div id="crosshair"></div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #00d2ff; text-shadow: 0 0 10px rgba(0,210,255,0.5);">3D FPS AIMLAB (GLOCK)</h1>
        <p style="color: #aaa; margin-top: -10px;">마우스로 고개를 돌려 360도 주변을 둘러보세요.</p>
        <button class="start-btn" onclick="initGame()">게임 시작하기</button>
    </div>

    <script>
        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        let ammo = 10;
        let isReloading = false;
        let isGameStarted = false;

        // 마우스 시점 회전 관련 변수
        let isPointerLocked = false;
        let yaw = 0, pitch = 0;

        // 3D 글록 모델 그룹 및 반동
        let gunGroup;
        let recoilZ = 0;

        // 섬광탄 관련
        let flashPos = new THREE.Vector3(0, 2, -10);
        let flashActive = false;

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            isGameStarted = true;

            // 1. Three.js 기본 씬 & 카메라 설정
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

            // 격자 바닥 & 3D 공간 벽면
            const gridHelper = new THREE.GridHelper(60, 30, 0x00d2ff, 0x333344);
            gridHelper.position.y = 0;
            scene.add(gridHelper);

            // 2. 3D 글록(Glock) 권총 생성 및 카메라 고정
            create3DGlock();

            // 3. 타겟 구체 생성
            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            // 4. 마우스 이동 감지 (360도 화면 회전)
            renderer.domElement.addEventListener('click', () => {
                renderer.domElement.requestPointerLock();
            });

            document.addEventListener('pointerlockchange', () => {
                isPointerLocked = (document.pointerLockElement === renderer.domElement);
            });

            document.addEventListener('mousemove', (e) => {
                if (!isPointerLocked) return;
                yaw -= e.movementX * 0.0022;
                pitch -= e.movementY * 0.0022;
                pitch = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, pitch));

                camera.rotation.order = "YXZ";
                camera.rotation.y = yaw;
                camera.rotation.x = pitch;
            });

            // 5. 클릭(사격) 및 R키(재장전) 입력
            document.addEventListener('mousedown', (e) => {
                if (e.button === 0) shoot();
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'r' || e.key === 'R') reload();
            });

            // 6. 섬광탄 타이머 (10초 주기)
            setInterval(triggerFlash, 10000);

            animate();
        }

        // 3D 글록 권총 가공 및 조립
        function create3DGlock() {
            gunGroup = new THREE.Group();

            // 슬라이드 (상부)
            const slideGeo = new THREE.BoxGeometry(0.12, 0.12, 0.45);
            const slideMat = new THREE.MeshStandardMaterial({ color: 0x222225, roughness: 0.3 });
            const slide = new THREE.Mesh(slideGeo, slideMat);
            slide.position.set(0, 0, 0);
            gunGroup.add(slide);

            // 프레임/그립 (하부)
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

            // 카메라 하단 우측에 고정
            gunGroup.position.set(0.25, -0.22, -0.5);
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

            // 360도 공간 상 정면/측면에 무작위 생성
            target.position.x = (Math.random() - 0.5) * 16;
            target.position.y = Math.random() * 3 + 1;
            target.position.z = -Math.random() * 12 - 4;

            target.userData = {
                dx: (Math.random() - 0.5) * 0.04,
                dy: (Math.random() - 0.5) * 0.04
            };

            scene.add(target);
            targets.push(target);
        }

        // 사격 로직 (10발 제한)
        function shoot() {
            if (!isPointerLocked || isReloading) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            // 반동 효과
            recoilZ = 0.12;

            // 레이캐스트 사격 감지
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);

            const intersects = raycaster.intersectObjects(targets);

            if (intersects.length > 0) {
                const hitObj = intersects[0].object;
                scene.remove(hitObj);
                targets = targets.filter(t => t !== hitObj);
                
                score += 100;
                hits++;
                updateUI();
                createTarget(); // 타겟 재생성
            }

            if (ammo === 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
            }
        }

        // 재장전 로직
        function reload() {
            if (isReloading || ammo === 10) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            // 재장전 총기 애니메이션 (아래로 내렸다가 올림)
            let reloadTimer = 0;
            const reloadInterval = setInterval(() => {
                reloadTimer += 0.05;
                gunGroup.position.y = -0.22 - Math.sin(reloadTimer * Math.PI) * 0.2;

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
            accuracyEl = document.getElementById('accuracy').innerText = acc;
        }

        // 섬광탄 피하기 시스템
        function triggerFlash() {
            if (!isGameStarted) return;
            document.getElementById('warningText').innerText = "⚠️ FLASHBANG INCOMING! (고개를 돌려 피하세요!)";

            setTimeout(() => {
                detonateFlash();
            }, 1400);
        }

        function detonateFlash() {
            document.getElementById('warningText').innerText = "";

            // 플레이어 카메라 정면 방향과 섬광탄 방향 각도 비교
            const camDir = new THREE.Vector3();
            camera.getWorldDirection(camDir);

            const toFlash = flashPos.clone().sub(camera.position).normalize();
            const dot = camDir.dot(toFlash);

            // 정면(dot > 0.3)을 바라보고 있으면 눈뽕 적구
            if (dot > 0.3) {
                const flashOverlay = document.getElementById('flashOverlay');
                flashOverlay.style.opacity = '1';
                setTimeout(() => {
                    flashOverlay.style.opacity = '0';
                }, 1800);
            }
        }

        // 실시간 3D 렌더링 루프
        function animate() {
            requestAnimationFrame(animate);

            // 반동 회복
            if (recoilZ > 0) {
                recoilZ -= 0.015;
                if (recoilZ < 0) recoilZ = 0;
            }
            if (gunGroup) {
                gunGroup.position.z = -0.5 + recoilZ;
            }

            // 타겟 이동 애니메이션
            targets.forEach(t => {
                t.position.x += t.userData.dx;
                t.position.y += t.userData.dy;

                if (Math.abs(t.position.x) > 10) t.userData.dx *= -1;
                if (t.position.y < 0.8 || t.position.y > 4.5) t.userData.dy *= -1;
            });

            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

components.html(game_code, height=540)
