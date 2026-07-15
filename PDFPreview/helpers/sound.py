from config.config import OS

if OS == "Windows":
    import winsound
    message_beep = winsound.MessageBeep
    dialog_sound = winsound.MB_OK
else:
    message_beep = lambda x: ...
    dialog_sound = 0
