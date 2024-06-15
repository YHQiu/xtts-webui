speed_change_config = {
    "en": 0.9
}

def get_speed_refactor(src_language, target_language):
    result = speed_change_config[target_language]
    if result is None:
        return 1.0