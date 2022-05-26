import math
import pygame
from pygame.locals import *
from datetime import datetime
import subprocess
from playsound import playsound


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 768
FPS = 0

K_CONSTANT = 680*2
ANGLE = math.radians(45)
GANTRY_MASS = 0.309

# Setup window =========================================================================================================
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Squash Ball Launcher')
# END SETUP WINDOW######################################################################################################


# Setup Classes ========================================================================================================
INPUT_FONT = pygame.font.SysFont("Segoe UI", 20)


class InputBox:  # Get value by input.text
    def __init__(self, x, y, w, h, text='', COLOR_INACTIVE=Color('lightskyblue3'), COLOR_ACTIVE=Color('dodgerblue2')):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = COLOR_INACTIVE
        self.color_active = COLOR_ACTIVE
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = INPUT_FONT.render(text, True, Color(0, 0, 0))
        self.active = False

    def handle_event(self, event_in):
        if event_in.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event_in.pos):
                # clear the box if user right click
                if event_in.button == 3:
                    self.text = ''
                    self.active = True
                else:
                    # Toggle the active variable.
                    self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive

        if event_in.type == pygame.KEYDOWN:
            if self.active:
                if event_in.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                elif event_in.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event_in.key == pygame.K_DELETE:
                    self.text = ""
                else:
                    if len(self.text) >= 6:
                        pass
                    elif event_in.unicode in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                        self.text += event_in.unicode
                    elif event_in.unicode in (".", ",") and "." not in self.text:
                        self.text += "."
                # Re-render the text.
        self.txt_surface = INPUT_FONT.render(self.text, True, Color(0, 0, 0))

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen_in):
        # Blit the rect.
        pygame.draw.rect(screen_in, self.color, self.rect, 0, 5)
        # Blit the text.
        text_rect = self.txt_surface.get_rect(center=screen.get_rect().center)
        screen_in.blit(self.txt_surface, (
            self.rect.x + (self.rect.w - text_rect[2]) * 0.5, self.rect.y + (self.rect.h - text_rect[3]) * 0.5))


BUTTON_FONT = pygame.font.SysFont("Segoe UI Bold", 40)


class Button:
    def __init__(self, x, y, w, h, text='', COLOR=Color('lightskyblue3'), TEXT_COLOR=Color(0, 0, 0)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR
        self.text = text
        self.txt_surface = BUTTON_FONT.render(text, True, TEXT_COLOR)

    def handle_event(self, event_in):
        if event_in.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the button.
            if self.rect.collidepoint(event_in.pos):
                return True
        return False

    def draw(self, screen_in):
        # Blit the rect.
        pygame.draw.rect(screen_in, self.color, self.rect, 0, 20)
        # Blit the text.
        text_rect = self.txt_surface.get_rect(center=screen.get_rect().center)
        screen_in.blit(self.txt_surface, (
            self.rect.x + (self.rect.w - text_rect[2]) * 0.5, self.rect.y + (self.rect.h - text_rect[3]) * 0.5))


class Text:
    def __init__(self, x, y, text, size, screen_in, color=Color(0, 0, 0)):
        txt_surface = pygame.font.SysFont("Segoe UI", size).render(text, True, color)
        text_rect = txt_surface.get_rect(center=screen.get_rect().center)
        screen_in.blit(txt_surface, (x - text_rect[2] * 0.5, y - text_rect[3] * 0.5))


class Calculate:
    def __init__(self, gantry_mass, angle, k_constant):
        self.gantry_mass = gantry_mass
        self.angle = angle
        self.k_constant = k_constant

    def playground(self, retraction, Xi, Yi, Xf, Yf, stat, screen_in):
        print(
            f"\n[Playground] Parameters received: Mass {self.gantry_mass}, Angle {math.degrees(self.angle)}, K {self.k_constant}, X {retraction}, Xo {Xi}, Yo {Yi}, Xg {Xf}, Yg {Yf}")
        # Calculate velocity
        velocity_squared = (self.k_constant * retraction * retraction / self.gantry_mass) - (
                2 * 9.81 * retraction * math.sin(self.angle))
        if velocity_squared <= 0:
            print(f"Error detected: Velocity is negative, Please increase retraction.")
            error.Retraction()
            return
        elif Xf + Yf == 0 or Xf == 0:
            print(f"Error detected: Goal is at origin, Please change Goal.")
            error.Goal()
            return
        velocity = math.sqrt(velocity_squared)
        print("Velocity: " + str(velocity))

        # Calculate max height and distance
        maxheight = (0.5 / 9.81) * (velocity * velocity) * pow(math.sin(self.angle), 2) + Yi
        stat.height(maxheight)
        maxdistance = (2 / 9.81) * (velocity * velocity) * math.cos(self.angle) * math.sin(self.angle) - Xi
        stat.distance(maxdistance)

        # Check for successful landing
        slope = math.tan(self.angle) - (9.81 * Xf / pow(velocity * math.cos(self.angle), 2))
        if slope > 0.7:
            print(f"Error detected: Going to the moon, Please decrease retraction. Slope is {slope}")
            error.GoingToTheMoon()

        height_at_goal = (Xf + Xi) * math.tan(self.angle) - (
                (pow(Xf + Xi, 2) * 4.905) / pow(velocity * math.cos(self.angle), 2)) + Yi
        if maxdistance < Xf:
            stat.success("Failure")
        elif -0.1 < height_at_goal - Yf < 0.1:
            stat.success("Success")
        else:
            stat.success("Failure")
        print(f"Height at goal: {height_at_goal}")

        # Draw the trajectory and basket
        global balls
        meter2pixel = 600 / (Xf + Xi)
        Basket(656, 515 - (Yf - Yi) * meter2pixel)

        # Draw a normal line
        x = 0
        threshold = (maxdistance + Xi) / 10000
        while x < maxdistance + Xi and x < Xf + Xi:
            y = x * math.tan(self.angle) - ((x * x * 4.905) / pow(velocity * math.cos(self.angle), 2))
            pygame.draw.circle(screen_in, Color("dark grey"), (56 + x * meter2pixel, 515 - y * meter2pixel), 1, 0)
            x += threshold

        # Draw advanced dots
        x = 0
        threshold = (maxdistance + Xi) / 30
        while x < maxdistance + Xi and x < Xf + Xi:
            y = x * math.tan(self.angle) - ((x * x * 4.905) / pow(velocity * math.cos(self.angle), 2))
            balls.append(Ball(57 + x * meter2pixel, 515 - y * meter2pixel, x - Xi, y + Yi, 5))
            x += threshold

        # Draw the landing dot
        if height_at_goal > Yi:
            balls.append(
                Ball(57 + (Xf + Xi) * meter2pixel, 515 - (height_at_goal - Yi) * meter2pixel, Xf, height_at_goal, 5,
                     Color("dark green")))

    def solver(self, Xi, Yi, Xf, Yf, screen_in):
        print(
            f"\n[Solver] Parameters received: Mass {self.gantry_mass}, Angle {math.degrees(self.angle)}, K {self.k_constant}, Xo {Xi}, Yo {Yi}, Xg {Xf}, Yg {Yf}")

        # Check for error
        if (((Xi + Xf) * math.tan(self.angle) - (Yf - Yi)) * pow(math.cos(self.angle), 2)) == 0:
            print(f"Error detected: Unable to solve")
            error.Goal()
            return

        if Yf < Yi:
            print(f"Error detected: Goal is below origin, Please change Goal.")
            error.GoalBelowGround()
            return

        # Calculate velocity
        velocity_squared = (4.905 * pow(Xi + Xf, 2)) / (
                ((Xi + Xf) * math.tan(self.angle) - (Yf - Yi)) * pow(math.cos(self.angle), 2))

        if velocity_squared <= 0:
            print(f"Error detected: Impossible goal.")
            error.Goal()
            return

        velocity = math.sqrt(velocity_squared)
        print("Velocity: " + str(velocity))

        retraction = ((self.gantry_mass * 9.81 * math.sin(self.angle)) + math.sqrt(
            pow(self.gantry_mass * 9.81 * math.sin(self.angle), 2) + (
                    self.k_constant * self.gantry_mass * velocity * velocity))) / self.k_constant

        print("Retraction: " + str(retraction))
        input_retraction.text = str(f"{retraction:.3f}")

        if retraction > 1000:
            print(f"Error detected: Solving this results in a very large retraction.")
            error.Inputs()
            return

        error.Arrow(495, Color("dark green"))
        Text(357, 300, "Solved Successfully!", 60, screen_in, Color("Black"))
        Text(230, 495, "Press START to view result.", 30, screen_in, Color("Black"))
        playsound('Assets/success.mp3', 0)


class Stats:
    def __init__(self):
        self.max_height = 0
        self.max_distance = 0
        self.success_var = "N/A"
        self.draw()

    def draw(self):
        pygame.draw.rect(screen, (215, 211, 182), (470, 645, 150, 52.5), 0, 15)  # Max height
        screen.blit(pygame.font.SysFont("Segoe UI", 22).render(f"Max Height (m)", True, (255, 255, 255)), (475, 705))
        pygame.draw.rect(screen, (215, 211, 182), (670, 645, 150, 52.5), 0, 15)  # Max distance
        screen.blit(pygame.font.SysFont("Segoe UI", 22).render(f"Max Distance (m)", True, (255, 255, 255)), (667, 705))
        pygame.draw.rect(screen, (215, 211, 182), (870, 645, 150, 52.5), 0, 15)  # Success
        screen.blit(pygame.font.SysFont("Segoe UI", 22).render(f"Success", True, (255, 255, 255)), (910, 705))
        Text(545, 668, f"{self.max_height:.2f}", 40, screen)
        Text(745, 668, f"{self.max_distance:.2f}", 40, screen)
        Text(945, 668, self.success_var, 40, screen)

    def clear(self):
        self.max_height = 0
        self.max_distance = 0
        self.success_var = "N/A"
        self.draw()

    def height(self, height):
        self.max_height = height
        self.draw()

    def distance(self, distance):
        self.max_distance = distance
        self.draw()

    def success(self, success):
        self.success_var = success
        self.draw()


# temporary screen for ball position overlay
temp = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
temp = temp.convert_alpha()


class Ball:
    def __init__(self, x, y, x_pos, y_pos, radius, COLOR_INACTIVE=Color("blue"), COLOR_ACTIVE=Color("red")):
        self.rect = pygame.Rect(x, y, x, y)
        self.color_inactive = COLOR_INACTIVE
        self.color_active = COLOR_ACTIVE
        self.color = self.color_inactive
        self.radius = radius
        self.active = False
        self.x_pos = x_pos
        self.y_pos = y_pos

    def handle_event(self, event_in):
        if event_in.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the ball.
            mouse_x, mouse_y = event_in.pos
            sqx = (mouse_x - self.rect[0] - 340) ** 2
            sqy = (mouse_y - self.rect[1] - 25) ** 2
            if math.sqrt(sqx + sqy) < self.radius:
                self.active = not self.active
            else:
                self.active = False
                pygame.draw.rect(temp, (255, 255, 255, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))  # empty temp screen
            self.color = self.color_active if self.active else self.color_inactive

        pygame.draw.circle(graph, self.color, (self.rect.x, self.rect.y), self.radius, 0)
        if self.active:
            pygame.draw.rect(temp, (255, 255, 255, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))  # empty temp screen
            pygame.draw.rect(temp, (255, 205, 255), (self.rect.x + 290, self.rect.y - 10, 100, 23))
            Text(self.rect.x + 340, self.rect.y, f"({self.x_pos:.2f}, {self.y_pos:.2f})", 20, temp)


class Basket:
    def __init__(self, x, y):
        image = pygame.transform.scale(pygame.image.load(r'Assets/basket.png'), (216 * 0.15, 233 * 0.15))
        graph.blit(image, (x - 15, y))


class Error:
    def __init__(self, screen_in):
        self.screen = screen_in

    def Arrow(self, y, color=Color("red")):
        pygame.draw.polygon(self.screen, color, ((5, y), (50, y - 40), (50, y + 40)))

    def GoingToTheMoon(self):
        self.Arrow(135)
        Text(357, 25, "Warning:", 60, self.screen, Color("red"))
        image = pygame.transform.scale(pygame.image.load(r'Assets/Rocket.png'), (1771 * 0.2, 2116 * 0.2))
        image.set_alpha(128)
        self.screen.blit(image, (180, 83))
        playsound('Assets/error.mp3', 0)

    def Retraction(self):
        graphing.blankGraph()
        self.Arrow(135)
        Text(357, 250, "Error:", 60, self.screen, Color("red"))
        Text(357, 350, "Unable to solve,", 50, self.screen, Color("red"))
        Text(357, 400, "please increase retraction.", 50, self.screen, Color("red"))
        playsound('Assets/error.mp3', 0)

    def Goal(self):
        graphing.blankGraph()
        self.Arrow(405)
        Text(357, 250, "Error:", 60, self.screen, Color("red"))
        Text(357, 350, "The goal cannot be here.", 50, self.screen, Color("red"))
        Text(357, 420, "X Distance cannot be 0 and Y Distance cannot be too high.", 20, self.screen, Color("red"))
        playsound('Assets/error.mp3', 0)

    def GoalBelowGround(self):
        graphing.blankGraph()
        self.Arrow(405)
        Text(357, 250, "Error:", 60, self.screen, Color("red"))
        Text(357, 350, "The goal cannot be here.", 50, self.screen, Color("red"))
        Text(357, 420, "The goal is below the ground.", 30, self.screen, Color("red"))
        playsound('Assets/error.mp3', 0)

    def Inputs(self):
        self.Arrow(255)
        self.Arrow(405)
        Text(357, 250, "Error:", 60, self.screen, Color("red"))
        Text(357, 350, "Invalid Input(s)", 50, self.screen, Color("red"))
        playsound('Assets/error.mp3', 0)


class Save:
    def __init__(self, screen_in):
        pygame.draw.rect(screen_in, (48, 48, 48), (17, 490, 295, 180))
        pygame.draw.rect(screen_in, (30, 30, 30), (30, 500, 270, 160), 0, 10)
        Text(165, 525, f"K Constant: {K_CONSTANT} N/m", 20, screen_in, Color("white"))
        Text(165, 575, f"Angle: {math.degrees(ANGLE)}°", 20, screen_in, Color("white"))
        Text(165, 625, f"Gantry mass: {GANTRY_MASS} Kg", 20, screen_in, Color("white"))
        timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        pygame.image.save(screen_in, f"Exports/{timestamp}.png")
        subprocess.Popen(f'explorer "Exports\\{timestamp}.png"')


# END SETUP CLASSES#####################################################################################################

# Create home screen ===================================================================================================
home = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.draw.rect(home, (48, 48, 48), (15, 15, 300, 738), 0, 10)  # Surface, Color, Position-Size, Thickness, Radius
pygame.draw.rect(home, (48, 48, 48), (330, 15, 735, 738), 0, 10)
# pygame.draw.rect(home, (255, 255, 255), (340, 25, 715, 600), 0, 10)
home.blit(pygame.font.SysFont("Segoe UI Bold", 45).render("Squash Launcher", True, (255, 255, 255)), (37, 38))

home.blit(pygame.font.SysFont("Segoe UI Bold", 22).render(f"Leave empty to solve", True, (255, 255, 255)), (90, 110))
pygame.draw.rect(home, (160, 87, 186), (30, 135, 270, 52.5), 0, 10)  # retraction
home.blit(pygame.font.SysFont("Segoe UI", 22).render(f"Spring Retraction {' ' * 11} m", True, (255, 255, 255)),
          (37, 143))

home.blit(pygame.font.SysFont("Segoe UI Bold", 22).render(f"Launcher Settings", True, (255, 255, 255)), (100, 200))
pygame.draw.rect(home, (56, 134, 64), (30, 225, 270, 52.5), 0, 10)  # X offset
home.blit(pygame.font.SysFont("Segoe UI", 22).render(f"X Offset {' ' * 12} m", True, (255, 255, 255)), (75, 234))
pygame.draw.rect(home, (186, 87, 87), (30, 285, 270, 52.5), 0, 10)  # Y offset
home.blit(pygame.font.SysFont("Segoe UI", 22).render(f"Y Offset {' ' * 12} m", True, (255, 255, 255)), (75, 294))

home.blit(pygame.font.SysFont("Segoe UI Bold", 22).render(f"Goal Settings", True, (255, 255, 255)), (115, 350))
pygame.draw.rect(home, (89, 87, 186), (30, 375, 270, 52.5), 0, 10)  # X Distance
home.blit(pygame.font.SysFont("Segoe UI", 22).render(f"X Distance {' ' * 12} m", True, (255, 255, 255)), (65, 385))
pygame.draw.rect(home, (150, 151, 88), (30, 435, 270, 52.5), 0, 10)  # Y Distance
home.blit(pygame.font.SysFont("Segoe UI", 22).render(f"Y Distance {' ' * 12} m", True, (255, 255, 255)), (65, 445))

fibo = pygame.transform.scale(pygame.image.load(r'Assets/fibo.png'), (216 * 0.3, 233 * 0.3))
home.blit(fibo, (135, 675))

home.blit(pygame.font.SysFont("Segoe UI Bold", 40).render(f"Stats:", True, (255, 255, 255)), (350, 650))

# END HOME SCREEN#######################################################################################################

# Create about screen ==================================================================================================
about = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
Text(540, 50, "About this program", 70, about, Color("White"))
Text(540, 150, "Created by:", 30, about, Color("White"))
Text(540, 250, "A. Nopparuj 64340500034", 30, about, Color("White"))
Text(540, 300, "I. Pantawit 64340500042", 30, about, Color("White"))
Text(540, 350, "B. Sahakon 64340500052", 30, about, Color("White"))
Text(540, 400, "C. Punyawat 64340500067", 30, about, Color("White"))
Text(540, 450, "M. Aekasit 64340500075", 30, about, Color("White"))
Text(540, 550, "FRA142 & FRA163", 30, about, Color("White"))
# END ABOUT SCREEN######################################################################################################

# Create graph screen ==================================================================================================
graph = pygame.Surface((715, 600))


class Graphing:
    def __init__(self, graph_input):
        self.graph_input = graph_input

    def cleanGraph(self):
        pygame.draw.rect(self.graph_input, (48, 48, 48), (0, 0, 715, 600))
        pygame.draw.rect(self.graph_input, Color("White"), (0, 0, 715, 600), 0, 10)
        launcher = pygame.transform.scale(pygame.image.load(r'Assets/launcher.PNG'), (3507 * 0.06, 2480 * 0.06))
        self.graph_input.blit(launcher, (-40, 475))
        # the start is at (56, 517)
        pygame.draw.rect(self.graph_input, Color("black"), (56, 515, 610, 2))  # x axis
        pygame.draw.polygon(self.graph_input, Color("black"), ((666, 509), (666, 522), (676, 515)))
        pygame.draw.rect(self.graph_input, Color("black"), (56, 57, 2, 458))  # y axis
        pygame.draw.polygon(self.graph_input, Color("black"), ((50, 57), (63, 57), (56, 47)))
        for y in range(0, 455, 75):  # y axis labels (horizontal lines)
            pygame.draw.rect(self.graph_input, Color("black"), (56, 515 - y, 600, 1))
        for x in range(0, 610, 75):  # x axis labels (vertical lines)
            pygame.draw.rect(self.graph_input, Color("black"), (56 + x, 65, 1, 450))

    def blankGraph(self):
        self.graph_input.fill((48, 48, 48))
        pygame.draw.rect(self.graph_input, Color("White"), (0, 0, 715, 600), 0, 10)

    def labelAxis(self, Xi, Xf, Yi):
        for ii in range(1, 8 + 1):
            x = -Xi + (Xf + Xi) / 8 * ii
            Text(131 + 75 * (ii - 1), 530, str(round(x, 2)), 15, self.graph_input)
        for jj in range(1, 6 + 1):
            y = Yi + (Xf + Xi) / 8 * jj
            Text(35, 440 - 75 * (jj - 1), str(round(y, 2)), 15, self.graph_input)


# the ball is at (56+X, 515-Y)
# pygame.draw.circle(graph, Color("red"), (56 + 225, 515 - 150), 5, 0)
Text(360, 290, "Welcome", 100, graph)
for i in range(0, 315):
    pygame.draw.circle(graph, Color("red"), (56 + i, 515 - 100 * math.sin(i / 100)), 1, 0)
for i in range(315, 630):
    pygame.draw.circle(graph, Color("red"), (275 + (i * 0.3), 515 - 20 * math.sin((i - 315) / 100)), 1, 0)
# END GRAPH SCREEN######################################################################################################

# Create objects =======================================================================================================
input_retraction = InputBox(200, 145, 70, 30, "0.125", Color('white'))
input_xoffset = InputBox(156, 236, 70, 30, "0.15", Color('white'))
input_yoffset = InputBox(156, 296, 70, 30, "0.29", Color('white'))
input_xgoal = InputBox(170, 387, 70, 30, "2.5", Color('white'))
input_ygoal = InputBox(170, 447, 70, 30, "0.6", Color('white'))
input_boxes_home = [input_retraction, input_xoffset, input_yoffset, input_xgoal, input_ygoal]

button_start = Button(100, 500, 130, 40, "Start", Color(60, 138, 255), Color('White'))
button_reset = Button(100, 553, 130, 40, "Reset", Color(217, 65, 65), Color('White'))
button_about = Button(30, 620, 130, 40, "About", Color(217, 129, 65), Color('White'))
button_save = Button(170, 620, 130, 40, "Save", Color("dark green"), Color('White'))
buttons_home = [button_start, button_reset, button_about, button_save]

button_back = Button(475, 675, 130, 40, "Back", Color("dark green"), Color('White'))
buttons_about = [button_back]

stats = Stats()

calculate = Calculate(GANTRY_MASS, ANGLE, K_CONSTANT)

balls = []

graphing = Graphing(graph)
graphing.cleanGraph()

error = Error(graph)
# END OBJECTS###########################################################################################################

# Active surfaces [0 home, 1 about]
current_screen = 0

# Program loop
running = True
clock = pygame.time.Clock()
clock.tick(FPS)

while running:
    # Event handling
    events = pygame.event.get()
    for event in events:
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False

    # tick clock
    clock.tick(FPS)

    # Home screen logic ================================================================================================
    if current_screen == 0:
        screen.blit(home, (0, 0))
        screen.blit(graph, (340, 25))
        screen.blit(temp, (0, 0))
        stats.draw()

        # draw boxes and buttons
        for box in input_boxes_home:
            box.draw(screen)
        for button in buttons_home:
            button.draw(screen)

        # Handle events
        for event in events:
            for box in input_boxes_home:  # Handle InputBox events
                box.handle_event(event)
            for ball in balls:
                ball.handle_event(event)
            if button_about.handle_event(event):  # Handle About button events
                current_screen = 1
            if button_save.handle_event(event):  # Handle Save button events
                Save(screen)
            if button_reset.handle_event(event):  # Handle Reset button events
                input_retraction.text = "0.125"
                input_xoffset.text = "0.15"
                input_yoffset.text = "0.29"
                input_xgoal.text = "2.5"
                input_ygoal.text = "0.6"
                graphing.cleanGraph()
                stats.clear()
                balls = []
            if button_start.handle_event(
                    event) or event.type == KEYDOWN and event.key == K_RETURN:  # Handle Start button events
                balls = []  # clear balls
                graphing.blankGraph()  # clear graph
                try:  # Check for valid inputs
                    X_OFFSET = float(input_xoffset.text)
                    Y_OFFSET = float(input_yoffset.text)
                    X_DISTANCE = float(input_xgoal.text)
                    Y_DISTANCE = float(input_ygoal.text)
                except ValueError:
                    print("Error detected: Invalid input")
                    error.Inputs()
                    continue

                if input_retraction.text == "" or input_retraction.text == ".":  # Solver mode
                    stats.clear()
                    stats.success("Solver")
                    calculate.solver(X_OFFSET, Y_OFFSET, X_DISTANCE, Y_DISTANCE, graph)
                else:  # Playground mode
                    graphing.cleanGraph()
                    SPRING_RETRACTION = float(input_retraction.text)
                    graphing.labelAxis(X_OFFSET, X_DISTANCE, Y_OFFSET)
                    calculate.playground(SPRING_RETRACTION, X_OFFSET, Y_OFFSET, X_DISTANCE, Y_DISTANCE, stats, graph)


    # END HOME SCREEN###################################################################################################

    # About screen logic ===============================================================================================
    elif current_screen == 1:  # about
        screen.blit(about, (0, 0))

        # Handle events
        for event in events:
            if button_back.handle_event(event):
                current_screen = 0

        # draw buttons
        for button in buttons_about:
            button.draw(screen)
    # END ABOUT SCREEN##################################################################################################

    pygame.display.update()

# pygame.image.save(screen, "screenshot.png")
# playsound('Assets/shutdown.mp3')
pygame.quit()
