import random
import os
import json
import time
import pygame

pygame.init()

#Anulowanie klatek jest kinda op - do naprawy
#Drylownica działa, nie wiem jak to naprawic
#Przydały by sie tapy pulle itd ale to nie jest tego warte

# Constants
WIDTH = 482
HEIGHT = 224
FPS = 30
GRAVITY = 0.5
CON1DEADZONE = 0.0
CON2DEADZONE = 0.0

# Initialize screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CrapFighter")
clock = pygame.time.Clock()

# Groups
all_sprites = pygame.sprite.Group()
characters = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

fx = pygame.sprite.Group()
foreground = pygame.sprite.Group()
ground = pygame.sprite.Group()
background = pygame.sprite.Group()
debug = pygame.sprite.Group()
ui = pygame.sprite.Group()

# Characters
charactersplayer1 = pygame.sprite.Group()
charactersplayer2 = pygame.sprite.Group()

# Store Character instances
characters_list = []

# Load available characters and maps
def load_available_characters():
    characters_dir = "assets/characters"
    characters = [d for d in os.listdir(characters_dir) if os.path.isdir(os.path.join(characters_dir, d))]
    return characters

def load_available_maps():
    maps_dir = "assets/stages"
    maps = [d for d in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, d))]
    return maps

# Character and map selectors
def character_selector(player_num):
    available_characters = load_available_characters()
    print(f"Player {player_num}, select your character:")
    for i, character in enumerate(available_characters):
        print(f"{i + 1}. {character}")
    choice = int(input(f"Enter the number of your choice (1-{len(available_characters)}): ")) - 1
    return os.path.join("assets/characters", available_characters[choice], "character.json")

def map_selector():
    available_maps = load_available_maps()
    print("Select a map:")
    for i, map_name in enumerate(available_maps):
        print(f"{i + 1}. {map_name}")
    choice = int(input(f"Enter the number of your choice (1-{len(available_maps)}): ")) - 1
    return os.path.join("assets/stages", available_maps[choice], "map.json")

# Select characters and map
CHARACTER1PATH = character_selector(1)
CHARACTER2PATH = character_selector(2)
MAPPATH = map_selector()

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, range, damage, owner, image_path, duration):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.range = range
        self.damage = damage
        self.owner = owner
        self.lifetime = duration * FPS  # Convert duration from seconds to frames
        self.speed = self.range / self.lifetime  # Calculate speed based on range and duration
        if debug:
            print(f"Projectile created at ({x}, {y}) with speed {self.speed} and direction {self.direction}")

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

        # Move the projectile
        self.rect.x += self.direction * self.speed
        if debug:
            print(f"Projectile moved to ({self.rect.x}, {self.rect.y}) with speed {self.speed} and direction {self.direction}")

        # Check for collision with characters
        self.check_collision()
                
    def check_collision(self):
        for character_sprite in characters:
            character = character_sprite.character_ref
            if character != self.owner and self.rect.colliderect(character.sprite.rect):
                if character.is_blocking:
                    character.health -= self.damage * 0.5  # Reduce damage by 50% when blocking
                else:
                    character.health -= self.damage
                character.trigger_hit_animation()  # Trigger hit animation
                self.owner.update_ulti_charge("projectile", hit=True)  # Update ultimate charge on hit
                if character.health <= 0:
                    character.play_death_animation()
                else:
                    self.owner.update_ulti_charge("health_lowered", hit=True)  # Update ultimate charge when health is lowered
                self.kill()

# Attack class
class Attack(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, length, damage, owner):
        super().__init__()
        self.image = pygame.Surface((length, length), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (255, 0, 0), [(0, 0), (length, length // 2), (0, length)])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.damage = damage
        self.owner = owner
        self.lifetime = 1  # Lifetime in frames
        self.character_ref = owner  # Reference to the Character instance

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

        # Check for collision with characters
        self.check_collision()

    def check_collision(self):
        for character_sprite in characters:
            character = character_sprite.character_ref
            if character != self.owner and self.rect.colliderect(character.sprite.rect):
                if character.is_blocking:
                    character.health -= self.damage * 0.25
                else:
                    character.health -= self.damage
                character.trigger_hit_animation()  # Trigger hit animation
                self.owner.update_ulti_charge("attack", hit=True)  # Update ultimate charge on hit
                if character.health <= 0:
                    character.play_death_animation()
                else:
                    self.owner.update_ulti_charge("health_lowered", hit=True)  # Update ultimate charge when health is lowered
                self.kill()

# Character class
class Character:
    def __init__(self, file, player, spawn_x, spawn_y):
        with open(file) as f:
            self.character_data = json.load(f)
        playercharacter = pygame.sprite.Sprite()
        playercharacter.image = pygame.image.load(f"assets/characters/{self.character_data['name']}/idle/1.png")
        playercharacter.rect = playercharacter.image.get_rect()
        playercharacter.rect.size = playercharacter.image.get_size()
        playercharacter.rect.center = (spawn_x, spawn_y)
        playercharacter.orientation = "right"
        playercharacter.character_ref = self  # Reference to the Character instance
        self.last_action_time = time.time()
        self.last_update_time = time.time()
        self.last_ulti_regen_time = time.time()  # Track last ulti regen time
        self.player = player
        self.status = "Idle"
        self.current_frame = 0
        self.is_jumping = False
        self.can_double_jump = self.character_data["stats"]["canDoubleJump"]
        self.has_double_jumped = False
        self.vertical_speed = 0
        self.cooldowns = {
            "attack": 0,
            "ability1": 0,
            "ability2": 0,
            "ulti": 0
        }
        self.is_falling = True
        self.is_stunned = False
        self.is_immobile = False
        self.pulled = False
        self.doingaction = False
        self.ulti_capacity = self.character_data["stats"]["ExCapacity"]  # Set ulti_capacity
        self.is_blocking = False  # Initialize blocking state
        if player == 1:
            charactersplayer1.add(playercharacter)
        if player == 2:
            charactersplayer2.add(playercharacter)
        characters.add(playercharacter)
        all_sprites.add(playercharacter)
        self.sprite = playercharacter
        self.speed = self.character_data["stats"]["speed"]
        self.jump_height = self.character_data["stats"]["jumpHeight"]
        self.health = self.character_data["stats"]["health"]
        self.ExCapacity = self.character_data["stats"]["ExCapacity"]
        self.ulti_charge = 0  # Initialize ulti_charge
        self.is_dead = False
        characters_list.append(self)

    def trigger_hit_animation(self):
        if self.is_dead:
            return
        self.status = "Hit"
        self.current_frame = 0
        self.update_animation()

    def update_animation(self):
        current_time = time.time()
        if self.is_dead:
            if self.status == "death":
                anim_folder = self.character_data["anims"]["Death"]
                frame_path = f"assets/characters/{self.character_data['name']}/{anim_folder}/{self.current_frame}.png"
                image = pygame.image.load(frame_path)
                if self.sprite.orientation == "left":
                    image = pygame.transform.flip(image, True, False)
                self.sprite.image = image

                next_frame_path = f"assets/characters/{self.character_data['name']}/{anim_folder}/{self.current_frame + 1}.png"
                if os.path.exists(next_frame_path):
                    self.current_frame += 1
                return

        if not self.is_jumping and not self.is_falling and current_time - self.last_action_time > 0.2:
            self.status = "Idle"

        # Slow down idle animation by updating every 0.5 seconds
        idle_update_interval = 0.5 if self.status == "Idle" else 0.1

        if current_time - self.last_update_time > idle_update_interval:
            anim_folder = self.character_data["anims"].get(self.status, self.character_data["anims"]["Idle"])
            frame_path = f"assets/characters/{self.character_data['name']}/{anim_folder}/{self.current_frame}.png"
            image = pygame.image.load(frame_path)
            if self.sprite.orientation == "left":
                image = pygame.transform.flip(image, True, False)
            self.sprite.image = image

            next_frame_path = f"assets/characters/{self.character_data['name']}/{anim_folder}/{self.current_frame + 1}.png"
            if os.path.exists(next_frame_path):
                self.current_frame += 1
            else:
                self.current_frame = 0

            self.last_update_time = current_time

    def update_ulti_charge(self, activity, hit=False):
        if activity == "idle":
            self.ulti_charge += self.character_data["stats"]["ExPassiveRegen"]
        elif activity == "walk":
            self.ulti_charge += self.character_data["stats"]["ExPassiveRegen"] * 2
        elif activity == "attack" and hit:
            self.ulti_charge += self.character_data["stats"]["ExActiveRegen"]
        elif activity in ["ability1", "ability2", "ulti"] and hit:
            self.ulti_charge += self.character_data["stats"]["ExAbilityRegen"]
        elif activity == "health_lowered" and hit:
            self.ulti_charge += self.character_data["stats"]["ExActiveRegen"]

        if self.ulti_charge > self.ulti_capacity:
            self.ulti_charge = self.ulti_capacity

    def perform_action(self, action):
        if self.is_dead:
            return False

        self.last_action_time = time.time()
        if self.status != action:
            self.status = action
            self.current_frame = 0
        self.update_animation()
        return True

    def execute_ability(self, ability_name):
        if self.is_dead:
            return

        ability = self.character_data["abilities"].get(ability_name)
        if not ability:
            print(f"Ability {ability_name} not found for character {self.character_data['name']}")
            return

        ability_key = ability_name.lower().replace(" ", "")
        if not self.is_ability_usable(ability):
            print(f"Ability {ability_name} is not usable for character {self.character_data['name']}")
            return

        self.cooldowns[ability_key] = time.time() + ability["cooldown"]
        self.use_ex_charge(ability["cost"])
        self.perform_action(ability_name)

        if ability["type"] == "melee":
            self.create_attack(ability)
        elif ability["type"] == "buff":
            self.apply_buff(ability)
        elif ability["type"] == "debuff":
            self.apply_debuff(ability)
        elif ability["type"] == "projectile":
            self.create_projectile(ability["cost"], ability["damage"], ability["range"], f"assets/characters/{self.character_data['name']}/{ability['sprite']}", ability["duration"])
        elif ability["type"] == "pull":
            self.apply_pull(ability)
        elif ability["type"] == "break":
            self.apply_break(ability)
        elif ability["type"] == "tap":
            self.apply_tap(ability)
        elif ability["type"] == "hold":
            self.apply_hold(ability)
        elif ability["type"] == "v-reversal":
            self.create_projectile(ability["cost"], ability["damage"], ability["range"], f"assets/characters/{self.character_data['name']}/{ability['sprite']}", ability["duration"])

    def use_ex_charge(self, amount):
        if self.ulti_charge >= amount:
            self.ulti_charge -= amount
            return True
        return False

    def create_attack(self, ability):
        direction = 1 if self.sprite.orientation == "right" else -1
        damage = ability.get("damage", 0)
        attack = Attack(self.sprite.rect.centerx, self.sprite.rect.centery, direction, ability["range"], damage, self)
        all_sprites.add(attack)
        characters.add(attack)

    def create_projectile(self, cost, damage, range, image_path, duration):
        if self.is_dead:
            return

        if self.use_mana(cost):
            direction = 1 if self.sprite.orientation == "right" else -1
            projectile = Projectile(self.sprite.rect.centerx, self.sprite.rect.centery, direction, range, damage, self, image_path, duration)
            projectiles.add(projectile)
            all_sprites.add(projectile)

    def apply_buff(self, ability):
        self.health += ability.get("health", 0)
        self.speed += ability.get("speed", 0)
        self.jump_height += ability.get("jumpHeight", 0)

    def apply_debuff(self, ability):
        for character_sprite in characters:
            character = character_sprite.character_ref
            if character != self:
                character.health -= ability.get("damage", 0)
                character.speed -= ability.get("speed", 0)
                character.jump_height -= ability.get("jumpHeight", 0)

    def apply_pull(self, ability):
        # Implement pull logic here
        pass

    def apply_break(self, ability):
        # Implement break logic here
        pass

    def apply_tap(self, ability):
        # Implement tap logic here
        pass

    def apply_hold(self, ability):
        # Implement hold logic here
        pass

    def is_ability_usable(self, ability):
        ability_key = ability["name"].lower().replace(" ", "")
        return time.time() > self.cooldowns.get(ability_key, 0) and self.ulti_charge >= ability["cost"]

    def update_stats(self):
        self.speed = self.character_data["stats"]["speed"]
        self.jump_height = self.character_data["stats"]["jumpHeight"]
        self.health = self.character_data["stats"]["health"]
        self.ExCapacity = self.character_data["stats"]["ExCapacity"]
        #self.ulti_capacity = self.character_data["stats"]["UltiCapacity"]

    def jump(self):
        if character.is_dead or character.is_stunned or character.is_immobile or character.pulled or character.doingaction:
            return

        if not self.is_jumping:
            self.is_jumping = True
            self.vertical_speed = -self.jump_height
            self.perform_action("Jump")
        elif self.can_double_jump and not self.has_double_jumped:
            self.has_double_jumped = True
            self.vertical_speed = -self.jump_height
            self.perform_action("Jump")

    def apply_gravity(self):
        if self.is_dead:
            return

        if self.is_jumping or self.is_falling:
            self.vertical_speed += GRAVITY
            self.sprite.rect.y += self.vertical_speed
            if self.sprite.rect.bottom >= HEIGHT:
                self.sprite.rect.bottom = HEIGHT
                self.is_jumping = False
                self.is_falling = False
                self.has_double_jumped = False
                self.vertical_speed = 0
            elif self.vertical_speed > 0:
                self.is_falling = True
                self.status = "Fall"
            else:
                self.is_falling = False

    def use_mana(self, amount):
        if self.ExCapacity >= amount:
            self.ExCapacity -= amount
            return True
        return False

    def play_death_animation(self):
        self.status = "death"
        self.is_dead = True
        self.current_frame = 0
        self.update_animation()

    def passive_ulti_regen(self):
        current_time = time.time()
        if current_time - self.last_ulti_regen_time >= 1:
            self.ulti_charge += self.character_data["stats"]["ExPassiveRegen"]
            if self.ulti_charge > self.ulti_capacity:
                self.ulti_charge = self.ulti_capacity
            self.last_ulti_regen_time = current_time

    def block(self):
        if self.is_dead:
            return
        self.is_blocking = True
        self.perform_action("Block")

    def stop_blocking(self):
        self.is_blocking = False

# Functions
def move_character(character, direction):
    if character.is_dead or character.is_stunned or character.is_immobile or character.pulled or character.doingaction:
        return

    speed = character.speed
    character.perform_action("Run")
    
    if direction == "left":
        if character.sprite.rect.x > 0:
            character.sprite.rect.x -= speed
        if character.sprite.orientation != "left":
            character.sprite.orientation = "left"
    elif direction == "right":
        if character.sprite.rect.x <  WIDTH - character.sprite.rect.size[0]:
            character.sprite.rect.x += speed
        if character.sprite.orientation != "right":
            character.sprite.orientation = "right"
    else:
        print("Invalid direction")

def CreateDebugObjectOnSurface(surface, color, x, y, width, height):
    def add_debug_object(surface_group, x, y, width, height, color):
        debug_object = pygame.sprite.Sprite()
        debug_object.image = pygame.Surface((width, height))
        debug_object.image.fill(color)
        debug_object.rect = debug_object.image.get_rect()
        debug_object.rect.topleft = (x, y)
        surface_group.add(debug_object)
        all_sprites.add(debug_object)
    
    surface_groups = {
        "characters": characters,
        "background": background,
        "foreground": foreground,
        "ground": ground,
        "fx": fx,
        "ui": ui,
        "debug": debug
    }
    
    if surface in surface_groups:
        add_debug_object(surface_groups[surface], x, y, width, height, color)
    else:
        print("Surface not found, defaulting to all_sprites")
        add_debug_object(all_sprites, x, y, width, height, color)

# Load map data
def load_map(file):
    with open(file) as f:
        map_data = json.load(f)
    
    map_name = map_data["name"]
    
    # Load background frames
    for frame_data in map_data["background"]:
        frame_image = pygame.image.load(f"assets/stages/{map_name}/background/{frame_data['image']}")
        frame_image = pygame.transform.scale(frame_image, (WIDTH, HEIGHT))  # Stretch to fit screen
        background_sprite = pygame.sprite.Sprite()
        background_sprite.image = frame_image
        background_sprite.rect = frame_image.get_rect()
        background.add(background_sprite)
    
    # Load foreground frames
    for frame_data in map_data["foreground"]:
        frame_image = pygame.image.load(f"assets/stages/{map_name}/foreground/{frame_data['image']}")
        frame_image = pygame.transform.scale(frame_image, (WIDTH, HEIGHT))  # Stretch to fit screen
        foreground_sprite = pygame.sprite.Sprite()
        foreground_sprite.image = frame_image
        foreground_sprite.rect = frame_image.get_rect()
        foreground.add(foreground_sprite)
    
    # Load ground frame
    ground_frame_data = map_data["ground"]
    ground_image = pygame.image.load(f"assets/stages/{map_name}/ground/{ground_frame_data['image']}")
    ground_image = pygame.transform.scale(ground_image, (WIDTH, ground_image.get_height()))  # Stretch to fit width
    ground_sprite = pygame.sprite.Sprite()
    ground_sprite.image = ground_image
    ground_sprite.rect = ground_image.get_rect()
    ground_sprite.rect.y = HEIGHT - ground_sprite.rect.height  # Position ground at the bottom
    ground.add(ground_sprite)

# Load the map
load_map(MAPPATH)

def draw_ui():
    font = pygame.font.Font(None, 36)
    health_text1 = font.render(f"Health: {character1.health}", True, (255, 255, 255))
    excharge_text1 = font.render(f"ExCharge: {character1.ulti_charge}", True, (255, 255, 255))
    health_text2 = font.render(f"Health: {character2.health}", True, (255, 255, 255))
    excharge_text2 = font.render(f"ExCharge: {character2.ulti_charge}", True, (255, 255, 255))

    screen.blit(health_text1, (10, 10))
    screen.blit(excharge_text1, (10, 50))
    screen.blit(health_text2, (WIDTH - 200, 10))
    screen.blit(excharge_text2, (WIDTH - 200, 50))


def display_game_over_message(winner):
    font = pygame.font.Font(None, 74)
    text = font.render(f"{winner} Wins!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(1)  # Wait for 1 second before quitting
    pygame.quit()
    exit()

# Load character data
character1 = Character(CHARACTER1PATH, 1, 100, HEIGHT - 100)
character2 = Character(CHARACTER2PATH, 2, WIDTH - 100, HEIGHT - 100)

running = True
is_debug = False
game_over = False  # Flag to indicate game over state

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_w:
                    character1.jump()
                if event.key == pygame.K_UP:
                    character2.jump()
                if event.key == pygame.K_s:
                    character1.block()
                if event.key == pygame.K_DOWN:
                    character2.block()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    character1.stop_blocking()
                if event.key == pygame.K_DOWN:
                    character2.stop_blocking()

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            move_character(character1, "left")
            character1.update_ulti_charge("walk")
        if keys[pygame.K_d]:
            move_character(character1, "right")
            character1.update_ulti_charge("walk")
        if keys[pygame.K_LEFT]:
            move_character(character2, "left")
            character2.update_ulti_charge("walk")
        if keys[pygame.K_RIGHT]:
            move_character(character2, "right")
            character2.update_ulti_charge("walk")
        if keys[pygame.K_1]:
            character1.execute_ability("LightPunch")
        if keys[pygame.K_2]:
            character1.execute_ability("HeavyPunch")
        if keys[pygame.K_3]:
            character1.execute_ability("LightKick")
        if keys[pygame.K_4]:
            character1.execute_ability("HeavyKick")
        if keys[pygame.K_5]:
            character1.execute_ability("V-Skill")
        if keys[pygame.K_6]:
            character1.execute_ability("V-Trigger")
        if keys[pygame.K_7]:
            character1.execute_ability("V-Reversal")
        if keys[pygame.K_8]:
            character1.execute_ability("EX-Buff")
        if keys[pygame.K_KP1]:
            character2.execute_ability("LightPunch")
        if keys[pygame.K_KP2]:
            character2.execute_ability("HeavyPunch")
        if keys[pygame.K_KP3]:
            character2.execute_ability("LightKick")
        if keys[pygame.K_KP4]:
            character2.execute_ability("HeavyKick")
        if keys[pygame.K_KP5]:
            character2.execute_ability("V-Skill")
        if keys[pygame.K_KP6]:
            character2.execute_ability("V-Trigger")
        if keys[pygame.K_KP7]:
            character2.execute_ability("V-Reversal")
        if keys[pygame.K_KP8]:
            character2.execute_ability("EX-Buff")

    # Call passive_ulti_regen and apply_gravity for each character
    for character in characters_list:
        character.passive_ulti_regen()
        character.apply_gravity()

    # Update animations for all characters
    for character in characters_list:
        character.update_animation()

    # Check for game over condition
    if character1.health <= 0 and not game_over:
        game_over = True
        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Set a timer for 1 second
    if character2.health <= 0 and not game_over:
        game_over = True
        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Set a timer for 1 second

    if game_over and event.type == pygame.USEREVENT:
        if character1.health <= 0:
            display_game_over_message("Player 2")
        if character2.health <= 0:
            display_game_over_message("Player 1")

    # Update all sprites
    all_sprites.update()

    # Draw everything
    screen.fill((0, 0, 0))

    background.draw(screen)
    ground.draw(screen)  # Ensure ground is drawn before characters
    foreground.draw(screen)
    characters.draw(screen)
    projectiles.draw(screen)  # Ensure projectiles are drawn
    fx.draw(screen)
    ui.draw(screen)
    debug.draw(screen)

    draw_ui()  # Draw the UI

    pygame.display.flip()

pygame.quit()