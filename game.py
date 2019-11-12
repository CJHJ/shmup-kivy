from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.graphics import Rotate
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.uix.label import Label
from random import randint

# widget drawer


class WidgetDrawer(Widget):
    # This widget is used to draw all of the objects on the screen
    # it handles the following:
    # widget movement, size, positioning
    def __init__(self, imageStr, **kwargs):
        super(WidgetDrawer, self).__init__(**kwargs)

        with self.canvas:
            self.size = (Window.width*.0015*40, Window.width*.0015*25)
            self.rect_bg = Rectangle(
                source=imageStr, pos=self.pos, size=self.size)

            self.bind(pos=self.update_graphics_pos)
            self.x = self.center_x
            self.y = self.center_y
            self.pos = (self.x, self.y)
            self.rect_bg.pos = self.pos

    def update_graphics_pos(self, instance, value):
        self.rect_bg.pos = value

    def setSize(self, width, height):
        self.size = (width, height)

    def setPos(xpos, ypos):
        self.x = xpos
        self.y = ypos

# add player ship


class PlayerShip(Widget):
    score = NumericProperty(0)

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

# Game over text


class GameoverText(Widget):

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

# player bullet


class Bullet(WidgetDrawer):
    imageStr = './assets/bullet.png'
    rect_bg = Rectangle(source=imageStr)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y

    def update(self):
        self.move()

# Asteroid


class Asteroid(WidgetDrawer):
    imageStr = './assets/sandstone_1.png'
    rect_bg = Rectangle(source=imageStr)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y

    def update(self):
        self.move()


class ShmupGame(Widget):
    # lists of asteroids and bullets
    asteroidList = []
    bulletList = []

    # maximum bullets
    maxBullet = 3
    bulletFired = False
    bulletCount = 0

    game = True

    player = ObjectProperty(None)
    goText = ObjectProperty(None)
    minProb = 1780

    # allow keyboard inputs and scrolling backgrounds
    def __init__(self, **kwargs):
        super(ShmupGame, self).__init__(**kwargs)

        with self.canvas.before:
            texture = CoreImage('./assets/bg.png').texture
            texture.wrap = 'repeat'
            self.rect_1 = Rectangle(
                texture=texture, size=(800 * 2, 600 * 2), pos=self.pos)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    # spawn player
    def spawn_player(self):
        self.player.center = self.center
        self.player.velocity = Vector(4, 0).rotate(randint(0, 360))
        self.remove_widget(self.goText)

    # add asteroids
    def add_asteroid(self):
        # add an asteroid to the screen
        imageNumber = randint(1, 4)
        imageStr = './assets/sandstone_'+str(imageNumber)+'.png'
        tmpAsteroid = Asteroid(imageStr)
        tmpAsteroid.x = Window.width*0.99

        # randomize y position
        ypos = randint(1, 16)
        ypos = ypos*Window.height*.0625
        tmpAsteroid.y = ypos
        tmpAsteroid.velocity_y = 0
        vel = 55  # randint(10,25)
        tmpAsteroid.velocity_x = -0.1*vel
        self.asteroidList.append(tmpAsteroid)
        self.add_widget(tmpAsteroid)

    def add_bullet(self):
        # add a bullet to the screen
        imageStr = './assets/bullet.png'
        tmpBullet = Bullet(imageStr)
        tmpBullet.x = self.player.pos[0]

        ypos = self.player.pos[1]
        tmpBullet.y = ypos
        tmpBullet.velocity_y = 0
        vel = 55  # randint(10,25)
        tmpBullet.velocity_x = 0.1*vel
        self.bulletList.append(tmpBullet)
        self.add_widget(tmpBullet)

    def spawn_asteroid(self):
        # randomly add asteroid
        tmpCount = randint(1, 1800)
        if tmpCount > self.minProb:
            self.add_asteroid()
            if self.minProb < 1000:
                self.minProb = 1000
            self.minProb = self.minProb - 1

    def update(self, dt):
        # scroll background
        t = Clock.get_boottime()
        self.rect_1.tex_coords = - \
            (t * 0.05), 0, -(t * 0.05 + 1), 0,  - \
            (t * 0.05 + 1), -1, -(t * 0.05), -1

        # set boundary
        if self.player.pos[0]-25 < 0:
            self.player.pos[0] = 25
        elif self.player.pos[0]+25 > self.size[0]:
            self.player.pos[0] = self.size[0]-25
        if self.player.pos[1]-15 < 0:
            self.player.pos[1] = 15
        elif self.player.pos[1]+15 > self.size[1]:
            self.player.pos[1] = self.size[1]-15

        # bullet time
        if self.bulletFired:
            if self.bulletCount < 60:
                self.bulletCount += 1
            else:
                self.bulletCount = 0
                self.bulletFired = False

        if self.game:
            self.spawn_asteroid()

        # for every asteroid run checkings
        for k in self.asteroidList:
            # if collided with player's bullet
            for l in self.bulletList:
                if k.collide_widget(l):
                    print('boom')
                    # remove asteroid
                    self.remove_widget(k)
                    self.asteroidList.remove(k)

                    # remove bullet
                    self.remove_widget(l)
                    self.bulletList.remove(l)

                    self.player.score += 1

            # check for collision with ship
            if k.collide_widget(self.player):
                print('death')
                Clock.unschedule(self.update)
                self.game = False
                self.player.pos[0] = -100
                self.player.pos[1] = -100
                self.remove_widget(k)
                # game over routine
                self.game_over()

            k.update()
            # check to see if asteroid is off the screen
            if k.x < -100:
                # since it's off the screen, remove the asteroid
                self.remove_widget(k)
                self.asteroidList.remove(k)

        for l in self.bulletList:
            l.update()
            if l.x > self.size[0]:
                self.remove_widget(l)
                self.bulletList.remove(l)

    def reset(self):

        # clean screen
        self.player.pos[0] = 10
        self.player.pos[1] = self.size[1]/2

        self.add_widget(self.player)
        print(len(self.asteroidList))
        for k in self.asteroidList:
            self.remove_widget(k)
        for l in self.bulletList:
            self.remove_widget(l)
        print(self.asteroidList)
        self.asteroidList = []
        self.bulletList = []
        self.player.score = 0
        self.game = True
        bulletFired = False
        bulletCount = 0
        self.remove_widget(self.goText)

        Clock.schedule_interval(self.update, 1.0/60.0)

    def game_over(self):
        self.remove_widget(self.player)
        self.add_widget(self.goText)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.game:
            if keycode[1] == 'up':
                self.player.center_y += 10
            elif keycode[1] == 'down':
                self.player.center_y -= 10
            elif keycode[1] == 'left':
                self.player.center_x -= 10
            elif keycode[1] == 'right':
                self.player.center_x += 10
            elif keycode[1] == 'z':
                if len(self.bulletList) < 3 and self.bulletFired == False:
                    self.add_bullet()
                    self.bulletFired = True
        else:
            if keycode[1] == 'r':
                self.reset()
        return True


class ShmupApp(App):
    def build(self):
        game = ShmupGame()
        game.spawn_player()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game


if __name__ == '__main__':
    ShmupApp().run()
