import matplotlib.pyplot as plt
from modules.env import LAMBDA, SAMPLE_HEIGHT, SAMPLE_WIDTH

def draw_g(g, title):
    fig = plt.figure()
    plt.plot(g, '-')
    plt.xlabel('Z')
    plt.ylabel('g(Z)')

    title = f'Lambda-{LAMBDA} Sample-{SAMPLE_HEIGHT}x{SAMPLE_WIDTH}'
    plt.title(title)
    fig.savefig(f'./fig/{title}.png')