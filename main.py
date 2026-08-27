from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# 1. 화면 및 기본 환경 설정
window.title = "Python AimLab Clone"
window.fps_counter.enabled = True
window.borderless = False

# 바닥 및 배경
ground = Entity(model='plane', scale=(100, 1, 100), color=color.gray, texture='white_cube')
Sky()

# 2. 난이도 및 점수 설정
DIFFICULTY = 'Medium'

if DIFFICULTY == 'Easy':
    TARGET_SCALE = 1.0
    TARGET_SPEED = 1.5
elif DIFFICULTY == 'Medium':
    TARGET_SCALE = 0.6
    TARGET_SPEED = 3.0
else:  # Hard
    TARGET_SCALE = 0.35
    TARGET_SPEED = 5.0

score = 0
score_text = Text(text=f"Score: {score} | Difficulty: {DIFFICULTY}", position=(-0.85, 0.45), scale=1.5, color=color.white)

# 3. 플레이어 설정
player = FirstPersonController(y=2, origin_y=-0.5)
player.cursor.color = color.red
mouse.locked = True  # 마우스를 화면 중앙에 고정

# 4. 글록(Glock) 권총 3D 모델링
gun = Entity(
    parent=camera,
    model='cube',
    color=color.dark_gray,
    scale=(0.15, 0.2, 0.7),
    position=(0.5, -0.3, 0.8)
)
gun_barrel = Entity(
    parent=gun,
    model='cube',
    color=color.black,
    scale=(0.8, 0.6, 1.2),
    position=(0, 0.2, 0.2)
)

# 5. 오디오 예외 처리 (파일이 없어도 에러 없이 실행되도록 설정)
try:
    gunshot_sound = Audio('laser_1', autoplay=False, false_option=False)
    hit_sound = Audio('pop', autoplay=False, false_option=False)
except:
    gunshot_sound = None
    hit_sound = None

# 6. 타겟 관리
targets = []

def create_target():
    x = random.uniform(-6, 6)
    y = random.uniform(1.5, 4.5)
    z = random.uniform(8, 12)
    
    target = Entity(
        model='sphere',
        color=color.azure,
        scale=TARGET_SCALE,
        position=(x, y, z),
        collider='sphere'
    )
    target.dir_x = random.choice([-1, 1]) * random.uniform(0.5, 1.0)
    target.dir_y = random.choice([-1, 1]) * random.uniform(0.5, 1.0)
    targets.append(target)

for _ in range(5):
    create_target()

# 7. 플래시(섬광탄) 회피 시스템
flash_warn = Text(text="FLASH BANG!", origin=(0, 0), scale=3, color=color.yellow, enabled=False)
flash_screen = Entity(parent=camera.ui, model='quad', color=color.white, scale=(2, 2), enabled=False)

flash_timer = 0
flash_active = False
flash_world_pos = Vec3(0, 0, 0)

def trigger_flash():
    global flash_active, flash_world_pos
    flash_active = True
    flash_warn.enabled = True
    flash_world_pos = player.position + player.forward * 10 + Vec3(0, 2, 0)
    invoke(detonate_flash, delay=1.5)

def detonate_flash():
    flash_warn.enabled = False
    
    cam_dir = camera.forward
    target_dir = (flash_world_pos - camera.world_position).normalized()
    dot_val = cam_dir.dot(target_dir)
    
    if dot_val > 0.4:
        flash_screen.enabled = True
        invoke(clear_flash, delay=2.0)
    else:
        global flash_active
        flash_active = False

def clear_flash():
    global flash_active
    flash_screen.enabled = False
    flash_active = False

# 8. 사격 처리
def input(key):
    global score
    if key == 'left mouse down':
        if gunshot_sound and gunshot_sound.clip:
            gunshot_sound.play()
        
        # 총 반동
        gun.animate_position((0.5, -0.3, 0.6), duration=0.04)
        gun.animate_position((0.5, -0.3, 0.8), delay=0.04, duration=0.08)
        
        # 사격 레이캐스트
        hit_info = raycast(camera.world_position, camera.forward, distance=50)
        
        if hit_info.hit and hit_info.entity in targets:
            if hit_sound and hit_sound.clip:
                hit_sound.play()
            
            hit_target = hit_info.entity
            targets.remove(hit_target)
            destroy(hit_target)
            
            score += 100
            score_text.text = f"Score: {score} | Difficulty: {DIFFICULTY}"
            create_target()

# 9. 실시간 프레임 업데이트
def update():
    global flash_timer
    
    # 타겟 이동
    for t in targets:
        t.x += t.dir_x * TARGET_SPEED * time.dt
        t.y += t.dir_y * TARGET_SPEED * time.dt
        
        if abs(t.x) > 7:
            t.dir_x *= -1
        if t.y < 1.0 or t.y > 5.5:
            t.dir_y *= -1

    # 섬광탄 주기
    if not flash_active:
        flash_timer += time.dt
        if flash_timer > 10:
            flash_timer = 0
            trigger_flash()

app.run()
