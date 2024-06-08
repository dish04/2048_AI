import itertools
import os
import pygame
import random
import time
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from agent import agent
from pynput.keyboard import Key, Controller
import neat
from visualize import draw_net
# from agent import agent

# global declarations
# board_values = [[0 for _ in range(4)] for _ in range(4)]
# run = True
# played = False
Net = None
Genome = None
dead = False
boards = list()
config = None

def are_all_2d_arrays_same(arrays):
    # Use the first array as the reference
    reference_array = arrays[0]
    
    # Compare each subsequent array to the reference array
    for array in arrays[1:]:
        if reference_array != array:
            return False
    return True
old_fits = list()
def get_fitness(board,score):
    global dead,boards
    # print(board)
    boards.append(board)
    if len(boards) >=100:
        boards.pop(0)
        dead = are_all_2d_arrays_same(boards)
    # print(boards)
    # print("dead is ",dead)
    # if(dead)print
    pen = 40
    highest = 0
    for i in board:
        for j in i:
            if j > highest:
                highest = j
    if board[0][0] == highest or board[3][0] == highest or board[0][3] == highest or board[3][3] == highest:
        pen += score*1000
    pen += score
    return pen

def prep(arr):
    arr = np.array(arr)
    return arr.reshape(16)

def get_choice(arr):
    max_prob = np.max(arr)
    max_indices = [i for i, prob in enumerate(arr) if prob == max_prob]
    chosen_index = random.choice(max_indices)
    ret = ''
    if chosen_index == 0:
        ret = 'up'
    elif chosen_index == 1:
        ret = 'down'
    elif chosen_index == 2:
        ret = 'left'
    else:
        ret = 'right'
    # print(ret)
    return ret
    

def run_game():
    global board_values, Net, Genome, dead, config
    pygame.init()

# initial set up
    WIDTH = 400
    HEIGHT = 500
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.display.set_caption('2048')
    timer = pygame.time.Clock()
    fps = 60
    font = pygame.font.Font('freesansbold.ttf', 24)

# 2048 game color library
    colors = {0: (204, 192, 179),
          2: (238, 228, 218),
          4: (237, 224, 200),
          8: (242, 177, 121),
          16: (245, 149, 99),
          32: (246, 124, 95),
          64: (246, 94, 59),
          128: (237, 207, 114),
          256: (237, 204, 97),
          512: (237, 200, 80),
          1024: (237, 197, 63),
          2048: (237, 194, 46),
          'light text': (249, 246, 242),
          'dark text': (119, 110, 101),
          'other': (0, 0, 0),
          'bg': (187, 173, 160)}

# game variables initialize
    board_values = [[0 for _ in range(4)] for _ in range(4)]
    game_over = False
    spawn_new = True
    first_Score = True
    init_count = 0
    direction = ''
    score = 0
    valid_move = True
    file = open('high_score.txt', 'r')
    init_high = int(file.readline())
    file.close()
    high_score = init_high

# draw game over and restart text
    def draw_over():
        pygame.draw.rect(screen, 'black', [50, 50, 300, 100], 0, 10)
        game_over_text1 = font.render('Game Over!', True, 'white')
        game_over_text2 = font.render('Press Enter to Restart', True, 'white')
        screen.blit(game_over_text1, (130, 65))
        screen.blit(game_over_text2, (70, 105))


# take your turn based on direction
    def take_turn(direc, board, score):
        # score = 0
        merged = [[False for _ in range(4)] for _ in range(4)]
        gshift = False
        if direc == 'UP':
            for i in range(4):
                for j in range(4):
                    shift = 0
                    if i > 0:
                        for q in range(i):
                            if board[q][j] == 0:
                                shift += 1
                        if shift > 0:
                            board[i - shift][j] = board[i][j]
                            if board[i][j] != 0:
                            # print("Raising")
                                gshift = True
                            board[i][j] = 0
                        if board[i - shift - 1][j] == board[i - shift][j] and not merged[i - shift][j] \
                            and not merged[i - shift - 1][j]:
                            board[i - shift - 1][j] *= 2
                            score += board[i - shift - 1][j]
                            board[i - shift][j] = 0
                            merged[i - shift - 1][j] = True
                            if board[i - shift][j] == 0:
                                continue

        elif direc == 'DOWN':
            for i in range(3):
                for j in range(4):
                    shift = 0
                    for q in range(i + 1):
                        if board[3 - q][j] == 0:
                            shift += 1
                    if shift > 0:
                        board[2 - i + shift][j] = board[2 - i][j]
                        if board[i][j] != 0:
                            # print("Raising")
                                gshift = True
                        board[2 - i][j] = 0
                    if 3 - i + shift <= 3:
                        if board[2 - i + shift][j] == board[3 - i + shift][j] and not merged[3 - i + shift][j] \
                            and not merged[2 - i + shift][j]:
                            board[3 - i + shift][j] *= 2
                            score += board[3 - i + shift][j]
                            board[2 - i + shift][j] = 0
                            merged[3 - i + shift][j] = True
                            if board[2 - i + shift][j] == 0:
                                continue

        elif direc == 'LEFT':
            for i in range(4):
                for j in range(4):
                    shift = 0
                    for q in range(j):
                        if board[i][q] == 0:
                            shift += 1
                    if shift > 0:
                        board[i][j - shift] = board[i][j]
                        if board[i][j] != 0:
                            # print("Raising")
                                gshift = True
                        board[i][j] = 0
                    if board[i][j - shift] == board[i][j - shift - 1] and not merged[i][j - shift - 1] \
                        and not merged[i][j - shift]:
                        board[i][j - shift - 1] *= 2
                        score += board[i][j - shift - 1]
                        board[i][j - shift] = 0
                        merged[i][j - shift - 1] = True
                        if board[i][j - shift] == 0:
                                continue

        elif direc == 'RIGHT':
            for i in range(4):
                for j in range(4):
                    shift = 0
                    for q in range(j):
                        if board[i][3 - q] == 0:
                            shift += 1
                    if shift > 0:
                        board[i][3 - j + shift] = board[i][3 - j]
                        if board[i][j] != 0:
                            # print("Raising")
                                gshift = True
                        board[i][3 - j] = 0
                    if 4 - j + shift <= 3:
                        if board[i][4 - j + shift] == board[i][3 - j + shift] and not merged[i][4 - j + shift] \
                            and not merged[i][3 - j + shift]:
                            board[i][4 - j + shift] *= 2
                            score += board[i][4 - j + shift]
                            board[i][3 - j + shift] = 0
                            merged[i][4 - j + shift] = True
                            if board[i][4 - j + shift] == 0:
                                continue
    # FIXME remove this after debugging
    # print("Shift = ",gshift,[i for i in merged])
    # choice = a.get_chocie(board)[0]
        return board,gshift,merged,score


# spawn in new pieces randomly when turns start
    def new_pieces(board):
        count = 0
        full = False
        over = True
        while any(0 in row for row in board) and count < 1:
            row = random.randint(0, 3)
            col = random.randint(0, 3)
            if board[row][col] == 0:
                count += 1
                if random.randint(1, 10) == 10:
                    board[row][col] = 4
                else:
                    board[row][col] = 2
    # FIXME remove this after debugging
    # print(count)
        if count < 1:
            full = True
        # FIXME remove this after debugging
        # print(full)
    
        for i in range(4):
            for j in range(4):
                if board[i][j] == 0:
                    over = False
                if( i !=3  and board[i][j] == board[i+1][j]) or (j != 3 and board[i][j] == board[i][j+1]):
                    over = False
    # print(over)
        return board, full, over


# draw background for the board
    def draw_board():
        pygame.draw.rect(screen, colors['bg'], [0, 0, 400, 400], 0, 10)
        score_text = font.render(f'Score: {score}', True, 'black')
        high_score_text = font.render(f'High Score: {high_score}', True, 'black')
        screen.blit(score_text, (10, 410))
        screen.blit(high_score_text, (10, 450))
        pass


# draw tiles for game
    def draw_pieces(board):
        for i in range(4):
            for j in range(4):
                value = board[i][j]
                if value > 8:
                    value_color = colors['light text']
                else:
                    value_color = colors['dark text']
                if value <= 2048:
                    color = colors[value]
                else:
                    color = colors['other']
                pygame.draw.rect(screen, color, [j * 95 + 20, i * 95 + 20, 75, 75], 0, 5)
                if value > 0:
                    value_len = len(str(value))
                    font = pygame.font.Font('freesansbold.ttf', 48 - (5 * value_len))
                    value_text = font.render(str(value), True, value_color)
                    text_rect = value_text.get_rect(center=(j * 95 + 57, i * 95 + 57))
                    screen.blit(value_text, text_rect)
                # pygame.draw.rect(screen, 'black', [j * 95 + 20, i * 95 + 20, 75, 75], 2, 5)


# main game loop
    # print("Starting main loop")
    choice = ''
    run = True                                                                                                                                          
    # print("Drawing....")
    # draw_net(config,Genome,view=True)
    # time.sleep(3)
    while run:
        timer.tick(fps)
    #TODO game beautify
        screen.fill('yellow')
        draw_board()
        draw_pieces(board_values)
    # choice = ''
        if spawn_new or init_count < 2:
            board_values, full,game_over = new_pieces(board_values)
            spawn_new = False
            init_count += 1
            # print("HERE 3")
            output = Net.activate(prep(board_values))
            # print("HERE 4")
            # print(output)
            choice = get_choice(output)
            Genome.fitness -= get_fitness(board_values, score)
        if direction != '':
            # print("HERE 2")
            if first_Score:
                score = 0
                first_Score = False
            board_values,ghift,merged,score = take_turn(direction, board_values,score)
            # print("HERE")
            output = Net.activate(prep(board_values))
            # print("HERE")
            # print(output)
            choice = get_choice(output)
            Genome.fitness -= get_fitness(board_values, score)
            played = True
            direction = ''
            if ghift or True in[True in i for i in merged]:
                spawn_new = True
            else:
                spawn_new = False
        if game_over:
            # print("\rGame over cause no valid moves left")
            draw_over()
            if high_score > init_high:
                file = open('high_score.txt', 'w')
                file.write(f'{high_score}')
                file.close()
                init_high = high_score
    
    # a = agent()
    # choice = a.get_chocie(board_values)[0]
    # time.sleep(0.5)
        # element = ''
        for event in pygame.event.get():
            keyboard = Controller()
            keyboard.press(Key.space)
    # while not game_over:
            if event.type == pygame.QUIT:
                # time.sleep(2)
                run = False
                game_over = True
            if choice == 'up':
                direction = 'UP'
            elif choice == 'down':
                direction = 'DOWN'
            elif choice == 'left':
                direction = 'LEFT'
            elif choice == 'right':
                direction = 'RIGHT'
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_UP:
            #         direction = 'UP'
            #     elif event.key == pygame.K_DOWN:
            #         direction = 'DOWN'
            #     elif event.key == pygame.K_LEFT:
            #         direction = 'LEFT'
            #     elif event.key == pygame.K_RIGHT:
            #         direction = 'RIGHT'
            if dead:
                # print("\rGame over cause dead moves")
                game_over=True
                dead = False
            if game_over:
                run = False
                # time.sleep(3)
                board_values = [[0 for _ in range(4)] for _ in range(4)]
                spawn_new = True
                init_count = 0
                score = 0
                direction = ''
                dead = False
                game_over = False

        if score > high_score:
            high_score = score

        pygame.display.flip()
    # print("Game Quit")
    pygame.quit()
# run_game(a)


def check():
    global run, board_values, played
    while run:
        if played:
            # print(board_values)
            played = False

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 4.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # print(id(net))
        global Net, Genome
        Net = net
        Genome= genome
        Genome.fitness = 0
        # print(id(Net))
        run_game()
        # game start
        # while game
        # for xi, xo in zip(xor_inputs, xor_outputs):
        #     output = net.activate(xi)
        #     genome.fitness -= (output[0] - xo[0]) ** 2
        #end of game

def run(config_file):
    # Load configuration.
    global config
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    print(stats)
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # # Show output of the most fit genome against training data.
    # print('\nOutput:')
    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    # for xi, xo in zip(xor_inputs, xor_outputs):
    #     output = winner_net.activate(xi)
    #     print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output)

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    # p.run(eval_genomes, 10)




if __name__ == '__main__':
    # global config_path
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir+"/folder", 'config.txt')
    run(config_file=config_path)
    # print(get_choice([0,1,1,1]))
    
    
    

