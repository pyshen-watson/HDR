import matplotlib.pyplot as plt
from modules.env import LAMBDA, SAMPLE_HEIGHT, SAMPLE_WIDTH

def draw_g(album_name, fig_path, g):
    fig = plt.figure()

    plt.plot(g[0], 'b-')
    plt.plot(g[1], 'g-')
    plt.plot(g[2], 'r-')
    plt.xlabel('Z')
    plt.ylabel('g(Z)')

    title = f'[{album_name}] Lambda={LAMBDA} Sample={SAMPLE_HEIGHT}x{SAMPLE_WIDTH}'
    plt.title(title)

    figname =  f'{fig_path}/g-{album_name}.png'
    fig.savefig(figname)
    print(f'Save {figname}.')

def draw_radiance(album_name, fig_path,E):

    fig = plt.figure()

    plt.imshow(E, cmap='jet')
    plt.axis('off')


    title = f'[{album_name} Radiance]'
    plt.title(title)

    figname =  f'{fig_path}/radiance-{album_name}.png'
    fig.savefig(figname)
