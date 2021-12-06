from datetime import datetime
from datetime import timedelta
import board


def lookup_pin(pin_number):
    if pin_number == 10:
        return board.D10
    elif pin_number == 12:
        return board.D12
    elif pin_number == 18:
        return board.D18
    elif pin_number == 21:
        return board.D21
    else:
        return board.D18


def parse_color_pattern_from_string(config_value_as_string):
    pattern_line_position = 0
    colors_line_position = 1
    start_date_line_position = 2
    number_of_days_position = 3
    max_config_line_parts = 4

    single_line_color_pattern_by_date = {}

    config_line_parts = config_value_as_string.strip().split(",")

    pattern_value = config_line_parts[pattern_line_position].strip()
    color_values = config_line_parts[colors_line_position].strip().split(" ")

    default_number_of_days = 1

    if len(config_line_parts) == max_config_line_parts:
        default_number_of_days = int(config_line_parts[number_of_days_position].strip())

    first_day = datetime.strptime(config_line_parts[start_date_line_position].strip(), '%m/%d')

    for x in range(0, default_number_of_days):
        current_date_in_loop = first_day + timedelta(days=x)
        date_as_key = current_date_in_loop.strftime('%m/%d')
        single_line_color_pattern_by_date[date_as_key] = pattern_value, color_values

    return single_line_color_pattern_by_date


def get_color_pattern_config(config_section):
    color_patterns = {}
    for individual_config_key in config_section:
        color_patterns.update(parse_color_pattern_from_string(config_section.get(individual_config_key)))
    return color_patterns
