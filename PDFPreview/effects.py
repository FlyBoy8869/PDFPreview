from PySide6.QtWidgets import QGraphicsBlurEffect


def create_blur_effects(widgets: tuple) -> list[QGraphicsBlurEffect]:
    blur_effects = [QGraphicsBlurEffect(widget) for widget in widgets]
    return blur_effects


def set_blur_effects(widgets: tuple, blur_effects: list[QGraphicsBlurEffect], radius: int) -> None:
    # noinspection PyNoneFunctionAssignment
    [(effect.setBlurRadius(radius), effect.setEnabled(False)) for effect in blur_effects]
    [widget.setGraphicsEffect(effect) for widget, effect in zip(widgets, blur_effects)]
