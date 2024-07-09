def calculate_percentage(current_value, maximum_value, index: int = 1):
    return round((current_value / maximum_value) * 100, index)

def reverse_value(x, min_value, max_value):
    return (max_value - x) + min_value