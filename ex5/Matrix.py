import pygame
import sys

# --- 定数設定 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 50, 255)  # プレイヤー (青)
PLATFORM_COLOR = (100, 100, 100) # 足場 (灰色)
SPIKE_COLOR = (255, 50, 50)   # 障害物 (赤)
KEY_COLOR = (255, 215, 0) # カギ (黄)
DOOR_COLOR = (0, 200, 0)    # トビラ (緑)

# 物理定数
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# --- プレイヤークラス (修正版) ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False  # 最初は空中にいる
        self.has_key = False

    def update(self, platforms):
        # 左右の入力
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
        else:
            self.vel_x = 0

        # 重力 (on_groundフラグは「前のフレーム」の状態)
        if not self.on_ground:
            self.vel_y += GRAVITY
            if self.vel_y > 10: # 最大落下速度
                self.vel_y = 10

        # X軸（横）の移動
        self.rect.x += self.vel_x
        # （ここに「壁」との衝突判定を追加できる）

        # Y軸（縦）の移動と衝突判定
        self.rect.y += self.vel_y
        
        hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hit_list:
            if self.vel_y > 0: # 下に落ちている時 (着地)
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
            elif self.vel_y < 0: # 上にジャンプしている時 (頭をぶつけた)
                self.rect.top = platform.rect.bottom
                self.vel_y = 0

        # --- on_ground 判定 (ここが重要！) ---
        # Y軸の移動と衝突処理が「すべて終わった後」に、
        # 「本当に地面に立っているか」をチェックし直す。
        
        # 1ピクセルだけ下に動かしてみて、足場に触れるかチェック
        self.rect.y += 1
        ground_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1 # すぐに元の位置に戻す

        # 1ピクセル下に足場があれば「地上」、なければ「空中」
        if len(ground_hit_list) > 0:
            self.on_ground = True
        else:
            self.on_ground = False

        # 画面外に出ないように
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def jump(self):
        # on_ground が正しく判定されるようになったため、
        # 左右に移動しながらでもジャンプできる
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH

    def reset_position(self, x, y):
        """プレイヤーを初期位置に戻す"""
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.on_ground = False # リセット時も空中判定に
        self.has_key = False

# --- その他のオブジェクトクラス ---
class Platform(pygame.sprite.Sprite):
    """足場"""
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

class Spike(pygame.sprite.Sprite):
    """トゲ（障害物）"""
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(SPIKE_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

class Key(pygame.sprite.Sprite):
    """カギ"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(KEY_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

class Door(pygame.sprite.Sprite):
    """トビラ（ゴール）"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(DOOR_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- メインゲーム処理 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minimalism Prototype")
    clock = pygame.time.Clock()

    # --- レベルのセットアップ ---
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    
    start_pos = (50, 450)
    player = Player(*start_pos)

    # 足場を作成
    floor = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
    p1 = Platform(200, 450, 100, 20)
    p2 = Platform(400, 350, 150, 20)
    
    platforms.add(floor, p1, p2)
    
    # 障害物を作成
    spike1 = Spike(250, 430, 20, 20) # p1の上
    spikes.add(spike1)
    
    # アイテムとゴールを作成
    key = Key(450, 320) # p2の上
    door = Door(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 100) # 床の右端

    all_sprites.add(player, platforms, spikes, key, door)
    # --- レベルセットアップここまで ---

    while True:
        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.jump()

        # --- 更新処理 ---
        player.update(platforms)

        # トゲとの衝突判定
        if pygame.sprite.spritecollide(player, spikes, False):
            print("ミス！リスタートします。")
            player.reset_position(*start_pos)
            # カギもリセット (もし取得済みだったら)
            if not key in all_sprites:
                all_sprites.add(key)


        # カギとの衝突判定
        if pygame.sprite.collide_rect(player, key):
            player.has_key = True
            key.kill() # カギを消す
            print("カギを手に入れた！")

        # トビラとの衝突判定
        if pygame.sprite.collide_rect(player, door):
            if player.has_key:
                print("クリア！おめでとう！")
                # (次のレベルへ...の処理)
                pygame.quit()
                sys.exit()
            else:
                # print("カギがないと開かない...") # 毎フレーム表示されるのでコメントアウト
                pass

        # --- 描画処理 ---
        screen.fill(BLACK) # 画面を黒で塗りつぶす
        all_sprites.draw(screen) # 全てのスプライトを描画
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()