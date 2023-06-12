import sys
import random
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()
start_screen_sound = pygame.mixer.Sound("start_screen_sound.mp3")
background_music = pygame.mixer.Sound("background_music.mp3")
destroyed =pygame.mixer.Sound("destroyed.wav")
shoot_bullet_sound = pygame.mixer.Sound("shoot_bullet_sound.mp3")
game_over_sound = pygame.mixer.Sound("game_over.mp3")
hit_sound = pygame.mixer.Sound("hit.wav")
# Game objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = None
        self.rect = None
        self.speed = 15
        self.health = 3
        self.bullet_damage = 2
        self.bullet_cooldown = 0.5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed
            if score % 50 == 0 and score > 0:
                self.bullet_cooldown *= 0.9
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = None
        self.rect = pygame.Rect(x, y, 80, 60)
        self.speed = 0.5
        self.health = health

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            global score
            score -= 10
            self.kill()
        # if self.health > max_enemy_health:
        #     # print("enemy.health:" + str(enemy.health) + "max_enemy_health:" + str(max_enemy_health))            # max_enemy_health = enemy.health
        #     max_enemy_health = self.health
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_image
        self.rect = pygame.Rect(x, y, 30, 20)
        self.rect.center = (x, y)
        self.speedy = -10
        self.damage = damage

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0))  # Yellow color for the particles
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.lifespan = 30  # Number of frames the particle will be alive

    def update(self):
        self.rect.move_ip(self.vel)  # Update particle position
        self.lifespan -= 1  # Decrease lifespan

        if self.lifespan <= 0:
            self.kill()  # Remove particle if its lifespan is over

class Explosion2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)  # Create a surface with transparency
        self.radius = 10  # Radius of the circle
        self.gradient_color = (255, 0, 0)  # Gradient color (red)
        self.create_gradient()
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, 3))
        self.lifespan = 30  # Number of frames the particle will be alive

    def create_gradient(self):
        alpha = 255
        for i in range(self.radius):
            pygame.draw.circle(self.image, (self.gradient_color[0], self.gradient_color[1], self.gradient_color[2], alpha), (self.radius, self.radius), self.radius - i)
            alpha -= 10  # Decrease alpha for each concentric circle

    def update(self):
        self.rect.move_ip(self.vel)  # Update particle position
        self.lifespan -= 1  # Decrease lifespan

        if self.lifespan <= 0:
            self.kill()  # Remove particle if its lifespan is over




# Variables
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosion_particles = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

score = 0
timer = 0
enemy_spawn_ratio = 2.0  # Initial enemy spawn ratio
health_increase_interval = 2  # Increase enemy health every 10 seconds
health_increase_amount = 1  # Health increase amount for enemies
spawn_rate_increase_interval = 30  # Increase spawn rate every 30 seconds
spawn_rate_increase_ratio = 0.15  # 15% increase in spawn rate
bullet_damage_increase_kills = 10  # Increase bullet damage every 10 kills
bullet_damage_increase_ratio = 0.05  # 5% increase in bullet damage
enemy_killed_count = 0
bullet_cooldown_decrease_points = 1  # Decrease bullet cooldown every 100 points
bullet_cooldown_decrease_ratio = 0.1  # 15% decrease in bullet cooldown
max_enemy_health = 2
def load_graphics():
    global enemy_image, player_image, bullet_image

    enemy_image = pygame.image.load("enemy.png").convert()
    enemy_image.set_colorkey((255, 255, 255))
    enemy_image = pygame.transform.scale(enemy_image, (30, 30))

    player_image = pygame.image.load("player.png").convert()
    player_image.set_colorkey((255, 255, 255))
    player_image = pygame.transform.scale(player_image, (40, 50))

    bullet_image = pygame.image.load("bullet.png").convert()
    bullet_image.set_colorkey((255, 255, 255))
    bullet_image = pygame.transform.scale(bullet_image, (5, 20))

    return enemy_image, player_image, bullet_image
    # return enemy_image, player_image, bullet_image

def update_game_state():
    global score, timer, enemy_killed_count

    all_sprites.update()

    explosion_particles.update()

    # Check for collisions between bullets and enemies
    collisions = pygame.sprite.groupcollide(bullets, enemies, True, False)
    for bullet, hit_enemies in collisions.items():
        for enemy in hit_enemies:
            enemy.health -= bullet.damage
            if enemy.health <= 0:
                destroyed.play()
                enemy.kill()
                score += 1
                enemy_killed_count += 1
                if enemy_killed_count % 10 == 0:
                    increase_bullet_damage()
                create_explosion(enemy.rect.centerx, enemy.rect.centery)  # Create explosion at enemy position

    # Check for collisions between player and enemies
    collisions = pygame.sprite.spritecollide(player, enemies, True)
    if collisions:
        player.health -= 1  # Reduce player health on collision
        hit_sound.play()
        if player.health <= 0:
            game_over()
    for enemy in collisions:
        create_explosion2(player.rect.centerx, player.rect.centery)  # Create explosion at player position

    # Update the timer
    timer += 1
    if timer % (60 * health_increase_interval) == 0:
        increase_enemy_health()
        print("increase_enemy_health")

    # Decrease bullet cooldown based on score
    if score % bullet_cooldown_decrease_points == 0 and score > 0 and player.bullet_cooldown > 0:
        player.bullet_cooldown -= player.bullet_cooldown * bullet_cooldown_decrease_ratio

    player.bullet_cooldown -=0.02  # Decrease the bullet cooldown by 0.02 each frame
    if player.bullet_cooldown < 0:
        player.bullet_cooldown = 0  # Ensure the bullet cooldown doesn't go below 0

def create_explosion2(x, y):
    num_particles = 20  # Number of particles in the explosion
    for _ in range(num_particles):
        particle = Explosion2(x, y)
        explosion_particles.add(particle)
        all_sprites.add(particle)

def handle_input():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pause_game()

    keys = pygame.key.get_pressed()
    if keys[K_SPACE]:
        shoot_bullet()

def shoot_bullet():
    if player.bullet_cooldown <= 0:
        bullet = Bullet(player.rect.centerx, player.rect.top, player.bullet_damage)
        bullets.add(bullet)
        all_sprites.add(bullet)
        # Reset the bullet cooldown
        player.bullet_cooldown = 0.2
        shoot_bullet_sound.play()

def pause_game():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = False

        # Display "Paused" message
        pygame.display.update()

def increase_enemy_health():
    for enemy in enemies:
        enemy.health += health_increase_amount

def create_explosion(x, y):
    num_particles = 20  # Number of particles in the explosion
    for _ in range(num_particles):
        particle = Explosion(x, y)
        explosion_particles.add(particle)
        all_sprites.add(particle)

def spawn_enemies():
    global enemy_image, enemy_spawn_ratio, max_enemy_health

    if timer % (60 * spawn_rate_increase_interval) == 0:
        enemy_spawn_ratio += enemy_spawn_ratio * spawn_rate_increase_ratio

    if enemy_spawn_ratio == 0:
        enemy_spawn_ratio = 0.01  # Set a small positive value

    if timer % (60 // enemy_spawn_ratio) == 0:
        if enemy_image is not None:
            num_enemies = 1
            for _ in range(num_enemies):
                x = random.randint(0, screen_width - enemy_image.get_width())
                y = 2
                enemy = Enemy(x, y, max_enemy_health)
                enemy.image = enemy_image
                enemy.rect = enemy.image.get_rect()
                enemy.rect.topleft = (x, y)
                enemies.add(enemy)
                all_sprites.add(enemy)
                # Update max_enemy_health if the spawned enemy has higher health
                if enemy.health > max_enemy_health:
                    print("enemy.health:" + str(enemy.health) + "max_enemy_health:" + str(max_enemy_health))
                    max_enemy_health = enemy.health
def increase_bullet_damage():
    player.bullet_damage += player.bullet_damage * bullet_damage_increase_ratio

def render_graphics():
    screen.fill((0, 0, 0))

    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)

    screen.blit(player.image, player.rect)

    for bullet in bullets:
        screen.blit(bullet.image, bullet.rect)

    for particle in explosion_particles:
        screen.blit(particle.image, particle.rect)

    font = pygame.font.Font(None, 36)
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    score_rect = score_text.get_rect()
    score_rect.center = (screen_width // 2, screen_height - 30)
    screen.blit(score_text, score_rect)

    timer_text = font.render("Time: " + str(timer // 60), True, (255, 255, 255))
    timer_rect = timer_text.get_rect()
    timer_rect.bottomright = (screen_width - 10, screen_height - 10)
    screen.blit(timer_text, timer_rect)

    # Render remaining lives
    lives_text = font.render("Lives: " + str(player.health), True, (255, 255, 255))
    lives_rect = lives_text.get_rect()
    lives_rect.bottomleft = (10, screen_height - 10)
    screen.blit(lives_text, lives_rect)

    font = pygame.font.Font(None, 24)  # Lower the font size to 24

    # Display current game mechanics
    current_dmg_text = font.render("Current DMG of bullets: " + "{:.2f}".format(player.bullet_damage), True,
                                   (255, 255, 255))
    current_dmg_rect = current_dmg_text.get_rect()
    current_dmg_rect.midright = (screen_width - 20, screen_height // 2 - 100)
    screen.blit(current_dmg_text, current_dmg_rect)

    # for enemy in enemies:
    # current_health_text = font.render("Max HEALTH of enemies: " + str(max_enemy_health), True, (255, 255, 255))
    # current_health_rect = current_health_text.get_rect()
    # current_health_rect.midright = (screen_width - 20, screen_height // 2 + 50)
    # screen.blit(current_health_text, current_health_rect)

    current_spawn_rate_text = font.render("Current spawn rate of enemies: " + "{:.2f}".format(enemy_spawn_ratio), True,
                                          (255, 255, 255))
    current_spawn_rate_rect = current_spawn_rate_text.get_rect()
    current_spawn_rate_rect.midright = (screen_width - 20, screen_height // 2 - 50)
    screen.blit(current_spawn_rate_text, current_spawn_rate_rect)

    pygame.display.update()

def game_over():
    background_music.stop()
    game_over_sound.play()
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect()
    game_over_rect.center = (screen_width // 2, screen_height // 2)
    screen.blit(game_over_text, game_over_rect)

    final_score_text = font.render("Final Score: " + str(score), True, (255, 255, 255))
    final_score_rect = final_score_text.get_rect()
    final_score_rect.center = (screen_width // 2, screen_height // 2 + 100)
    screen.blit(final_score_text, final_score_rect)

    pygame.display.update()

    pygame.time.wait(5000)
    pygame.quit()
    sys.exit()

def start_screen():
    font = pygame.font.Font(None, 72)
    welcome_text = font.render("GPTlaga", True, (0, 255, 0))
    welcome_rect = welcome_text.get_rect()
    welcome_rect.center = (screen_width // 2, screen_height // 2)
    screen.blit(welcome_text, welcome_rect)
    pygame.display.update()
    start_screen_sound.play()
    pygame.time.wait(5000)
    start_screen_sound.stop()

# Run the Game
if __name__ == "__main__":
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    enemy_image, player_image, bullet_image = load_graphics()

    player.image = player_image
    player.rect = player.image.get_rect()
    player.rect.center = (screen_width // 2, screen_height - 50)

    start_screen()
    background_music.play()
    while True:
        spawn_enemies()
        handle_input()
        update_game_state()
        bullets.update()
        render_graphics()
        clock.tick(60)
