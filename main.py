import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - AK47 Edition", layout="centered")

st.title("🎯 3D Web AimLab (AK-47 Edition)")
st.caption("난이도를 선택하고 AK-47으로 에임을 연습해보세요! (25발 탄창 / R키: 재장전)")

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
            color: #ff9900;
            font-size: 28px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 10px rgba(255,153,0,0.5);
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
            background: rgba(10, 10, 12, 0.92);
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
            background: #222;
            color: #ccc;
            border: 2px solid #444;
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: 0.2s;
        }
        .diff-btn.selected {
            background: #ff9900;
            color: #000;
            border-color: #ffaa00;
            box-shadow: 0 0 12px rgba(255,153,0,0.6);
        }
        .start-btn {
            background: linear-gradient(135deg, #ff8800, #ff5500);
            color: white;
            border: none;
            padding: 14px 45px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 85, 0, 0.4);
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
        점수: <span id="score" style="color:#ff9900">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">25</span> / 25 <span id="reloadMsg" style="font-size:16px; color:#ff3333; display:none;"><br>[R] 키를 눌러 재장전!</span>
    </div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #ff9900; text-shadow: 0 0 10px rgba(255,153,0,0.5); margin-bottom: 5px;">AK-47 AIMLAB</h1>
        <p style="color: #aaa; margin-bottom: 10px;">난이도를 선택하고 게임을 시작하세요.</p>
        
        <div class="diff-container">
            <button class="diff-btn" onclick="selectDiff('easy', this)">EASY</button>
            <button class="diff-btn selected" onclick="selectDiff('normal', this)">NORMAL</button>
            <button class="diff-btn" onclick="selectDiff('hard', this)">HARD</button>
        </div>

        <button class="start-btn" onclick="initGame()">게임 시작하기</button>
    </div>

    <script>
        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        
        // 탄약 25발 설정
        const MAX_AMMO = 25;
        let ammo = MAX_AMMO;
        let isReloading = false;
        let isGameStarted = false;

        // 난이도 옵션
        let currentDiff = 'normal';
        let targetSpeed = 0.03;
        let targetRadius = 0.5;

        // 마우스 및 시점
        let mouse = new THREE.Vector2();

        // 3D AK-47 파츠
        let akGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        function selectDiff(diff, btn) {
            currentDiff = diff;
            document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (diff === 'easy') {
                targetSpeed = 0.015;
                targetRadius = 0.65;
            } else if (diff === 'normal') {
                targetSpeed = 0.035;
                targetRadius = 0.5;
            } else if (diff === 'hard') {
                targetSpeed = 0.065;
                targetRadius = 0.35;
            }
        }

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            isGameStarted = true;

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x121215);
            scene.fog = new THREE.FogExp2(0x121215, 0.015);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
            camera.position.set(0, 1.6, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, 500);
            document.body.appendChild(renderer.domElement);

            // 조명
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
            dirLight.position.set(5, 12, 7);
            scene.add(dirLight);

            // 바닥 그리드
            const gridHelper = new THREE.GridHelper(60, 30, 0xff9900, 0x333344);
            gridHelper.position.y = 0;
            scene.add(gridHelper);

            // 3D AK-47 조합
            create3DAK47();

            // 타겟 5개 생성
            for (let i = 0; i < 5; i++) {
                createTarget();
            }

            // 이벤트 리스너
            window.addEventListener('mousemove', (e) => {
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            });

            window.addEventListener('mousedown', (e) => {
                if (e.button === 0 && isGameStarted) shoot();
            });

            window.addEventListener('keydown', (e) => {
                if (e.key === 'r' || e.key === 'R') reload();
            });

            setInterval(triggerFlash, 11000);

            animate();
        }

        // AK-47 3D 모델 가공
        function create3DAK47() {
            akGroup = new THREE.Group();

            const woodMat = new THREE.MeshStandardMaterial({ color: 0x8B4513, roughness: 0.6 }); // 개머리판/총열덮개
            const metalMat = new THREE.MeshStandardMaterial({ color: 0x222225, roughness: 0.3 }); // 메탈 몸통
            const magMat = new THREE.MeshStandardMaterial({ color: 0xaa5511, roughness: 0.5 }); // AK 특유의 오렌지/브라운 탄창

            // 1. 리시버 (몸통)
            const bodyGeo = new THREE.BoxGeometry(0.1, 0.14, 0.6);
            const body = new THREE.Mesh(bodyGeo, metalMat);
            akGroup.add(body);

            // 2. 총열 (Barrel)
            const barrelGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.7, 16);
            const barrel = new THREE.Mesh(barrelGeo, metalMat);
            barrel.rotation.x = Math.PI / 2;
            barrel.position.set(0, 0.02, -0.6);
            akGroup.add(barrel);

            // 3. 우드 핸드가드 (총열 덮개)
            const handguardGeo = new THREE.BoxGeometry(0.09, 0.1, 0.35);
            const handguard = new THREE.Mesh(handguardGeo, woodMat);
            handguard.position.set(0, -0.01, -0.4);
            akGroup.add(handguard);

            // 4. 개머리판 (Stock)
            const stockGeo = new THREE.BoxGeometry(0.08, 0.16, 0.4);
            const stock = new THREE.Mesh(stockGeo, woodMat);
            stock.position.set(0, -0.04, 0.45);
            stock.rotation.x = -0.1;
            akGroup.add(stock);

            // 5. 권총 손잡이 (Grip)
            const gripGeo = new THREE.BoxGeometry(0.07, 0.2, 0.08);
            const grip = new THREE.Mesh(gripGeo, woodMat);
            grip.position.set(0, -0.15, 0.15);
            grip.rotation.x = 0.3;
            akGroup.add(grip);

            // 6. 곡형 탄창 (Magazine) - 독립 객체로 생성해 재장전 애니메이션 적용
            magazineMesh = new THREE.Group();
            const magBox = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.3, 0.12), magMat);
            magBox.position.set(0, -0.15, -0.1);
            magBox.rotation.x = -0.25; // AK 곡형 각도
            magazineMesh.add(magBox);
            akGroup.add(magazineMesh);

            // 7. 총구 화염 (Muzzle Flash)
            const flashGeo = new THREE.ConeGeometry(0.08, 0.25, 8);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.rotation.x = -Math.PI / 2;
            muzzleFlashMesh.position.set(0, 0.02, -0.98);
            akGroup.add(muzzleFlashMesh);

            // 카메라 하단에 고정
            akGroup.position.set(0.22, -0.25, -0.55);
            camera.add(akGroup);
            scene.add(camera);
        }

        function createTarget() {
            const geo = new THREE.SphereGeometry(targetRadius, 32, 32);
            const mat = new THREE.MeshStandardMaterial({
                color: 0xff9900,
                emissive: 0x662200,
                roughness: 0.2
            });
            const target = new THREE.Mesh(geo, mat);

            target.position.x = (Math.random() - 0.5) * 12;
            target.position.y = Math.random() * 3 + 1;
            target.position.z = -Math.random() * 8 - 4;

            target.userData = {
                dx: (Math.random() - 0.5) * targetSpeed * 2,
                dy: (Math.random() - 0.5) * targetSpeed * 2
            };

            scene.add(target);
            targets.push(target);
        }

        // 사격 기능
        function shoot() {
            if (isReloading) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            // AK-47 묵직한 반동 및 총구 화염 효과
            recoilZ = 0.18;
            recoilRotX = 0.12;

            muzzleFlashMesh.material.opacity = 0.9;
            setTimeout(() => {
                muzzleFlashMesh.material.opacity = 0;
            }, 40);

            // 레이캐스팅
            const raycaster = new THREE.Raycaster();
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

        // 탄창 탈부착 재장전 애니메이션
        function reload() {
            if (isReloading || ammo === MAX_AMMO) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            let step = 0;
            const reloadInterval = setInterval(() => {
                step += 0.04;

                // 1단계: 탄창이 아래로 빠짐 (Drop)
                if (step < 0.4) {
                    magazineMesh.position.y -= 0.03;
                    magazineMesh.position.z += 0.01;
                    akGroup.rotation.z = 0.2; // 총을 약간 기울임
                } 
                // 2단계: 새 탄창 준비 (Reset pos)
                else if (step >= 0.4 && step < 0.5) {
                    magazineMesh.position.set(0, -0.5, -0.1);
                } 
                // 3단계: 새 탄창 결합 (Insert)
                else if (step >= 0.5 && step < 0.9) {
                    magazineMesh.position.y += 0.03;
                } 
                // 4단계: 완료
                else {
                    clearInterval(reloadInterval);
                    magazineMesh.position.set(0, 0, 0);
                    akGroup.rotation.z = 0;
                    ammo = MAX_AMMO;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    document.getElementById('reloadMsg').innerText = "[R] 키를 눌러 재장전!";
                    updateUI();
                }
            }, 30);
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
                if (Math.hypot(mouse.x, mouse.y) < 0.65) {
                    const flashOverlay = document.getElementById('flashOverlay');
                    flashOverlay.style.opacity = '1';
                    setTimeout(() => {
                        flashOverlay.style.opacity = '0';
                    }, 1800);
                }
            }, 1300);
        }

        // 메인 프레임 렌더링 루프
        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                // 커서 추종 부드러운 시점 회전
                camera.rotation.y += (-mouse.x * 0.45 - camera.rotation.y) * 0.1;
                camera.rotation.x += (mouse.y * 0.28 - camera.rotation.x) * 0.1;

                // 총기 위치 관성 이동
                akGroup.position.x = 0.22 + mouse.x * 0.04;
                akGroup.position.y = -0.25 + mouse.y * 0.04;

                // 반동 복귀 애니메이션
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

                // 난이도별 타겟 움직임
                targets.forEach(t => {
                    t.position.x += t.userData.dx;
                    t.position.y += t.userData.dy;

                    if (Math.abs(t.position.x) > 7.5) t.userData.dx *= -1;
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
