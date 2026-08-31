import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit 3D AimLab - Valorant Edition", layout="centered")

st.title("🎯 3D Web AimLab (Valorant Style Edition)")
st.caption("발로란트 스타일 라이플과 레전드 레드/화이트 과녁! (25발 탄창 / R키: 재장전)")

game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #0b0e14;
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
            color: #ff4655;
            font-size: 28px;
            font-weight: bold;
            z-index: 10;
            text-shadow: 0 0 10px rgba(255,70,85,0.5);
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
            background: rgba(11, 14, 20, 0.94);
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
            background: #1f232d;
            color: #ece8e1;
            border: 2px solid #363c4a;
            padding: 10px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.2s;
        }
        .diff-btn.selected {
            background: #ff4655;
            color: #fff;
            border-color: #ff4655;
            box-shadow: 0 0 15px rgba(255,70,85,0.6);
        }
        .start-btn {
            background: linear-gradient(135deg, #ff4655, #ff727d);
            color: white;
            border: none;
            padding: 14px 45px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 70, 85, 0.4);
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
        점수: <span id="score" style="color:#ff4655">0</span> | 명중률: <span id="accuracy" style="color:#00ff88">100</span>%
    </div>
    <div id="ammo-panel">
        AMMO: <span id="ammo">25</span> / 25 <span id="reloadMsg" style="font-size:16px; color:#ff4655; display:none;"><br>[R] 키를 눌러 재장전!</span>
    </div>
    <div id="warningText"></div>
    <div id="flashOverlay"></div>

    <div id="startOverlay">
        <h1 style="color: #ff4655; text-shadow: 0 0 12px rgba(255,70,85,0.6); margin-bottom: 5px; font-size: 36px;">VALORANT AIMLAB</h1>
        <p style="color: #8b929a; margin-bottom: 10px;">난이도를 선택하면 스피디한 레드/화이트 타겟이 등장합니다.</p>
        
        <div class="diff-container">
            <button class="diff-btn" onclick="selectDiff('easy', this)">EASY</button>
            <button class="diff-btn selected" onclick="selectDiff('normal', this)">NORMAL</button>
            <button class="diff-btn" onclick="selectDiff('hard', this)">HARD (FAST)</button>
        </div>

        <button class="start-btn" onclick="initGame()">게 임 시 작</button>
    </div>

    <script>
        let scene, camera, renderer;
        let targets = [];
        let score = 0, totalShots = 0, hits = 0;
        
        const MAX_AMMO = 25;
        let ammo = MAX_AMMO;
        let isReloading = false;
        let isGameStarted = false;

        // 난이도별속도 대폭 증가 (기존 대비 2.2배 이상)
        let currentDiff = 'normal';
        let targetSpeed = 0.08;
        let targetRadius = 0.5;

        let mouse = new THREE.Vector2();

        // 라이플 및 메인 파츠
        let rifleGroup, magazineMesh, muzzleFlashMesh;
        let recoilZ = 0, recoilRotX = 0;

        function selectDiff(diff, btn) {
            currentDiff = diff;
            document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            if (diff === 'easy') {
                targetSpeed = 0.045;
                targetRadius = 0.6;
            } else if (diff === 'normal') {
                targetSpeed = 0.085;
                targetRadius = 0.48;
            } else if (diff === 'hard') {
                targetSpeed = 0.14; // 초고속
                targetRadius = 0.35;
            }
        }

        function initGame() {
            document.getElementById('startOverlay').style.display = 'none';
            isGameStarted = true;

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0f1218);
            scene.fog = new THREE.FogExp2(0x0f1218, 0.015);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / 500, 0.1, 1000);
            camera.position.set(0, 1.6, 0);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, 500);
            document.body.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
            dirLight.position.set(5, 12, 7);
            scene.add(dirLight);

            // 네온 스타일 하단 그리드
            const gridHelper = new THREE.GridHelper(60, 30, 0xff4655, 0x222836);
            gridHelper.position.y = 0;
            scene.add(gridHelper);

            // 발로란트 스타일 소총 생성
            createValorantRifle();

            for (let i = 0; i < 5; i++) {
                createTarget();
            }

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

            setInterval(triggerFlash, 10000);

            animate();
        }

        // 발로란트 미래지향적 소총 모델링
        function createValorantRifle() {
            rifleGroup = new THREE.Group();

            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x1a1d24, roughness: 0.2, metalness: 0.8 });
            const accentMat = new THREE.MeshStandardMaterial({ color: 0xff4655, roughness: 0.3 }); // 핫핑크/레드 포인트
            const neonMat = new THREE.MeshBasicMaterial({ color: 0x00ffcc }); // 네온 그린 광원 포인트
            const glassMat = new THREE.MeshStandardMaterial({ color: 0x00ffff, transparent: true, opacity: 0.6 });

            // 1. 유선형 총몸 (Upper/Lower Receiver)
            const mainBodyGeo = new THREE.CylinderGeometry(0.06, 0.08, 0.55, 6);
            const mainBody = new THREE.Mesh(mainBodyGeo, bodyMat);
            mainBody.rotation.z = Math.PI / 2;
            rifleGroup.add(mainBody);

            // 2. 각진 프론트 섀시 (Chassis)
            const frontGeo = new THREE.ConeGeometry(0.07, 0.45, 5);
            const front = new THREE.Mesh(frontGeo, bodyMat);
            front.rotation.z = -Math.PI / 2;
            front.position.set(0, 0.01, -0.42);
            rifleGroup.add(front);

            // 3. 발광 레일 라인 (Neon Accent Strip)
            const stripGeo = new THREE.BoxGeometry(0.01, 0.02, 0.6);
            const strip = new THREE.Mesh(stripGeo, neonMat);
            strip.position.set(0, 0.07, -0.1);
            rifleGroup.add(strip);

            // 4. 세련된 개머리판 (SF Stock)
            const stockGeo = new THREE.BoxGeometry(0.05, 0.12, 0.35);
            const stock = new THREE.Mesh(stockGeo, accentMat);
            stock.position.set(0, -0.02, 0.4);
            stock.rotation.x = -0.15;
            rifleGroup.add(stock);

            // 5. 총구 (Muzzle Brake)
            const muzzleGeo = new THREE.CylinderGeometry(0.025, 0.025, 0.15, 8);
            const muzzle = new THREE.Mesh(muzzleGeo, bodyMat);
            muzzle.rotation.x = Math.PI / 2;
            muzzle.position.set(0, 0.01, -0.7);
            rifleGroup.add(muzzle);

            // 6. 조준경 (Dot Sight Scope)
            const scopeBase = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.06, 0.12), accentMat);
            scopeBase.position.set(0, 0.1, -0.1);
            rifleGroup.add(scopeBase);

            const scopeLens = new THREE.Mesh(new THREE.RingGeometry(0.01, 0.025, 16), glassMat);
            scopeLens.position.set(0, 0.11, -0.16);
            rifleGroup.add(scopeLens);

            // 7. 사선 곡형 탄창 (Mag)
            magazineMesh = new THREE.Group();
            const magBox = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.28, 0.1), bodyMat);
            magBox.position.set(0, -0.16, -0.05);
            magBox.rotation.x = -0.35;
            
            // 탄창 밑면 핑크 포인트
            const magBottom = new THREE.Mesh(new THREE.BoxGeometry(0.055, 0.04, 0.11), accentMat);
            magBottom.position.set(0, -0.28, -0.08);
            magBottom.rotation.x = -0.35;
            
            magazineMesh.add(magBox);
            magazineMesh.add(magBottom);
            rifleGroup.add(magazineMesh);

            // 8. 총구 화염
            const flashGeo = new THREE.OctahedronGeometry(0.09, 0);
            const flashMat = new THREE.MeshBasicMaterial({ color: 0xff3355, transparent: true, opacity: 0 });
            muzzleFlashMesh = new THREE.Mesh(flashGeo, flashMat);
            muzzleFlashMesh.position.set(0, 0.01, -0.8);
            rifleGroup.add(muzzleFlashMesh);

            rifleGroup.position.set(0.24, -0.24, -0.55);
            camera.add(rifleGroup);
            scene.add(camera);
        }

        // 빨간색 & 흰색 동심원 과녁 생성
        function createTarget() {
            const targetGroup = new THREE.Group();

            // 캔버스를 활용해 클래식 표적지 텍스처 생성 (레드&화이트 교차)
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
            
            // 전면 원형 과녁 판 (Flat Target Disc)
            const discGeo = new THREE.CylinderGeometry(targetRadius, targetRadius, 0.06, 32);
            const discMat = [
                new THREE.MeshStandardMaterial({ color: 0x333333 }), // 옆면
                new THREE.MeshStandardMaterial({ map: texture, roughness: 0.3 }), // 윗면 (과녁 텍스처)
                new THREE.MeshStandardMaterial({ color: 0x111111 })  // 뒷면
            ];

            const disc = new THREE.Mesh(discGeo, discMat);
            disc.rotation.x = Math.PI / 2; // 플레이어를 정면으로 바라봄
            targetGroup.add(disc);

            // 랜덤 위치배치
            targetGroup.position.x = (Math.random() - 0.5) * 11;
            targetGroup.position.y = Math.random() * 3.2 + 0.8;
            targetGroup.position.z = -Math.random() * 8 - 4;

            // 이동 속도 부여 (x, y축 고속 이동)
            targetGroup.userData = {
                dx: (Math.random() - 0.5) * targetSpeed * 2.5,
                dy: (Math.random() - 0.5) * targetSpeed * 2.5
            };

            scene.add(targetGroup);
            targets.push(targetGroup);
        }

        function shoot() {
            if (isReloading) return;

            if (ammo <= 0) {
                document.getElementById('reloadMsg').style.display = 'inline';
                return;
            }

            ammo--;
            totalShots++;
            updateUI();

            recoilZ = 0.16;
            recoilRotX = 0.14;

            muzzleFlashMesh.material.opacity = 1.0;
            setTimeout(() => {
                muzzleFlashMesh.material.opacity = 0;
            }, 35);

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, camera);

            // 그룹 형태의 과녁 감지
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
                document.getElementById('reloadMsg').style.display = 'inline';
            }
        }

        function reload() {
            if (isReloading || ammo === MAX_AMMO) return;
            isReloading = true;
            document.getElementById('reloadMsg').innerText = "재장전 중...";

            let step = 0;
            const reloadInterval = setInterval(() => {
                step += 0.04;

                if (step < 0.4) {
                    magazineMesh.position.y -= 0.035;
                    magazineMesh.position.z += 0.01;
                    rifleGroup.rotation.z = 0.25;
                } else if (step >= 0.4 && step < 0.5) {
                    magazineMesh.position.set(0, -0.5, -0.05);
                } else if (step >= 0.5 && step < 0.9) {
                    magazineMesh.position.y += 0.035;
                } else {
                    clearInterval(reloadInterval);
                    magazineMesh.position.set(0, 0, 0);
                    rifleGroup.rotation.z = 0;
                    ammo = MAX_AMMO;
                    isReloading = false;
                    document.getElementById('reloadMsg').style.display = 'none';
                    document.getElementById('reloadMsg').innerText = "[R] 키를 눌러 재장전!";
                    updateUI();
                }
            }, 25);
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
            }, 1200);
        }

        function animate() {
            requestAnimationFrame(animate);

            if (isGameStarted) {
                camera.rotation.y += (-mouse.x * 0.45 - camera.rotation.y) * 0.1;
                camera.rotation.x += (mouse.y * 0.28 - camera.rotation.x) * 0.1;

                rifleGroup.position.x = 0.24 + mouse.x * 0.04;
                rifleGroup.position.y = -0.24 + mouse.y * 0.04;

                if (recoilZ > 0) {
                    recoilZ -= 0.02;
                    if (recoilZ < 0) recoilZ = 0;
                }
                if (recoilRotX > 0) {
                    recoilRotX -= 0.015;
                    if (recoilRotX < 0) recoilRotX = 0;
                }

                rifleGroup.position.z = -0.55 + recoilZ;
                rifleGroup.rotation.x = recoilRotX;

                // 빠르게 다이나믹하게 이동하는 레드/화이트 표적지
                targets.forEach(t => {
                    t.position.x += t.userData.dx;
                    t.position.y += t.userData.dy;

                    // 미세 회전 효과 추가
                    t.rotation.z += 0.02;

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
