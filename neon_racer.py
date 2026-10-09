# =============================================================================
# CHISHTI BRO PYTHON NEON RACER - HIGH LEVEL PC EDITION
# Created by Chishti Bro Computer and Developers
# Pure Python + Pygame
# =============================================================================

import random
import sys
import threading
import time

import pygame

try:
    import pyttsx3
    VOICE_AVAILABLE = True
except Exception:
    pyttsx3 = None
    VOICE_AVAILABLE = False

WIDTH, HEIGHT = 1280, 720
FPS = 60
ROAD_LEFT, ROAD_RIGHT = 300, 980
LANES = 3
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) / LANES

PLAYER_W, PLAYER_H = 62, 112
TRAFFIC_W, TRAFFIC_H = 56, 102
BASE_SPEED, MAX_SPEED = 300.0, 900.0

BLACK = (3, 6, 12)
ROAD = (10, 16, 25)
WHITE = (240, 248, 255)
CYAN = (0, 225, 255)
BLUE = (35, 100, 255)
GOLD = (255, 195, 45)
RED = (255, 55, 70)
GREEN = (65, 255, 165)
PURPLE = (175, 75, 255)

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHISHTI BRO PYTHON NEON RACER - HIGH LEVEL")
clock = pygame.time.Clock()

F_HUGE = pygame.font.SysFont("arial", 54, True)
F_XL = pygame.font.SysFont("arial", 42, True)
F_L = pygame.font.SysFont("arial", 29, True)
F_M = pygame.font.SysFont("arial", 20, True)
F_S = pygame.font.SysFont("arial", 15, True)
F_XS = pygame.font.SysFont("arial", 12, True)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lane_x(lane):
    return int(ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH / 2)


def text(surface, value, font, color, pos, center=False):
    img = font.render(value, True, color)
    rect = img.get_rect()
    rect.center = pos if center else rect.center
    if not center:
        rect.topleft = pos
    surface.blit(img, rect)


def rr(surface, color, rect, radius=8, width=0):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def glow(surface, rect, color, strength=12):
    for i in range(strength, 0, -2):
        layer = pygame.Surface(
            (rect.width + i * 2, rect.height + i * 2), pygame.SRCALPHA
        )
        pygame.draw.rect(
            layer, (*color, max(5, 45 - i * 2)),
            layer.get_rect(), 2, border_radius=max(5, rect.height // 5)
        )
        surface.blit(layer, (rect.x - i, rect.y - i))


class Voice:
    def __init__(self):
        self.enabled = VOICE_AVAILABLE
        self.lock = threading.Lock()
        self.last = ""
        self.last_at = 0.0

    def say(self, phrase):
        if not self.enabled:
            return
        now = time.time()
        if phrase == self.last and now - self.last_at < 0.8:
            return
        self.last, self.last_at = phrase, now
        threading.Thread(target=self._run, args=(phrase,), daemon=True).start()

    def _run(self, phrase):
        try:
            with self.lock:
                e = pyttsx3.init()
                e.setProperty("rate", 175)
                e.setProperty("volume", 0.9)
                e.say(phrase)
                e.runAndWait()
                e.stop()
        except Exception:
            pass


voice = Voice()


class Particle:
    def __init__(self, x, y, color, vx, vy, life, size):
        self.x, self.y = x, y
        self.color = color
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        q = self.life / self.max_life
        r = max(1, int(self.size * q))
        layer = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*self.color, int(220 * q)), (r * 2, r * 2), r)
        surface.blit(layer, (int(self.x - r * 2), int(self.y - r * 2)))


def draw_car(surface, cx, cy, color, player=False):
    w, h = (PLAYER_W, PLAYER_H) if player else (TRAFFIC_W, TRAFFIC_H)
    x, y = int(cx - w / 2), int(cy - h / 2)

    if player:
        aura = pygame.Surface((w + 90, h + 90), pygame.SRCALPHA)
        pygame.draw.ellipse(aura, (*CYAN, 42), aura.get_rect())
        surface.blit(aura, (x - 45, y - 45))

    pygame.draw.ellipse(surface, (0, 0, 0, 150), (x - 10, y + h - 7, w + 20, 18))
    body = pygame.Rect(x, y, w, h)
    rr(surface, (3, 8, 16), body, 12)
    rr(surface, color, body.inflate(-6, -6), 10)

    cabin = pygame.Rect(x + int(w*.19), y + int(h*.19), int(w*.62), int(h*.36))
    rr(surface, (7, 19, 33), cabin, 8)
    rr(surface, (20, 72, 108), cabin.inflate(-5, -5), 6)

    pygame.draw.line(
        surface, tuple(min(255, c + 60) for c in color),
        (cx, y + 10), (cx, y + h - 12), 2
    )

    lw, lh = max(6, int(w*.17)), max(4, int(h*.055))
    for lx in (x + 7, x + w - 7 - lw):
        rr(surface, (205, 245, 255), pygame.Rect(lx, y + int(h*.08), lw, lh), 3)
        rr(surface, RED, pygame.Rect(lx, y + int(h*.86), lw, lh), 3)

    ww, wh = max(6, int(w*.12)), max(16, int(h*.18))
    for wy in (y + int(h*.26), y + int(h*.65)):
        rr(surface, (1, 3, 7), pygame.Rect(x - ww//2, wy, ww, wh), 3)
        rr(surface, (1, 3, 7), pygame.Rect(x + w - ww//2, wy, ww, wh), 3)

    if player:
        pygame.draw.line(surface, CYAN, (x + 10, y + h - 5), (x + w - 10, y + h - 5), 3)


class Traffic:
    COLORS = [(245,55,55),(255,120,30),(175,65,255),(255,210,55),(55,230,160),(235,235,245)]

    def __init__(self, lane):
        self.lane = lane
        self.x = lane_x(lane)
        self.y = -random.randint(100, 330)
        self.factor = random.uniform(.70, .96)
        self.color = random.choice(self.COLORS)
        self.passed = False

    def update(self, dt, speed):
        self.y += speed * self.factor * dt

    def rect(self):
        return pygame.Rect(
            int(self.x - TRAFFIC_W/2 + 8),
            int(self.y - TRAFFIC_H/2 + 9),
            TRAFFIC_W - 16, TRAFFIC_H - 18
        )

    def draw(self, surface):
        draw_car(surface, self.x, self.y, self.color)


class BoostPad:
    def __init__(self, lane):
        self.x = lane_x(lane)
        self.y = -120

    @property
    def rect(self):
        return pygame.Rect(self.x - 34, int(self.y - 60), 68, 120)

    def update(self, dt, speed):
        self.y += speed * dt

    def draw(self, surface):
        r = self.rect
        glow(surface, r, GOLD, 9)
        rr(surface, (80,52,8), r, 8)
        for yy in range(r.top+14, r.bottom-8, 27):
            pygame.draw.polygon(surface, GOLD, [
                (self.x, yy), (self.x-18, yy+15), (self.x-8, yy+15),
                (self.x, yy+7), (self.x+8, yy+15), (self.x+18, yy+15)
            ])


class Game:
    def __init__(self):
        self.fullscreen = False
        self.reset(True)

    def reset(self, first=False):
        self.player_lane = 1
        self.player_x = float(lane_x(1))
        self.player_y = HEIGHT - 135
        self.score = 0.0
        self.distance = 0.0
        self.speed = BASE_SPEED
        self.traffic, self.boosts, self.particles = [], [], []
        self.spawn_timer, self.boost_timer = .4, 2.8
        self.road_offset = 0.0
        self.nitro, self.boost_time = 100.0, 0.0
        self.combo, self.combo_timer = 0, 0.0
        self.paused = self.crashed = False
        self.message, self.message_timer = "", 0.0
        self.shake, self.flash = 0.0, 0.0
        self.high_score = self.load_high_score()
        if first:
            voice.say("Chishti Bro Neon Racer. Get ready.")

    def load_high_score(self):
        try:
            return int(open("neon_racer_highscore.txt", encoding="utf-8").read())
        except Exception:
            return 0

    def save_high_score(self):
        try:
            with open("neon_racer_highscore.txt", "w", encoding="utf-8") as f:
                f.write(str(max(self.high_score, int(self.score))))
        except Exception:
            pass

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if self.fullscreen else pygame.display.set_mode((WIDTH, HEIGHT))

    def move(self, direction):
        if self.crashed or self.paused:
            return
        new_lane = int(clamp(self.player_lane + direction, 0, LANES-1))
        if new_lane != self.player_lane:
            self.player_lane = new_lane
            self.message, self.message_timer = "LANE SHIFT", .35
            for _ in range(6):
                self.particles.append(Particle(
                    self.player_x, self.player_y+40, CYAN,
                    random.uniform(-40,40), random.uniform(40,130), .35, random.uniform(2,4)
                ))

    def boost(self, manual=True):
        if self.crashed or self.paused:
            return
        if self.nitro <= 2:
            if manual:
                self.message, self.message_timer = "NITRO EMPTY", .7
                voice.say("Nitro empty.")
            return
        self.boost_time = max(self.boost_time, .65)
        self.nitro = max(0, self.nitro - (12 if manual else 4))
        self.message, self.message_timer = "BOOST x2", .7
        self.add_particles(self.player_x, self.player_y+48, GOLD, 15)
        voice.say("Boost.")

    def add_particles(self, x, y, color, amount):
        for _ in range(amount):
            self.particles.append(Particle(
                x + random.uniform(-18,18), y + random.uniform(-8,12), color,
                random.uniform(-80,80), random.uniform(40,190),
                random.uniform(.25,.75), random.uniform(2,6)
            ))

    def player_rect(self):
        return pygame.Rect(
            int(self.player_x-PLAYER_W/2+8),
            int(self.player_y-PLAYER_H/2+10),
            PLAYER_W-16, PLAYER_H-20
        )

    def crash(self):
        self.crashed = True
        self.shake, self.flash = 1.0, .8
        self.message, self.message_timer = "CRASH!", 2
        self.add_particles(self.player_x, self.player_y, RED, 55)
        self.save_high_score()
        voice.say("Crash. Game over.")

    def update(self, dt):
        if self.paused:
            return
        if self.crashed:
            for p in self.particles: p.update(dt)
            self.particles[:] = [p for p in self.particles if p.life > 0]
            self.shake = max(0, self.shake-dt*1.5)
            self.flash = max(0, self.flash-dt)
            return

        difficulty = clamp(self.distance/9000, 0, 1)
        target = min(MAX_SPEED, BASE_SPEED + self.distance*.025)
        if self.boost_time > 0:
            self.boost_time -= dt
            target *= 1.55
        self.speed += (target-self.speed)*min(1,dt*3)
        self.distance += self.speed*dt
        self.score += (self.speed/60)*dt

        if self.boost_time <= 0:
            self.nitro = min(100, self.nitro + dt*4)

        self.road_offset = (self.road_offset + self.speed*dt) % 90
        self.player_x += (lane_x(self.player_lane)-self.player_x)*min(1,dt*13)

        self.spawn_timer -= dt
        self.boost_timer -= dt
        self.combo_timer -= dt
        self.message_timer -= dt
        self.shake = max(0,self.shake-dt*3)
        self.flash = max(0,self.flash-dt)

        if self.spawn_timer <= 0:
            lanes = list(range(LANES)); random.shuffle(lanes)
            amount = 2 if self.distance > 1800 and random.random() < .25 else 1
            used = 0
            for lane in lanes:
                if any(c.lane == lane and c.y < 180 for c in self.traffic):
                    continue
                self.traffic.append(Traffic(lane)); used += 1
                if used >= amount: break
            self.spawn_timer = random.uniform(.55-.15*difficulty,.95-.18*difficulty)

        if self.boost_timer <= 0:
            self.boosts.append(BoostPad(random.randrange(LANES)))
            self.boost_timer = random.uniform(3,5.5)

        if self.combo_timer <= 0:
            self.combo = 0

        pr = self.player_rect()

        for car in self.traffic:
            car.update(dt,self.speed)
            if pr.colliderect(car.rect()):
                self.crash(); return
            if not car.passed and car.y > self.player_y+25:
                car.passed = True
                if abs(car.x-self.player_x) < 110:
                    self.combo += 1
                    self.combo_timer = 1.7
                    mult = min(5,1+self.combo//2)
                    self.score += 80*mult
                    self.message, self.message_timer = f"CLEAN PASS x{mult}", .9
                    self.add_particles(self.player_x,self.player_y-45,CYAN,8)
                    voice.say("Clean pass.")

        self.traffic[:] = [c for c in self.traffic if c.y < HEIGHT+160]

        for pad in self.boosts:
            pad.update(dt,self.speed)
            if pad.rect.colliderect(pr):
                self.boost_time = max(self.boost_time,1.4)
                self.nitro = min(100,self.nitro+35)
                self.score += 150
                self.message, self.message_timer = "BOOST PAD x2", .9
                self.add_particles(self.player_x,self.player_y+45,GOLD,18)
                voice.say("Boost pad.")
        self.boosts[:] = [b for b in self.boosts if b.y < HEIGHT+160]

        if self.boost_time > 0:
            self.add_particles(self.player_x,self.player_y+52,CYAN,1)

        for p in self.particles: p.update(dt)
        self.particles[:] = [p for p in self.particles if p.life > 0]

        if int(self.score) > self.high_score:
            self.high_score = int(self.score)
            self.save_high_score()

    def background(self, s):
        s.fill(BLACK)
        for i in range(10):
            layer=pygame.Surface((WIDTH,100),pygame.SRCALPHA)
            pygame.draw.rect(layer,(0,110,255,max(0,32-i*3)),layer.get_rect())
            s.blit(layer,(0,i*6))
        pygame.draw.rect(s,ROAD,(ROAD_LEFT,0,ROAD_RIGHT-ROAD_LEFT,HEIGHT))
        for y in range(0,HEIGHT,20):
            c=12+int(7*y/HEIGHT)
            pygame.draw.line(s,(c,c+5,c+11),(ROAD_LEFT,y),(ROAD_RIGHT,y),1)

        pygame.draw.line(s,CYAN,(ROAD_LEFT,0),(ROAD_LEFT,HEIGHT),4)
        pygame.draw.line(s,CYAN,(ROAD_RIGHT,0),(ROAD_RIGHT,HEIGHT),4)
        pygame.draw.line(s,GOLD,(ROAD_LEFT+9,0),(ROAD_LEFT+9,HEIGHT),2)
        pygame.draw.line(s,GOLD,(ROAD_RIGHT-9,0),(ROAD_RIGHT-9,HEIGHT),2)

        for lane in range(1,LANES):
            x=int(ROAD_LEFT+LANE_WIDTH*lane)
            y=-90+self.road_offset
            while y<HEIGHT:
                pygame.draw.line(s,(205,225,245),(x,int(y)),(x,int(y+42)),5)
                y+=90

        for y in range(-80,HEIGHT+100,95):
            yy=int(y+self.road_offset*.5)
            for side in (-1,1):
                x=ROAD_LEFT-50 if side<0 else ROAD_RIGHT+28
                col=CYAN if (y//95)%2==0 else GOLD
                pygame.draw.rect(s,col,(x,yy,14,35),border_radius=4)

    def hud(self,s):
        panel=pygame.Surface((WIDTH,96),pygame.SRCALPHA)
        pygame.draw.rect(panel,(2,7,15,225),panel.get_rect())
        s.blit(panel,(0,0))
        text(s,"CHISHTI BRO",F_M,WHITE,(22,12))
        text(s,"NEON RACER",F_M,CYAN,(22,42))
        text(s,"CODE • BOOST • SURVIVE",F_XS,(155,180,205),(22,70))
        text(s,f"SCORE  {int(self.score):07d}",F_M,WHITE,(WIDTH-285,13))
        text(s,f"SPEED  {int(self.speed)}",F_S,CYAN,(WIDTH-175,51))

        bx,by,bw,bh=WIDTH//2-140,18,280,14
        rr(s,(28,38,55),pygame.Rect(bx,by,bw,bh),7)
        rr(s,GOLD if self.nitro>25 else RED,pygame.Rect(bx,by,int(bw*self.nitro/100),bh),7)
        text(s,f"NITRO {int(self.nitro)}%",F_XS,WHITE,(WIDTH//2,50),True)
        if self.boost_time>0:
            text(s,"BOOST x2",F_L,GOLD,(WIDTH//2,75),True)

    def draw(self,s):
        self.background(s)
        for b in self.boosts: b.draw(s)
        for c in self.traffic: c.draw(s)
        for p in self.particles: p.draw(s)
        draw_car(s,self.player_x,self.player_y,BLUE,True)
        self.hud(s)

        if self.message_timer>0:
            text(s,self.message,F_XL,WHITE,(WIDTH//2,145),True)

        # Footer requested by the owner.
        footer_y=HEIGHT-28
        f=pygame.Surface((WIDTH,28),pygame.SRCALPHA)
        pygame.draw.rect(f,(2,5,10,235),f.get_rect())
        s.blit(f,(0,footer_y))
        text(s,"Created by Chishti Bro Computer and Developers",F_XS,
             (175,205,225),(WIDTH//2,footer_y+7),True)

        if self.paused:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,165)); s.blit(ov,(0,0))
            text(s,"PAUSED",F_HUGE,CYAN,(WIDTH//2,HEIGHT//2-45),True)
            text(s,"Press P to continue",F_M,WHITE,(WIDTH//2,HEIGHT//2+20),True)

        if self.crashed:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,180)); s.blit(ov,(0,0))
            text(s,"GAME OVER",F_HUGE,RED,(WIDTH//2,HEIGHT//2-105),True)
            text(s,f"SCORE  {int(self.score):07d}",F_L,WHITE,(WIDTH//2,HEIGHT//2-45),True)
            text(s,f"BEST  {self.high_score:07d}",F_M,GOLD,(WIDTH//2,HEIGHT//2),True)
            text(s,"Press R to race again",F_M,CYAN,(WIDTH//2,HEIGHT//2+55),True)
            text(s,"F11 Fullscreen  •  ESC Quit",F_S,(185,205,225),(WIDTH//2,HEIGHT//2+95),True)

        if self.flash>0:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            ov.fill((255,30,45,int(120*self.flash))); s.blit(ov,(0,0))


def main():
    game=Game()
    running=True

    while running:
        dt=min(clock.tick(FPS)/1000,.035)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_F11:
                    game.toggle_fullscreen()
                elif event.key in (pygame.K_LEFT,pygame.K_a):
                    game.move(-1)
                elif event.key in (pygame.K_RIGHT,pygame.K_d):
                    game.move(1)
                elif event.key==pygame.K_SPACE:
                    game.boost(True)
                elif event.key==pygame.K_p and not game.crashed:
                    game.paused=not game.paused
                    voice.say("Game paused." if game.paused else "Game resumed.")
                elif event.key==pygame.K_r and game.crashed:
                    game.reset(); voice.say("Race restarted.")
                elif event.key==pygame.K_ESCAPE:
                    running=False

        keys=pygame.key.get_pressed()
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not game.crashed and not game.paused:
            game.boost(True)

        game.update(dt)

        if game.shake>0:
            canvas=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            game.draw(canvas)
            screen.fill(BLACK)
            screen.blit(canvas,(random.randint(-8,8),random.randint(-5,5)))
        else:
            game.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__=="__main__":
    main()
