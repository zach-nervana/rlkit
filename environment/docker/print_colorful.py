import random
import colorful

id_colors = {}
next_color = 0
colors = ["blue", "orange", "cyan", "red", "green", "violet", "magenta", "yellow"]


def id_to_color(id):
    if id not in id_colors:
        # id_colors[id] = colors[next_color]
        # next_color + 1
        id_colors[id] = random.choice(colors)

    return id_colors[id]


def print_colorful(id, text, **kwargs):
    color = getattr(colorful, id_to_color(id))
    print(color(text), **kwargs)
