import pygame
import levels
import time
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#Using pygame clock function to set a default fps for the game
clock = pygame.time.Clock()
fps = 60

#Our default screen size so it can work on any laptop and on the monitor too
screen_width = 700
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Jingle Jump')

#define font
font = pygame.font.Font('pixelfont.ttf', 60)
font_score = pygame.font.SysFont('Bauhaus 93', 32)

#define game variables
tile_size = 35
game_over = 0
main_menu = True
level = 1
max_levels = 2
score = 0

#define colours
white = (255, 255, 255)
blue = (0, 0, 0)

#load images
bg_img = pygame.image.load('img/sky2.png')
main_menu_img = pygame.image.load('img/main_menu.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#load sounds
pygame.mixer.music.load('music/mario.mp3')
# pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)
game_win_fx = pygame.mixer.Sound('music/win.mp3')
game_win_fx.set_volume(0.5)


# def draw_grid():
#     """ This is a demonstration function for the game to show how our game works. I have divided
#         the game screen in a grid. Doing this will make the future development easy, so we can use
#         each tile for something. You can use this function in the main game loop to see the grid."""
#     for line in range(0, 20):
# 	    pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size,
#
#                                                                            screen_height))

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


# function to reset level
def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    """Loading World Data Using External Python File (levels.py)"""
    world_data = levels.getLevel(level)
    world = World(world_data)

    return world

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action

# Player Class
class Player():
    """This is the main player class and it will be used to create, show, update and all the
    things needed for the player."""

    def __init__(self, x, y):
        self.reset(x, y)


    def update(self, game_over):
        """This is the player update function. This is the most important function for the
        player class because it will be used to update every thing we do with the player. Every
        thing which is created in the self function will be updated here. For example, the player
        animation loop is made in the default class, but it is updated here so whenever player moves
        to the right the animation loop goes through to change the image."""
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over ==0:
            # get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1

            if key[pygame.K_a] == False and key[pygame.K_d] == False :
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collision
            self.in_air = True
            for tile in world.tile_list:
                """ Very simple logic is behind the collision, every tile in the world is a 
                rectangle. We are basically running a for loop to go through each tile and checking 
                if their x and y coordinates are colliding with the players coordinates. If they collide
                we dont let player move any further."""

                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # check for collision with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                pygame.mixer.music.stop()
                game_over = -1
                game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                pygame.mixer.music.stop()
                game_over = -1
                game_over_fx.play()

            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0

        elif game_over == -1:
            self.image = self.dead_image
            screen.blit(bg_img, (0, 0))
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 140, screen_height // 2 - 10)
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player onto screen
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (28, 56))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    """This is the world-class used to create a world. By world, I mean everything you
    will see in the game. We are using a grid system so for each tile something is added."""
    def __init__(self, data):
        self.tile_list = []

        # load images
        snow_block = pygame.image.load('img/dirt_snow.png')
        dirt = pygame.image.load('img/dirt.png')
        snowflake_img = pygame.image.load('img/snowflake.png')


        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(snowflake_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(snow_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(dirt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 3)
                    blob_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    gift = Gift(col_count * tile_size, row_count * tile_size + 3)
                    gift_group.add(gift)
                if tile == 8:
                    exit_ = Exit(col_count * tile_size, row_count * tile_size - (tile_size/2))
                    exit_group.add(exit_)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/snowman.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 35:
			self.move_direction *= -1
			self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Gift(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/gift.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size * 1.5))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


player = Player(100, screen_height - 91)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
gift_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#creating a dummy coin for showing the score
score_gift = Gift(tile_size/2, tile_size/2)
gift_group.add(score_gift)

"""Loading World Data Using External Python File (levels.py)"""
world_data = levels.getLevel(level)
world = World(world_data)

#Creating some buttons
restart_button = Button(screen_width // 2 - 35, screen_height // 2 - 50, restart_img)
start_button = Button(screen_width // 2 - 300, screen_height // 2 , start_img)
exit_button = Button(screen_width // 2 - 300, screen_height // 2 + 150, exit_img)
menu_button = Button(screen_width // 2 - 35, screen_height // 2 - 50, restart_img)


run = True
while run:
    """ Setting frame rate here, fps variable is defined above which is 60 that means our game will 
    run on 60 fps """

    clock.tick(fps)


    if main_menu == True:
        screen.blit(main_menu_img, (0, 0))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
            game_win_fx.stop()
            mixer.music.play()

    else:
        screen.blit(bg_img, (0, 0))

        world.draw()

        if game_over == 0:
            if level==2:
                blob_group.update()

            #Checking for if the player has collided with the gift
            if pygame.sprite.spritecollide(player, gift_group, True):
                score += 1
                coin_fx.play()
            draw_text('X  -  ' + str(score), font_score, white, tile_size , 25)

        blob_group.draw(screen)
        lava_group.draw(screen)
        gift_group.draw(screen)
        exit_group.draw(screen)


        game_over = player.update(game_over)

        # draw_grid()

        # if player has died
        if game_over == -1:
            if restart_button.draw():
                pygame.mixer.music.play(-1, 0.0, 5000)
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
                # gift_group.empty()

        if game_over == 1:
            # reset game and go to next level
            level += 1
            if level <= max_levels:
                pygame.mixer.music.play(-1, 0.0, 5000)
                gift_group.empty()
                score_gift = Gift(tile_size / 2, tile_size / 2)
                gift_group.add(score_gift)
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
            else:
                screen.blit(bg_img, (0, 0))
                mixer.music.stop()
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 100, screen_height // 2)
                game_win_fx.play()
                if restart_button.draw():
                    gift_group.empty()
                    score_gift = Gift(tile_size / 2, tile_size / 2)
                    gift_group.add(score_gift)
                    level = 1
                    # reset level
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0
                    main_menu = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()