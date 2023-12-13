
# ----------------------------------------- Processing -----------------------------------------
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
    # Normalize the string (remove 'ca.', 'or later', 'or modern', etc.)
    normalized_range = date_range.lower().split(' or ')[0]
    if not contains_integer(normalized_range):
        normalized_range = date_range.lower().split(' or ')[1]

    parts = normalized_range.replace('ca. ', '').replace('s', '').split('–')
    start_part, end_part = (parts + parts)[:2]  # Handles single entry cases

    is_bce = 'bce' in start_part or 'bce' in end_part
    part_of_century_start = 'early' if 'early' in start_part else 'mid' if 'mid' in start_part else 'late' if 'late' in start_part else ''
    part_of_century_end = 'early' if 'early' in end_part else 'mid' if 'mid' in end_part else 'late' if 'late' in end_part else ''

    # Logic for 'mid' or 'third quarter'
    def interpret_complex_phrase(part):
        if 'mid' in part:
            return 'mid'
        if 'third quarter' in part:
            return 'third quarter'
        return ''

    complex_phrase_start = interpret_complex_phrase(start_part)
    complex_phrase_end = interpret_complex_phrase(end_part)

    # Extract numeric part from century strings, if available
    start_century = ''.join(filter(str.isdigit, start_part))
    end_century = ''.join(filter(str.isdigit, end_part))

    try:
        if complex_phrase_start or complex_phrase_end:
            # Handle complex phrases
            century = int(start_century or end_century)
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

    try:
        return start, end
    except:
        pass


def normalize_year(year):
    if isinstance(year, tuple):
        return year[0]  # Assuming the first element of the tuple is the start year
    return year
