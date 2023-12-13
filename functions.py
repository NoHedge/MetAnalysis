
import re


# ----------------------------------------- Processing -----------------------------------------

def split_on_first_non_digit(s):
    match = re.search(r'\d+\D', s)
    match2 = re.search(r'\D(\d+)', s)
    if match or match2:
        ret = match.group()[:-1] if match else match2.group(1)
        return ret
    return s



def contains_integer(input_string):
    integer_pattern = r'\d+'
    match = re.search(integer_pattern, input_string)
    return match is not None


# Function to convert century text to year
def century_to_year(century_str, part_of_century='', is_bce=False):
    try:
        century = int(''.join(filter(str.isdigit, century_str)))
    except ValueError:
        raise ValueError(f"Cannot extract century from '{century_str}'")

    year_start = (century - 1) * 100
    year_end = century * 100

    if is_bce:
        year_start, year_end = -year_end, -year_start

    # Adjust for early, mid, and late
    if part_of_century == 'early':
        return year_start, year_start + 33
    elif part_of_century == 'mid':
        return year_start + 34, year_start + 66
    elif part_of_century == 'late':
        return year_start + 67, year_end
    else:
        return year_start, year_end


# Function to parse a date range string
def parse_date_range(date_range):
    # Normalize the string (remove 'ca.' 'or later', 'or modern', etc.), divide date range by the word 'or' if it exists
    normalized_range = date_range.lower().split(' or ')[0]
    # If no integer, the date is the second half of the split, for cases like 'First or second half 12th century'
    if not contains_integer(normalized_range):
        normalized_range = date_range.lower().split(' or ')[1]

    # if normalized_range.count("ca") > 1:
    #     # For cases like "ca. 1400-50"
    #     normalized_range = normalized_range.split('ca')[1]

    parts = normalized_range.replace('ca. ', '').replace('s', '').split('–')
    start_part, end_part = (parts + parts)[:2]  # Handles single entry cases

    start_part = start_part.replace(" (?)", "")
    end_part = end_part.replace(" (?)", "")

    if start_part.isdigit() and end_part.isdigit():
        start = int(start_part)
        end = int(end_part)
        if start > end:
            end = int(start_part[:2] + end_part)
        return start, end

    is_bce = 'bc' in start_part or 'bc' in end_part
    part_of_century_start = 'early' if 'early' in start_part else 'mid' if 'mid' in start_part else 'late' if 'late' in start_part else ''
    part_of_century_end = 'early' if 'early' in end_part else 'mid' if 'mid' in end_part else 'late' if 'late' in end_part else ''

    # Logic for 'mid' or 'third quarter'
    def interpret_complex_phrase(part):
        if 'early' in part:
            return 'early'
        if 'mid' in part:
            return 'mid'
        if 'third quarter' in part:
            return 'third quarter'
        return ''

    complex_phrase_start = interpret_complex_phrase(start_part)
    complex_phrase_end = interpret_complex_phrase(end_part)

    # Extract numeric part from century strings, if available
    start_century = split_on_first_non_digit(start_part)
    end_century = split_on_first_non_digit(end_part)

    if not is_bce and "centur" not in date_range.lower() and start_century.isdigit() and end_century.isdigit():
        start = int(start_century)
        end = int(end_century)
        if start > end:
            end = int(start_century[:2] + end_century)
            pass
        return start, end
    try:
        if complex_phrase_start or complex_phrase_end:
            # Handle complex phrases
            century = int(start_century) if start_century.isdigit() else int(end_century)
            if complex_phrase_start == 'mid':
                start = (century - 1) * 100 + 34
            elif complex_phrase_start == 'third quarter':
                start = (century - 1) * 100 + 50
            else:
                start = (century - 1) * 100

            if complex_phrase_end == 'mid':
                end = (century - 1) * 100 + 66
            elif complex_phrase_end == 'third quarter':
                end = (century - 1) * 100 + 75
            else:
                end = century * 100
        else:
            # Handle normal cases
            start = century_to_year(start_century, part_of_century_start, is_bce)
            end = century_to_year(end_century, part_of_century_end, is_bce)
    except ValueError as e:
        raise ValueError(f"{e}, \ndate_range: {date_range}, start_century: {start_century}, end_century: {end_century}")

    return start, end



def normalize_year(year, index):
    if isinstance(year, tuple):
        return year[index]
    return year
