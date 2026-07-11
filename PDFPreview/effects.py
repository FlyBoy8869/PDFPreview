from PySide6.QtWidgets import QGraphicsBlurEffect


def create_blur_effects(widgets: tuple) -> list[QGraphicsBlurEffect]:
    blur_effects = [QGraphicsBlurEffect(widget) for widget in widgets]
    disable_effect(blur_effects)
    return blur_effects


def disable_effect(effects: list[QGraphicsBlurEffect]) -> None:
    for effect in effects:
        effect.setEnabled(False)


def set_blur_effects(widgets: tuple, blur_effects: list[QGraphicsBlurEffect], radius: int) -> None:
    for widget, effect in zip(widgets, blur_effects):
        effect.setBlurRadius(radius)
        widget.setGraphicsEffect(effect)
