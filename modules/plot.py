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

    figname =  f'{fig_path}/response-curve.png'
    fig.savefig(figname)
    print(f'Save {figname}.')

def draw_radiance(album_name, fig_path, radiances):

    color_name = 'BGR'

    for i in range(3):

        fig = plt.figure()

        plt.imshow(radiances[i], cmap='jet')
        plt.axis('off')
        plt.title(f'[{album_name}_{color_name[i]} Radiance]')

        fig_name =  f'{fig_path}/radiance-{color_name[i]}-{album_name}.png'
        print(f'Save {fig_name}')
        fig.savefig(fig_name)
