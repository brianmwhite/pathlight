from datetime import datetime
from datetime import timedelta


def parse_color_pattern_from_string(config_value_as_string):
    single_color_pattern_by_date = {}

    config_line_parts = config_value_as_string.split(",")
    color_values = config_line_parts[0].split(" ")

    number_of_days = 1

    if len(config_line_parts) == 3:
        number_of_days = int(config_line_parts[2].strip())

    first_day = datetime.strptime(config_line_parts[1].strip(), '%m/%d')

    for x in range(0, number_of_days):
        current_date_in_loop = first_day + timedelta(days=x)
        date_as_key = current_date_in_loop.strftime('%m/%d')
        single_color_pattern_by_date[date_as_key] = color_values

    return single_color_pattern_by_date


def get_color_pattern_config(config_section):
    color_patterns = {}
    for individual_config_key in config_section:
        color_patterns.update(parse_color_pattern_from_string(config_section.get(individual_config_key)))
    return color_patterns
