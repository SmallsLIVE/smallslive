from humanfriendly import round_number, pluralize, concatenate


# Common time units, used for formatting of time spans.
time_units = (dict(divider=1, singular='s', plural='s'),
              dict(divider=60, singular='min', plural='mins'),
              dict(divider=60*60, singular='hr', plural='hrs'),
              dict(divider=60*60*24, singular='d', plural='d'),
              dict(divider=60*60*24*7, singular='wk', plural='wks'),
              dict(divider=60*60*24*7*52, singular='yr', plural='yrs'))


def format_timespan(num_seconds):
    """
    Taken from the humanfriendly library and changed the time units to
    their abbreviations.
    """

    if num_seconds < 60:
        # Fast path.
        rounded_number = round_number(num_seconds, False)
        return pluralize(rounded_number, 's', 's')
    else:
        # Slow path.
        result = []
        for unit in reversed(time_units):
            if num_seconds >= unit['divider']:
                count = int(num_seconds / unit['divider'])
                num_seconds %= unit['divider']
                result.append(pluralize(count, unit['singular'], unit['plural']))
        if len(result) == 1:
            # A single count/unit combination.
            return result[0]
        else:
            # Remove insignificant data from the formatted timespan and format
            # it in a readable way.
            return concatenate(result[:2])
