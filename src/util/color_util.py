def calc_color(percentage):
    red = (1, 0, 0)
    yellow = (1, 1, 0)
    green = (0, 1, 0)
    if percentage < 0:
        return _interpolate(yellow, red, -percentage)
    return _interpolate(yellow, green, percentage)


def _interpolate(color1, color2, fraction):
    r = _interpolate_channel(color1[0], color2[0], fraction)
    g = _interpolate_channel(color1[1], color2[1], fraction)
    b = _interpolate_channel(color1[2], color2[2], fraction)

    return (r, g, b)


def _interpolate_channel(d1, d2, fraction):
    return d1 + (d2 - d1) * fraction
