import math
import pygame

WIDTH, HEIGHT = 800, 800
SIZE_SCALE = 10e9/149597e6
pygame.init()
DIST = pygame.font.SysFont("comicsans", 16)
NAME = pygame.font.SysFont("comicsans", 14)

class Vector2D:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        self.x + other.x
        self.y + other.y

    def mul(self, other):
        self.x * other.x
        self.y * other.y

    def __mul__(self, scalar):
        self.x * scalar
        self.y * scalar

class _StarDefaultsBase:
    AU =  149597e6
    G = 6.67428e-11
    x_vel = 0
    y_vel = 0
    distance_to_sun = 0

class Body(_StarDefaultsBase):
    def __init__(self, name, x, y, radius, colour, mass, sun=False):
        self.name = name
        self.orbit = []
        self.x = x
        self.y = y
        self.original_radius = radius
        self.radius = radius
        self.colour = colour
        self.mass = mass
        self.sun = sun

    def draw(self, win, cam_pos, scale):
        """Draw planets and lines"""
        x = self.x * scale + WIDTH / 2
        y = self.y * scale + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * scale + WIDTH / 2 + cam_pos[0]
                y = y * scale + HEIGHT / 2 + cam_pos[1]
                updated_points.append((x, y))
            pygame.draw.lines(win, self.colour, False, updated_points, 2)

        pygame.draw.circle(win, self.colour, (x, y), self.radius)
        if not self.sun:
            distance_text = DIST.render(f"{round(self.distance_to_sun/1e6, 1)}Mm", 1, (255,255,255))
            win.blit(distance_text, (x-distance_text.get_width()/2, y-2*distance_text.get_height()))
        name_text = NAME.render(self.name, 1, (255,255,255))
        win.blit(name_text, (x-name_text.get_width()/2, y-2*name_text.get_height()/2))

    def attraction(self, other) -> tuple:
        """Calculate orbital mechanics"""
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        if other.sun:
            self.distance_to_sun = distance

        force = self.G * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets, time_step):
        """
        takes the total net acceleration along the x and y axis, multiplies
        it by the timestep to get the velocity and adds that velocity to the
        current velocity. Upon doing so, updates the position based on the
        time step.
        """
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx * time_step
        self.y_vel += total_fy * time_step

        self.x += self.x_vel * time_step
        self.y += self.y_vel * time_step
        self.orbit.append((self.x, self.y))
        if not self.sun and len(self.orbit) > (self.distance_to_sun  * 100 * (21600/time_step) /(0.387 * self.AU)):
            self.orbit.pop(0)

class Game:
    def __init__(self, width, height, caption) -> None:
        self.win = pygame.display.set_mode((width, height))
        self.run = True
        self.bg = (255, 255, 255)
        self.bodies = []
        self.cam_pos = [0, 0]
        self.cam_speed = 50
        pygame.display.set_caption(caption)
        self.scale = (250) / Body.AU
        self.scale_speed = 50 / Body.AU
        self.timestep_selector = 2
        self.timesteps = [1, 60, 3600, 3600*6, 3600*12, 86400, 86400*2]
        self.timestep = self.timesteps[self.timestep_selector]
        self.camera_track = False
        self.planet_selector = 3

    def start(self) -> None:
        """Starts the game loop"""
        clock = pygame.time.Clock()
        while self.run:
            clock.tick(30)
            self.win.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                pygame.key.set_repeat(15)
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.cam_pos[1] += self.cam_speed
                if pygame.key.get_pressed()[pygame.K_DOWN]:
                    self.cam_pos[1] -= self.cam_speed
                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.cam_pos[0] += self.cam_speed
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    self.cam_pos[0] -= self.cam_speed

                pygame.key.set_repeat(25)
                if pygame.key.get_pressed()[pygame.K_z]:
                    self.scale *= 1.2
                    self.cam_pos[0] = self.cam_pos[0]*1.2
                    self.cam_pos[1] = self.cam_pos[1]*1.2
                    for body in self.bodies:
                        body.radius *= 1.2
                if pygame.key.get_pressed()[pygame.K_x]:
                    self.scale /= 1.2
                    self.cam_pos[0] /= 1.2
                    self.cam_pos[1] /= 1.2
                    for body in self.bodies:
                        body.radius/=1.2

                pygame.key.set_repeat(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.planet_selector = (self.planet_selector+1) % len(self.bodies)
                        print(self.planet_selector)
                    if event.key == pygame.K_f:
                        self.camera_track = not self.camera_track
                        print("Camera track")
                        print(self.camera_track)
                    if event.key == pygame.K_c:
                        self.timestep_selector = max(0, self.timestep_selector-1)
                        self.timestep = self.timesteps[self.timestep_selector]
                    if event.key == pygame.K_v:
                        self.timestep_selector = min(len(self.timesteps)-1, self.timestep_selector+1)
                        self.timestep = self.timesteps[self.timestep_selector]
                    if event.key == pygame.K_r:
                        self.camera_track = False
                        self.cam_pos = [0, 0]
                        self.scale = 250 / Body.AU
                        for body in self.bodies:
                            body.radius = body.original_radius
                    if event.key == pygame.K_a:
                        for i in self.bodies:
                            i.G *= 2
                    if event.key == pygame.K_s:
                        for i in self.bodies:
                            i.G /= 2

            for body in self.bodies:
                body.update_position(self.bodies, self.timestep)
                body.draw(self.win, self.cam_pos, self.scale)
            if self.camera_track:
                body = self.bodies[self.planet_selector]
                self.cam_pos = [-body.x * self.scale-body.x_vel*self.scale*self.timestep,
                                -body.y * self.scale-body.y_vel*self.scale*self.timestep]
            c_text1 = DIST.render(f"Up/Down/Left/Right: moves camera   Z/X: Zooms in/out   R: Reset View", 1, (255,255,255))
            c_text2 = DIST.render(f"C/V: speeds time up/down   F: locks onto planet,   G: switches planet", 1, (255,255,255))
            self.win.blit(c_text1, (0, HEIGHT-c_text1.get_height()*2))
            self.win.blit(c_text2, (0, HEIGHT-c_text2.get_height()))
            time_text = DIST.render(f"{self.timesteps[self.timestep_selector]/60:.2f} minutes a second", 1, (255,255,255))
            self.win.blit(time_text, (WIDTH-time_text.get_width(), HEIGHT-time_text.get_height()))
            pygame.display.update()

        pygame.quit()

    def add_bodies(self, planets) -> None:
        """Adds a list of planets to the planet list"""
        self.bodies.extend(planets)

def main() -> None:
    OrbitGame = Game(800, 800, "Planet Simulation")

    YELLOW = (255, 255, 0)
    MERCURY = (117, 116, 112)
    VENUS = (196, 152, 107)
    EARTH = (50, 50, 74)
    MARS = (166, 29, 19)
    JUPITER = (137, 84, 14)
    SATURN = (194, 184, 147)
    URANUS = (184, 204, 206)
    NEPTUNE = (43, 52, 191)
    PLUTO = (168, 161, 150)

    Sun = Body("Sol", 0, 0, SIZE_SCALE*30, YELLOW, 1.98892e30, True)
    Mercury = Body("Mercury", 0.387 * Body.AU, 0, SIZE_SCALE*0.383, MERCURY, 3.30e23)
    Venus = Body("Venus", 0.723 * Body.AU, 0, SIZE_SCALE*0.95, VENUS, 4.8685e24)
    Earth = Body("Earth", -1 * Body.AU, 0, SIZE_SCALE, EARTH, 5.9742e24)
    Mars = Body("Mars", -1.524 * Body.AU, SIZE_SCALE*0.532, 2.5, MARS, 6.39e23)
    Jupiter = Body("Jupiter", 5.4588 * Body.AU, 0, SIZE_SCALE*11.21, JUPITER, 1.8982e27)
    Saturn = Body("Saturn", 9.91*Body.AU, 0, SIZE_SCALE*9.45, SATURN, 5.68319e26)
    Uranus = Body("Uranus", 19.73*Body.AU, 0, SIZE_SCALE*4.01, URANUS, 86.811e25)
    Neptune = Body("Neptune", 29.97*Body.AU, 0, SIZE_SCALE*3.88, NEPTUNE, 102.409e24)
    Pluto = Body("Pluto", 48.49*Body.AU, 0, SIZE_SCALE*0.187, PLUTO, 0.01303e24)
    Moon = Body("Moon", -1*Body.AU, 405400e3, SIZE_SCALE*0.2724, PLUTO, 0.07346e24)
    Sun2 = Body("Sol", 0, 5*Body.AU, SIZE_SCALE*30, YELLOW, 1.98892e30, True)

    Mercury.y_vel = -47.4e3
    Venus.y_vel = -35.02e3
    Earth.y_vel = 29.783e3
    Moon.y_vel = 29.783e3
    Moon.x_vel = 0.970e3 * 1.25
    Mars.y_vel = 24.077e3
    Jupiter.y_vel = -12.6e3
    Saturn.y_vel = -9.09e3
    Uranus.y_vel = -7.11e3
    Neptune.y_vel = -5.50e3
    Pluto.y_vel = -3.71e3
    Sun2.x_vel = 20.6e3


    OrbitGame.add_bodies([Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn])
    OrbitGame.add_bodies([Uranus, Neptune, Pluto])
    OrbitGame.add_bodies([Moon])
    #uncommit this for extra fun
    # OrbitGame.add_bodies([Sun2])

    OrbitGame.start()


if __name__ == "__main__":
    main()