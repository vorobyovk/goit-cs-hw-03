def validate_name(name: str) -> tuple[bool, str, str]:
    """Валідація імені кота"""
    name = name.strip()
    if not name:
        return False, "", "Ім'я кота не може бути порожнім"
    if len(name) < 2:
        return False, "", "Ім'я кота має бути довшим за 1 символ"
    return True, name, ""  # Changed to return three values


def validate_age(age: str) -> tuple[bool, int, str]:
    """Валідація віку кота"""
    try:
        age_int = int(age)
        if age_int <= 0:
            return False, 0, "Вік кота має бути додатнім числом"
        if age_int > 30:
            return False, 0, "Вказаний вік перевищує очікувану тривалість життя кота"
        return True, age_int, ""
    except ValueError:
        return False, 0, "Вік має бути цілим числом"


def validate_features(features: str) -> tuple[bool, list, str]:
    """Валідація характеристик кота"""
    features_list = [f.strip() for f in features.split(",") if f.strip()]
    if not features_list:
        return False, [], "Потрібно вказати хоча б одну характеристику"
    return True, features_list, ""
