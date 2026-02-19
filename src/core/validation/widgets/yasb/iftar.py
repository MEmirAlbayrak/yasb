from typing import Literal

from pydantic import Field

from core.validation.widgets.base_model import (
    AnimationConfig,
    CallbacksConfig,
    CustomBaseModel,
    KeybindingConfig,
    PaddingConfig,
    ShadowConfig,
)


class IftarCallbacksConfig(CallbacksConfig):
    on_left: str = "toggle_label"
    on_right: str = "do_nothing"
    on_middle: str = "do_nothing"


class IftarConfig(CustomBaseModel):
    label: str = "<span>\uf017</span> Iftar: {iftar_time}"
    label_alt: str = "<span>\uf017</span> Sahur: {sahur_time} | Iftar: {iftar_time} | Remaining: {remaining}"
    class_name: str = ""
    city: str = "Istanbul"
    country: str = "Turkey"
    calculation_method: int = Field(default=13, ge=0, le=23)
    time_format: Literal["12h", "24h"] = "24h"
    update_interval: int = Field(default=3600, ge=60, le=86400)
    tooltip: bool = True
    animation: AnimationConfig = AnimationConfig()
    container_padding: PaddingConfig = PaddingConfig()
    label_shadow: ShadowConfig = ShadowConfig()
    container_shadow: ShadowConfig = ShadowConfig()
    keybindings: list[KeybindingConfig] = []
    callbacks: IftarCallbacksConfig = IftarCallbacksConfig()
