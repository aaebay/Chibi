import pygame
import sys

GRID_SIZE = 10
SQUARE_SIZE = 50
WINDOW_WIDTH = GRID_SIZE * SQUARE_SIZE + 200
WINDOW_HEIGHT = GRID_SIZE * SQUARE_SIZE
BG_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 0, 0)
PLAYER_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 0, 0),
    (0, 128, 0),
    (0, 0, 128),
    (128, 128, 0),
    (128, 0, 128),
    (0, 128, 128),
]

current_input = 0
current_player = 0
grid = [[-1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
game_state = "splash_page"
input_string = ""
players = []

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Chibi')
font = pygame.font.Font(None, 24)

def draw_splash_page():
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, 48)
    title = font.render("Chibi", True, (0, 0, 0))
    title_rect = title.get_rect()
    title_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
    screen.blit(title, title_rect)

    rules = [
        "1. Players take turns to capture a square.",
        "2. Capturing a square gives another turn.",
        "3. When a row or column is complete,",
        "   the player with the majority captures",
        "   the entire row or column.",
    ]
    font = pygame.font.Font(None, 24)
    for i, rule in enumerate(rules):
        rule_text = font.render(rule, True, (0, 0, 0))
        screen.blit(rule_text, (WINDOW_WIDTH // 4, (WINDOW_HEIGHT // 2) + i * 30))

    go_play_text = font.render("Click to start!", True, (0, 0, 0))
    go_play_rect = go_play_text.get_rect()
    go_play_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
    screen.blit(go_play_text, go_play_rect)


def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE,
                               SQUARE_SIZE, SQUARE_SIZE)
            owner = grid[y][x]
            color = players[owner]['color'] if owner != -1 else BG_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def draw_player_info():
    info_surf = pygame.Surface((WINDOW_WIDTH - GRID_SIZE * SQUARE_SIZE,
                                WINDOW_HEIGHT))
    info_surf.fill(BG_COLOR)
    for i, player in enumerate(players):
        player_rect = pygame.Rect(10, 50 * i + 10, 30, 30)
        pygame.draw.rect(info_surf, player['color'], player_rect)
        if i == current_player:
            pygame.draw.rect(info_surf, HIGHLIGHT_COLOR,
                             player_rect, 3)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"{player['name']}: {player['score']}",
                                 True, (0, 0, 0))
        info_surf.blit(score_text, (50, 50 * i + 10))
    screen.blit(info_surf, (GRID_SIZE * SQUARE_SIZE, 0))

def draw_player_setup():
    global input_string
    screen.fill(BG_COLOR)
    if game_state == "player_count":
        prompt = "Enter the number of players (2-20): "
    elif game_state == "player_name":
        prompt = f"Enter name for Player {len(players) + 1}: "
    else:
        prompt = f"Choose color for {players[-1]['name']} (click on the color): "

    prompt_text = font.render(prompt, True, (0, 0, 0))
    screen.blit(prompt_text, (10, 10))
    if game_state == "player_count" or game_state == "player_name":
        input_text = font.render(input_string, True, (0, 0, 0))
        screen.blit(input_text, (10, 50))
    elif game_state == "player_color":
        for i, color in enumerate(PLAYER_COLORS):
            color_rect = pygame.Rect(10 + (i % 6) * 50, 50 + (i // 6) * 50, 30, 30)
            pygame.draw.rect(screen, color, color_rect)

def in_bounds(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def check_capture(x, y, player):
    if not in_bounds(x, y) or grid[y][x] == -1 or grid[y][x] == player:
        return
    surrounded = True
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y +         dy
        if not in_bounds(nx, ny) or grid[ny][nx] != player:
            surrounded = False
            break

    if surrounded:
        prev_owner = grid[y][x]
        if 0 <= prev_owner < len(players):
            grid[y][x] = player
            players[player]['score'] += 1
            players[prev_owner]['score'] -= 1

def check_majority(x, y, player):
    for direction in ('row', 'column'):
        count = [0] * len(players)
        complete = True

        for i in range(GRID_SIZE):
            if direction == 'row':
                owner = grid[y][i]
            else:
                owner = grid[i][x]

            if owner == -1:
                complete = False
                break
            else:
                count[owner] += 1

        if not complete:
            continue

        max_count = max(count)
        if max_count > GRID_SIZE // 2:
            majority_owner = count.index(max_count)
            for i in range(GRID_SIZE):
                if direction == 'row':
                    prev_owner = grid[y][i]
                    grid[y][i] = majority_owner
                else:
                    prev_owner = grid[i][x]
                    grid[i][x] = majority_owner

                if 0 <= prev_owner < len(players) and prev_owner != majority_owner:
                    players[majority_owner]['score'] += 1
                    players[prev_owner]['score'] -= 1



def place_piece(x, y, player):
    if grid[y][x] == -1:
        grid[y][x] = player
        players[player]['score'] += 1
        captured = False
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if check_capture(x + dx, y + dy, player):
                captured = True
        check_majority(x, y, player)
        return captured
    return False

def main():
    global current_input, game_state, input_string, current_player

    grid = [[-1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if game_state == "splash_page":
                    game_state = "player_count"
                elif game_state == "playing":
                    if x < GRID_SIZE * SQUARE_SIZE:
                        grid_x, grid_y = x // SQUARE_SIZE, y // SQUARE_SIZE
                        if grid[grid_y][grid_x] == -1:
                            captured = place_piece(grid_x, grid_y, current_player)
                            if not captured:
                                current_player = (current_player + 1) % len(players)
                elif game_state == "player_color":
                    color_idx = (x - 10) // 50 + ((y - 50) // 50) * 6
                    if 0 <= color_idx < len(PLAYER_COLORS):
                        players[-1]['color'] = PLAYER_COLORS[color_idx]
                        if len(players) < num_players:
                            game_state = "player_name"
                            input_string = ""
                        else:
                            game_state = "playing"
            elif event.type == pygame.KEYDOWN:
                if game_state == "player_count" or game_state == "player_name":
                    if event.key == pygame.K_RETURN:
                        if input_string:
                            if game_state == "player_count":
                                num_players = int(input_string)
                                game_state = "player_name"
                            else:
                                players.append({"name": input_string, "score": 0})
                                game_state = "player_color"
                            input_string = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_string = input_string[:-1]
                    else:
                        input_string += event.unicode

        if game_state == "playing":
            draw_grid()
            draw_player_info()
        elif game_state == "splash_page":
            draw_splash_page()
        else:
            draw_player_setup()

        pygame.display.flip()

if __name__ == "__main__":
    main()