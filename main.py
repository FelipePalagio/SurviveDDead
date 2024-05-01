import string
import sys
from panda3d.core import AnimControl
from ursina import *
import third_person_controller
from third_person_controller import ThirdPersonController
from ursina.shaders import colored_lights_shader
from direct.actor.Actor import Actor
import time

app = Ursina()

random.seed(0)
Entity.default_shader = colored_lights_shader
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4))

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = ThirdPersonController(z=-10, color=color.orange, origin_y=-.5, speed=8, collider='box')
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2.8000001907348633, 1))
actor = Actor("alex/alex.glb")
actor.reparent_to(player)
actor.setH(180)
actor.setScale(2, 2, 2)

gun = Entity(model="cube", parent=player, position=(0, 20, 0), on_cooldown=False)
# gun.muzzle_flash = Entity(parent=player, world_scale=.5, position=(-.2, 3, 2), model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent
for i in range(16):
    Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1, 2),
           x=random.uniform(-8, 8),
           z=random.uniform(-8, 8) + 8,
           collider='box',
           scale_y=random.uniform(2, 3),
           color=color.hsv(0, 0, random.uniform(.9, 1))
           )


class TheCreator:
    global recast

    def __init__(self, aniname):
        self.aniname = aniname
        self.state = 0

    def anime_control(self):
        return actor.getAnimControl(self.aniname)

    def upper(self):
        if self.state < 10:
            if self.aniname == "shoot":
                self.state += 10
            else:
                self.state += .5
        self.effct_control()

    def downr(self):

        if self.state >= .5:
            if self.aniname == "shoot":
                self.state -= 1
            else:
                self.state -= .5
        self.effct_control()

    def effct_control(self):
        return actor.setControlEffect(self.aniname, self.state)


animation_data = []
for animation in actor.getAnimNames():
    animation_data.append(TheCreator(animation))

print(actor.getAnimNames())


def animate(x):
    for data in animation_data:
        actor.enableBlend()
        if x == data.aniname:
            data.upper()
            if data.anime_control().isPlaying():
                if not third_person_controller.aim_mode:
                    player.rotation_x = 0
                    player.y = 0
                if data.aniname == "walkleft":
                    player.speed = 1.8
                if data.aniname == "walkright":
                    player.speed = 1.8
                if data.aniname == "walk":
                    player.speed = 4
                if data.aniname == "back":
                    player.speed = 3.5
                if data.aniname == "gunback":
                    player.speed = 2
                if data.aniname == "aim":
                    if player.camera_pivot.rotation_x > 19:
                        player.camera_pivot.rotation_x = 20
                    if player.camera_pivot.rotation_x < 20:
                        player.rotation_x = player.camera_pivot.rotation_x
                if data.aniname == "run":
                    third_person_controller.aim_mode = False
                    player.speed = 8
                if data.aniname == "rungun":
                    player.speed = 6
                if data.aniname == "gunleft":
                    player.speed = 1.8
                if data.aniname == "gunright":
                    player.speed = 1.8
                if data.aniname == "gunwalk":
                    player.speed = 3.5

            else:
                data.anime_control().loop(data.anime_control())

        else:
            data.downr()


pistol = False
transition_to_aim = False
transition_to_rest = False


def update():
    global pistol
    global transition_to_aim
    global transition_to_rest
    if transition_to_aim:
        third_person_controller.aim_mode = True
        if third_person_controller.camera.x < .8:
            third_person_controller.camera.x += .1
        if third_person_controller.camera.y < 1:
            third_person_controller.camera.y += .1
        if third_person_controller.camera.z < -1.2:
            third_person_controller.camera.z += .1

    if transition_to_rest:
        third_person_controller.aim_mode = False
        if third_person_controller.camera.x > 0:
            third_person_controller.camera.x -= .1
        if third_person_controller.camera.y > .6:
            third_person_controller.camera.y -= .1
        if third_person_controller.camera.z > -3:
            third_person_controller.camera.z -= .1

    if pistol:
        if not held_keys["shift"]:
            if not held_keys["3"]:
                if not held_keys["w"]:
                    if not held_keys["s"]:
                        if not held_keys["d"]:
                            if not held_keys["a"]:
                                if not held_keys["left mouse"]:
                                    animate('aim')
        if held_keys['w']:
            if not held_keys["shift"]:
                animate("gunwalk")
            if held_keys["shift"]:
                animate("run")

        if held_keys['d']:
            animate("gunright")
        if held_keys['a']:
            animate("gunleft")
        if held_keys['s']:
            animate("gunback")
    if not pistol:
        if not held_keys["shift"]:
            if not held_keys["w"]:
                if not held_keys["s"]:
                    if not held_keys["d"]:
                        if not held_keys["a"]:
                            if not held_keys["left mouse"]:
                                animate('idle')

        if held_keys["w"]:
            if not held_keys["shift"]:
                animate("walk")
            if held_keys["shift"]:
                animate("run")
        if held_keys["a"]:
            animate("walkleft")
        if held_keys["s"]:
            animate("back")
        if held_keys["d"]:
            animate("walkright")

    if not held_keys['right mouse']:
        transition_to_aim = False
        transition_to_rest = True
        pistol = False

    if held_keys['right mouse']:
        transition_to_aim = True
        transition_to_rest = False
        pistol = True
        if held_keys['left mouse']:
            shoot()


def shoot():
    if not gun.on_cooldown:
        Audio('shoot.mp3')
        animate('shoot')
        gun.on_cooldown = True
        invoke(setattr, gun, 'on_cooldown', False, delay=.5)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)


from ursina.prefabs.health_bar import HealthBar


class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.light_gray,
                         collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self, ))
        # print(hit_info.entity)
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1


# Enemy()
#enemies = [Enemy(x=x*4) for x in range(4)]


def pause_input(key):
    if key == 'tab':  # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled


pause_handler = Entity(ignore_paused=True, input=pause_input)

sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
Sky()
app.run()
