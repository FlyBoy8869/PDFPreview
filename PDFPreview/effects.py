from PySide6.QtWidgets import QGraphicsBlurEffect


def create_blur_effects(widgets: tuple) -> list[QGraphicsBlurEffect]:
    blur_effects = [QGraphicsBlurEffect(widget) for widget in widgets]
    disable_effects(blur_effects)
    return blur_effects


def disable_effects(effects: list[QGraphicsBlurEffect]) -> None:
    _toggle_effects(effects, False)


def enable_effects(effects: list[QGraphicsBlurEffect]) -> None:
    _toggle_effects(effects, True)


def set_blur_effects(widgets: tuple, blur_effects: list[QGraphicsBlurEffect], radius: int) -> None:
    for widget, effect in zip(widgets, blur_effects):
        effect.setBlurRadius(radius)
        widget.setGraphicsEffect(effect)


def _toggle_effects(effects: list[QGraphicsBlurEffect], enable: bool) -> None:
    for effect in effects:
        effect.setEnabled(enable)
