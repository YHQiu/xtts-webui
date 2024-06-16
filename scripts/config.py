speed_change_config = {
    "en": 0.8
}

def get_speed_refactor(src_language, target_language):
    result = speed_change_config[target_language]
    if result is None:
        return 1.0
    result = float(result)
    print(result)
    return result

if __name__ == "__main__":
    print(1.0/get_speed_refactor(None, "en"))