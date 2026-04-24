import pygame
import random
import numpy as np

# Do not change the code in this file!!

IS_COLAB = False
try:
    from google.colab.patches import cv2_imshow
    from google.colab import output
    import cv2
    IS_COLAB = True
except ModuleNotFoundError as _:
    pass

if IS_COLAB:
    import os, time
    os.environ["SDL_VIDEODRIVER"] = "dummy"

print("imported game_loop")
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

class QState(object):
    def __init__(self, snake_rel_pos: tuple, surroundings):
        self.snake_rel_pos = snake_rel_pos
        self.surroundings = surroundings

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return self.snake_rel_pos == o.snake_rel_pos and self.surroundings == o.surroundings

    def __str__(self) -> str:
        return f"{self.snake_rel_pos}, {self.surroundings}"
    
    def __repr__(self) -> str:
        return f"{self.snake_rel_pos}, {self.surroundings}"

    def __hash__(self):
        return hash((self.snake_rel_pos, self.surroundings))


def is_blocked(pos, snake_list, DIS_WIDTH, DIS_HEIGHT):
    if pos[0] < 0 or pos[1] < 0: return True
    elif pos[0] >= DIS_WIDTH or pos[1] >= DIS_HEIGHT: return True
    elif pos in snake_list[:-1]: return True
    else: return False


def get_dist_from_food(snake_list, food_loc):
    return abs(snake_list[-1][0] - food_loc[0]) + abs(snake_list[-1][1] - food_loc[1])


def GameLoop(agent, DIS_WIDTH, DIS_HEIGHT, BLOCK_SIZE, FRAMESPEED, draw=True):

    def DrawFood(foodx, foody):
        pygame.draw.rect(dis, GREEN, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])   

    def DrawScore(score):
        font = pygame.font.SysFont("comicsansms", 35)
        value = font.render(f"Score: {score}", True, YELLOW)
        dis.blit(value, [0, 0])

    def DrawSnake(snake_list):
        for x in snake_list:
            pygame.draw.rect(dis, BLACK, [x[0], x[1], BLOCK_SIZE, BLOCK_SIZE])

    def get_Qstate(snake_list, food_loc):
        snake_head = snake_list[-1]
        surrounding_locs = [(snake_head[0], snake_head[1] - BLOCK_SIZE), # up
                            (snake_head[0], snake_head[1] + BLOCK_SIZE), # down
                            (snake_head[0] - BLOCK_SIZE, snake_head[1]), # left
                            (snake_head[0] + BLOCK_SIZE, snake_head[1])] # right
        
        surroundings = [int(is_blocked(loc, snake_list, DIS_WIDTH, DIS_HEIGHT)) for loc in surrounding_locs]
        return QState((np.sign(food_loc[0] - snake_head[0]), np.sign(food_loc[1] - snake_head[1])), tuple(surroundings))


    global dis
    
    if draw: 
        dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
        pygame.display.set_caption('Snake')
        clock = pygame.time.Clock()

    ACTION_DELTA = {'left': (-BLOCK_SIZE, 0), 'right': (BLOCK_SIZE, 0), 'up': (0, -BLOCK_SIZE), 'down': (0, BLOCK_SIZE)}

    # Starting position of snake
    snake_head = (DIS_WIDTH / 2, DIS_HEIGHT / 2)
    snake_list = [snake_head]
    length_of_snake = 1

    # Create first food
    food = (round(random.randrange(0, DIS_WIDTH - BLOCK_SIZE) / 10.0) * 10.0, round(random.randrange(0, DIS_HEIGHT - BLOCK_SIZE) / 10.0) * 10.0)

    game_over = False
    while not game_over:
        
        # Get action from agent
        state = get_Qstate(snake_list, food)
        action = agent.act(state)

        #move the snake based on the selected action
        action_delta = ACTION_DELTA[action]
        snake_head = (snake_head[0] + action_delta[0], snake_head[1] + action_delta[1])
        snake_list.append(snake_head)

        game_over = is_blocked(snake_head, snake_list, DIS_WIDTH, DIS_HEIGHT)

        # Check if snake ate food
        if snake_head == food:
            food = (round(random.randrange(0, DIS_WIDTH - BLOCK_SIZE) / 10.0) * 10.0, 
                    round(random.randrange(0, DIS_HEIGHT - BLOCK_SIZE) / 10.0) * 10.0)
            length_of_snake += 1

        # Delete the last cell since we just added a head for moving, unless we ate a food
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Update Q Table
        agent.update(game_over, get_dist_from_food(snake_list, food), get_Qstate(snake_list, food))

        # Draw food, snake and update score
        if draw:
            dis.fill(BLUE)
            DrawFood(*food)
            DrawSnake(snake_list)
            DrawScore(length_of_snake - 1)
            pygame.display.update()
        
            # Next Frame
            clock.tick(FRAMESPEED)

            if IS_COLAB:
                view = pygame.surfarray.array3d(dis)
                view = view.transpose([1, 0, 2])
                img_bgr = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
                cv2_imshow(img_bgr)
                time.sleep(0.1)
                output.clear()

    return length_of_snake - 1
