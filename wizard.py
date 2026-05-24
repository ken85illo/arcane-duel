from animation import Animation


class Wizard:
    STATES = ("idle", "walking", "casting")

    def __init__(
        self, color: str, frame_duration_ms: int, img_scale: float = 100.0
    ):
        if color not in ("blue", "red"):
            raise ValueError("Wizard color must be 'blue' or 'red'")
        self.color = color
        self.img_scale = img_scale
        self.frame_duration_ms = frame_duration_ms

        self.animations = {}
        for state in self.STATES:
            folder = f"wizard_{color}"
            frame_paths = [
                f"assets/{folder}/{self._state_prefix(state)}_000.png",
                f"assets/{folder}/{self._state_prefix(state)}_001.png",
                f"assets/{folder}/{self._state_prefix(state)}_002.png",
                f"assets/{folder}/{self._state_prefix(state)}_003.png",
                f"assets/{folder}/{self._state_prefix(state)}_004.png",
            ]
            # By default, only idle and walking repeat, casting does not
            repeat = state not in ("casting", "walking")
            self.animations[state] = Animation(
                frame_paths, img_scale, frame_duration_ms, repeat=repeat
            )
        self.state = "idle"

    def _state_prefix(self, state):
        return {"idle": "1_IDLE", "walking": "4_JUMP", "casting": "5_ATTACK"}[
            state
        ]

    def set_state(self, state: str):
        if state not in self.STATES:
            raise ValueError(f"Invalid state: {state}")
        if self.state != state:
            self.state = state
            self.animations[state].reset()

    def update(self):
        self.animations[self.state].update()

    def get_current_frame(self):
        return self.animations[self.state].get_current_frame()
