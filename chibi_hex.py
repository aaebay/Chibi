import pygame
import sys
import math



HEX_RADIUS = 25
HEX_SPACING = 0
GRID_SIZE = 10
SQUARE_SIZE = 50

LEFT_PADDING = 75
TOP_PADDING = 75

GRID_WIDTH = int(GRID_SIZE * (1.5 * HEX_RADIUS + HEX_SPACING) + LEFT_PADDING * 2)
GRID_HEIGHT = int(GRID_SIZE * (math.sqrt(3) * HEX_RADIUS + HEX_SPACING) + math.sqrt(3) * HEX_RADIUS / 2 + HEX_SPACING / 2 + TOP_PADDING * 2)

WINDOW_WIDTH = GRID_WIDTH + 200
WINDOW_HEIGHT = GRID_HEIGHT

HIGHLIGHT_COLOR = (0, 0, 0)
PLAYER_COLORS = [    (255, 0, 0), (0, 255, 0), (0, 0, 255),    (255, 255, 50), (255, 100, 180), (50, 255, 255),    (255, 120, 0), (150, 50, 200), (200, 80, 100),    (255, 200, 0), (150, 120, 255), (0, 255, 180),    (255, 0, 200), (255, 180, 0), (50, 220, 220),    (170, 50, 255), (255, 90, 90), (0, 170, 170),    (150, 150, 255), (255, 130, 100), (60, 200, 130),    (255, 50, 255), (240, 100, 100), (30, 200, 255),    (200, 70, 200), (200, 200, 50), (255, 50, 50),    (80, 150, 255), (255, 150, 50), (0, 255, 255)]



available_colors = PLAYER_COLORS.copy()
bg_color = (72, 118, 127)
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
    screen.fill(bg_color)
    title_font = pygame.font.Font("freesansbold.ttf", 144)
    title_text = title_font.render("Chibi", True, (0, 0, 0))
    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 50))

    rules_font = pygame.font.Font("freesansbold.ttf", 20)
    rules = [
        "Rules:",
        "1. Players take turns placing a piece on the grid.",
        "2. If a piece is surrounded by an opponent's pieces,",
        "it's captured and the capturing player receives another turn.",
        "3. If a player fills a row or column with more than half",
        "their pieces, they capture all the pieces in that row or column.",
        "4. The game ends when the entire grid is filled.",
        "5. The player with the most captured pieces wins!",
    ]
    y_offset = 250
    line_spacing = 25
    for rule in rules:
        rule_text = rules_font.render(rule, True, (0, 0, 0))
        screen.blit(rule_text, (WINDOW_WIDTH // 2 - rule_text.get_width() // 2, y_offset))
        y_offset += line_spacing

    go_play_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, y_offset + 20, 200, 50)
    pygame.draw.rect(screen, (0, 0, 0), go_play_button, 2)
    go_play_text = pygame.font.Font("freesansbold.ttf", 32).render("Go Play", True, (0, 0, 0))
    screen.blit(go_play_text, (WINDOW_WIDTH // 2 - go_play_text.get_width() // 2, y_offset + 30))


def draw_hexagon(screen, x, y, color):
    points = []
    for angle in range(0, 360, 60):
        px = x + HEX_RADIUS * math.cos(math.radians(angle))
        py = y + HEX_RADIUS * math.sin(math.radians(angle))
        points.append((px, py))
    pygame.draw.polygon(screen, color, points)
    pygame.draw.lines(screen, (0, 0, 0), True, points, 1)

def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            hex_x = LEFT_PADDING + x * (1.5 * HEX_RADIUS + HEX_SPACING)
            hex_y = TOP_PADDING + y * (math.sqrt(3) * HEX_RADIUS + HEX_SPACING)

            if x % 2 != 0:
                hex_y += math.sqrt(3) * HEX_RADIUS / 2 + HEX_SPACING / 2

            # Draw background color for each hexagon
            bg_points = [(hex_x + HEX_RADIUS * math.cos(math.radians(angle)), hex_y + HEX_RADIUS * math.sin(math.radians(angle))) for angle in range(0, 360, 60)]
            pygame.draw.polygon(screen, players[current_player]['color'], bg_points)

            # Draw hexagon
            owner = grid[y][x]
            color = players[owner]['color'] if owner != -1 else (255, 255, 255)
            draw_hexagon(screen, hex_x, hex_y, color)


def draw_player_info():
    info_surf = pygame.Surface((WINDOW_WIDTH - GRID_SIZE * SQUARE_SIZE,
                                WINDOW_HEIGHT))
    info_surf.fill(bg_color)
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
    screen.fill(bg_color)
    if game_state == "player_count":
        prompt = "Enter the number of players (2-5): "
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
        for i, color in enumerate(available_colors):
            color_rect = pygame.Rect(10 + (i % 6) * 50, 50 + (i // 6) * 50, 30, 30)
            pygame.draw.rect(screen, color, color_rect)

def in_bounds(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def get_hex_neighbors(x, y):
    neighbors = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)):
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny):
            neighbors.append((nx, ny))
    return neighbors

def check_capture(x, y, player):
    if not in_bounds(x, y) or grid[y][x] == -1 or grid[y][x] == player:
        return

    neighbors = get_hex_neighbors(x, y)
    player_neighbors_count = 0

    for nx, ny in neighbors:
        if grid[ny][nx] == player:
            player_neighbors_count += 1

    if player_neighbors_count >= 4:
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
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)):
            nx, ny = x + dx, y + dy
            prev_owner = grid[ny][nx] if in_bounds(nx, ny) else -1
            check_capture(nx, ny, player)
            if prev_owner != -1 and prev_owner != player and grid[ny][nx] == player:
                captured = True
        check_majority(x, y, player)
        return captured
    return False

def coord_to_grid(x, y):
    x -= LEFT_PADDING
    y -= TOP_PADDING
    grid_x = int(round(x / (1.5 * HEX_RADIUS + HEX_SPACING)))
    if grid_x % 2 == 0:
        grid_y = int(round(y / (math.sqrt(3) * HEX_RADIUS + HEX_SPACING)))
    else:
        grid_y = int(round((y - math.sqrt(3) * HEX_RADIUS / 2 - HEX_SPACING / 2) / (math.sqrt(3) * HEX_RADIUS + HEX_SPACING)))

    return grid_x, grid_y


def main():
    global current_input, game_state, input_string, current_player, bg_color

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
                    grid_x, grid_y = coord_to_grid(x, y)
                    if in_bounds(grid_x, grid_y) and grid[grid_y][grid_x] == -1:
                        captured = place_piece(grid_x, grid_y, current_player)
                        if not captured:
                            current_player = (current_player + 1) % len(players)
                elif game_state == "player_color":  # Fix the indentation here
                    color_idx = (x - 10) // 50 + ((y - 50) // 50) * 6
                    if 0 <= color_idx < len(available_colors):
                        chosen_color = available_colors[color_idx]
                        players[-1]['color'] = chosen_color
                        available_colors.remove(chosen_color)
                        if len(players) < num_players:
                            game_state = "player_name"
                            input_string = ""
                        else:
                            # Set the background color to white before the game starts
                            bg_color = (255, 255, 255)
                            game_state = "playing"


            elif event.type == pygame.KEYDOWN:
                if game_state == "player_count" or game_state == "player_name":
                    if event.key == pygame.K_RETURN:
                        if input_string:
                            if game_state == "player_count":
                                num_players = int(input_string)
                                if 2 <= num_players <= 5:  # Enforce min and max number of players
                                    game_state = "player_name"
                                else:
                                    input_string = ""  # Clear input string and prompt for a valid number
                            else:
                                players.append({"name": input_string, "score": 0, "color": None})
                                game_state = "player_color"
                            input_string = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_string = input_string[:-1]
                    else:
                        input_string += event.unicode

        if game_state == "playing":
            screen.fill(bg_color)
            # Update the background color to match the current player's color
            bg_color = players[current_player]['color']
            draw_grid()
            draw_player_info()
        elif game_state == "splash_page":
            draw_splash_page()
        else:
            draw_player_setup()

        pygame.display.flip()



if __name__ == "__main__":
    main()
