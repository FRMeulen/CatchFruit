import random
from pyglet.gl import *

orthoWidth = 1000
orthoHeight = 750
fieldHeight = 650

class Attribute:
    def __init__(self, game):
        self.game = game
        self.game.attributes.append(self)
        self.install()
        self.reset()
    
    def reset (self):
        self.commit()
    
    def predict (self):
        pass
    
    def interact (self):
        pass
    
    def commit (self):
        pass
        
class Sprite(Attribute):
    def __init__(self, game, width, height):
        self.width = width
        self.height = height
        Attribute.__init__(self, game)
    
    def install (self):
        image = pyglet.image.create(
            self.width,
            self.height,
            pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        )
        
        image.anchor_x = self.width // 2
        image.anchor_y = self.height // 2
        
        self.pygletSprite = pyglet.sprite.Sprite (image, 0, 0, batch = self.game.batch)

    def reset(self, vX = 0, vY = 0, x = orthoWidth // 2, y = fieldHeight // 2):
        self.vX = vX
        self.vY = vY
        
        self.x = x
        self.y = y

        Attribute.reset(self)
        
    def predict(self):
        self.x += self.vX * self.game.deltaT
        self.y += self.vY * self.game.deltaT
    
    def commit (self):
        self.pygletSprite.x = self.x
        self.pygletSprite.y = self.y
        
class Basket (Sprite):
    margin = 30
    width = 75
    height = 10
    speed = 500
    
    def __init__(self, game):
        Sprite.__init__ (self, game, self.width, self.height)
    
    def reset (self):
        Sprite.reset(
            self,
            x = orthoWidth // 2,
            y = self.margin
        )
    
    def predict (self):
        self.vX = 0
        
        if self.game.keymap [pyglet.window.key.A]:
            self.vX = -self.speed
        elif self.game.keymap [pyglet.window.key.D]:
            self.vX = self.speed
        
        Sprite.predict(self)
    
    def interact (self):
        self.x = max (self.width / 2, min (self.x, orthoWidth - self.width // 2))
    
        if (
            ((self.x - self.width // 2) - 5)  < self.game.fruit.x < ((self.x + self.width // 2) + 5)
            and (
                (self.game.fruit.y < self.y)
            )
        ):
            self.game.fruit.x = self.x
            self.game.succeeded()

class Fruit (Sprite):
    side = 8
    speed = -250
    
    def __init__ (self, game):
        Sprite.__init__(self, game, self.side, self.side)

    def reset(self):
        Sprite.reset(
            self,
            y = fieldHeight,
            x = random.randint(0, orthoWidth),
            vY = self.speed
        )
        print('Spawning fruit at x:', self.x)
        print('Fruit fall speed:', abs(self.speed))
        print('')
    
    def nextFruit(self):
        Sprite.reset(
            self,
            y = fieldHeight,
            x = random.randint(0, orthoWidth),
            vY = self.vY * 1.05
        )
        print('Spawning fruit at x:', self.x)
        print('Fruit fall speed:', abs(self.vY))
        print('')
    
    def predict (self):
        Sprite.predict(self)
        if self.y < 0:
            if self.game.scoreboard.lives != 0:
                print('Fruit fell, resetting fall speed')
                self.game.failed()
            elif self.game.scoreboard.lives == 0:
                print('Game Over!')
                self.game.gameOver()
        

class Scoreboard (Attribute):
    controlsShift = 25
    scoreShift = 55
    livesShift = 85
    
    def install (self):
        def defineLabel (text, x, y):
            return pyglet.text.Label(
                text,
                font_name = 'Arial', font_size = 24,
                x = x, y = y,
                anchor_x = 'center', anchor_y = 'center',
                batch = self.game.batch
            )
        
        defineLabel ('Left: A, Right: D', 1 * orthoWidth // 2, fieldHeight + self.controlsShift)
        defineLabel ('Score: ', 1 * orthoWidth // 3, fieldHeight + self.scoreShift)
        defineLabel ('Lives: ', 1 * orthoWidth // 3, fieldHeight + self.livesShift)
            
        self.scoreLabel = (defineLabel ('000', 2 * orthoWidth // 3, fieldHeight + self.scoreShift))
        self.livesLabel = (defineLabel ('000', 2 * orthoWidth // 3, fieldHeight + self.livesShift))
            
        self.game.batch.add (2, GL_LINES, None, ('v2i', (0, fieldHeight, orthoWidth, fieldHeight)))

    def decrement (self):
        self.lives -= 1

    def increment (self):
        self.score += 1
        
    def reset (self):
        self.score = 0
        self.lives = 2
        Attribute.reset(self)
        
    def commit (self):
        self.scoreLabel.text = '{}'.format (self.score)
        self.livesLabel.text = '{}'.format (self.lives)
        
class Game:
    def __init__ (self):
        self.batch = pyglet.graphics.Batch()
        
        self.deltaT = 0
        self.pause = True
        
        self.attributes = []
        self.basket = Basket (self)
        self.fruit = Fruit (self)
        self.scoreboard = Scoreboard (self)
        
        self.window = pyglet.window.Window (
            640, 480, resizable = True, visible = False, caption = "Catch the fruit"
        )
        
        self.keymap = pyglet.window.key.KeyStateHandler()
        self.window.push_handlers (self.keymap)
        
        self.window.on_draw = self.draw
        self.window.on_resize = self.resize
        
        self.window.set_location(
            (self.window.screen.width - self.window.width) // 2,
            (self.window.screen.height - self.window.height) // 2
        )
        
        self.window.clear()
        self.window.flip()
        self.window.set_visible (True)
        pyglet.clock.schedule_interval(self.update, 1/60.)
        pyglet.app.run()
        
    def update (self, deltaT):
        self.deltaT = deltaT
        
        if self.pause:
            if self.keymap [pyglet.window.key.SPACE]:
                self.pause = False
            elif self.keymap [pyglet.window.key.ENTER]:
                self.scoreboard.reset()
            elif self.keymap [pyglet.window.key.ESCAPE]:
                self.exit()
        
        else:
            for attribute in self.attributes:
                attribute.predict()
            
            for attribute in self.attributes:
                attribute.interact()
                
            for attribute in self.attributes:
                attribute.commit()
    
    def succeeded(self):
        self.scoreboard.increment()
        self.fruit.nextFruit()
    
    def failed(self):
        self.scoreboard.decrement()
        self.fruit.reset()
    
    def gameOver(self):
        self.scoreboard.reset()
        self.basket.reset()
        self.fruit.reset()
        self.pause = True
    
    def draw (self):
        self.window.clear()
        self.batch.draw()
    
    def resize (self, width, height):
        glViewport (0, 0, width, height)
        
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity()
        glOrtho (0, orthoWidth, 0, orthoHeight, -1, 1)
        
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        
        return pyglet.event.EVENT_HANDLED

game = Game()
