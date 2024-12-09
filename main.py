import pygame
from pygame.locals import *
from collections import deque
import random
import re
import os
import subprocess

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 10  # Size of each square in the grid (reduced by 50%)
ROWS = HEIGHT // GRID_SIZE
COLS = WIDTH // GRID_SIZE

BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GRID_LINE_COLOR = (200, 200, 200)  # Light grey grid lines for a subtler effect
BUTTON_COLOR = (150, 150, 255)
BUTTON_BORDER_COLOR = (0, 0, 150)
FPS = 30


################################################################################


        # PYGAME FUNCTIONS

################################################################################


# Initialize pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flood Fill on Grid')

# Create a 2D array for the grid to store colors
grid = [[WHITE for _ in range(COLS)] for _ in range(ROWS)]

# List to store one point per connected shape
shapes = []

# Define the "Save" button
button_rect = pygame.Rect(10, HEIGHT - 40, 100, 30)

def draw_grid():
    """Draw the grid and current colors on the screen."""
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(screen, grid[row][col], (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
    # Draw grid lines with a lighter, thinner color for a less perturbing look
    for row in range(ROWS + 1):  # Draw horizontal lines
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, row * GRID_SIZE), (WIDTH, row * GRID_SIZE), 1)

    for col in range(COLS + 1):  # Draw vertical lines
        pygame.draw.line(screen, GRID_LINE_COLOR, (col * GRID_SIZE, 0), (col * GRID_SIZE, HEIGHT), 1)

def draw_button():
    """Draw the 'Save' button at the bottom of the screen."""
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, button_rect, 3)  # Border for the button
    font = pygame.font.Font(None, 36)
    text = font.render("Save", True, (0, 0, 0))
    screen.blit(text, (button_rect.x + 20, button_rect.y + 5))



################################################################################


        # END OF PYGAME FUNCTIONS

################################################################################    


################################################################################


        # INPUT PROCESSING FUNCTIONS

################################################################################


def generate_adjacency_matrix(zone_matrix):
    """Generate the adjacency matrix for the zones in the zone_matrix."""
    # Get the number of zones (excluding the -1, which represents black cells)
    zone_ids = set(zone for row in zone_matrix for zone in row if zone >= 0)
    zone_count = len(zone_ids)

    # Initialize the adjacency matrix (zone_count x zone_count), all values set to 0
    adjacency_matrix = [[0] * zone_count for _ in range(zone_count)]

    # Map zone_id to its index in the adjacency matrix
    zone_to_index = {zone_id: idx for idx, zone_id in enumerate(sorted(zone_ids))}

    # Iterate through the grid and check neighbors
    for row in range(ROWS):
        for col in range(COLS):
            current_zone = zone_matrix[row][col]

            if current_zone >= 0:  # If it's a zone (including -1)
                # Check all 4 neighbors (up, down, left, right)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = col + dx, row + dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS:
                        neighbor_zone = zone_matrix[ny][nx]

                        # If the neighbor is -1, continue searching in the same direction until we find a valid zone
                        if neighbor_zone == -1:
                            # Follow the neighbor's direction to find a valid zone
                            while 0 <= nx < COLS and 0 <= ny < ROWS and zone_matrix[ny][nx] == -1:
                                nx += dx
                                ny += dy

                            # If a valid zone is found (not -1), check its adjacency
                            if 0 <= nx < COLS and 0 <= ny < ROWS:
                                neighbor_zone = zone_matrix[ny][nx]

                        # If the neighbor is a valid zone and not the current zone, add adjacency
                        if neighbor_zone != -1 and neighbor_zone != current_zone:
                            # Get the indices for both zones
                            current_idx = zone_to_index[current_zone]
                            neighbor_idx = zone_to_index[neighbor_zone]

                            # Add the edge to the adjacency matrix (undirected graph)
                            adjacency_matrix[current_idx][neighbor_idx] = 1
                            adjacency_matrix[neighbor_idx][current_idx] = 1

    return adjacency_matrix, zone_count 

def save_shapes():
    """Identify all distinct shapes (white connected components) and store one point per shape."""
    visited = set()
    shapes.clear()
    
    # Initialize a matrix to store zone IDs, where -1 represents black cells (borders)
    zone_matrix = [[-1 if grid[row][col] == BLACK else 0 for col in range(COLS)] for row in range(ROWS)]
    
    zone_id = 0  # Start with the first zone id for labeling connected white regions
    
    for row in range(ROWS):
        for col in range(COLS):
            if (col, row) not in visited and grid[row][col] == WHITE:
                # Perform BFS to label the current shape and mark the visited nodes
                bfs(col, row, visited, zone_id, zone_matrix)
                
                # After BFS, add one point from the shape (first visited point in the zone)
                shapes.append((col, row))
                
                # Increment zone_id for the next shape
                zone_id += 1
    adj, zncnt = generate_adjacency_matrix(zone_matrix)
    update_4color_file(adj, zncnt)


def process_adjacency_matrix(adjacency_matrix, zone_count):
    """
    Processes the adjacency matrix to generate neighbor and non-neighbor constraints.

    Returns:
    - neighbors: List of neighbor relationships (e.g., neighbor(a, b).)
    - non_neighbors: List of non-neighbor relationships (e.g., -neighbor(a, c).)
    - not_equals: List of not-equal constraints (e.g., a != b.)
    """
    neighbors = []
    non_neighbors = []
    not_equals = []

    # Generate the variable names for each zone
    zone_vars = [chr(ord('a') + i) for i in range(zone_count)]

    for i in range(zone_count):
        for j in range(i + 1, zone_count):  # Avoid duplicate checks
            if adjacency_matrix[i][j] == 1:
                neighbors.append(f"neighbor({zone_vars[i]}, {zone_vars[j]}).")
            else:
                non_neighbors.append(f"-neighbor({zone_vars[i]}, {zone_vars[j]}).")
            not_equals.append(f"{zone_vars[i]} != {zone_vars[j]}.")

    return neighbors, non_neighbors, not_equals

def update_4color_file(adjacency_matrix, zone_count):
    """
    Reads the current 4color.in file, updates its count, and creates a new file
    with the adjacency relations and not-equals constraints after the % neighbor relations line.
    """
    original_file = "4color.in"
    if not os.path.exists(original_file):
        print(f"Error: File {original_file} does not exist.")
        return

    with open(original_file, 'r') as file:
        lines = file.readlines()

    # Extract the current count from the first line
    first_line = lines[0]
    if not first_line.__contains__("original file("):
        print("Error: Invalid format for the first line of the file.")
        return

    # Extract the count from the format %original file(current count 0)
    try:
        current_count = int(first_line.split('(')[1].split()[2].split(')')[0])
    except (IndexError, ValueError):
        print("Error: Invalid format for the current count.")
        return

    new_count = current_count + 1

    lines[0] = f"%original file(current count {new_count})\n"

    # Write the updated lines back to the file
    with open(original_file, 'w') as file:
        file.writelines(lines)

    lines[2] = lines[2].replace("DOMAIN_SIZE", str(zone_count))

    # Prepare the new file name
    new_file = f"4color{new_count}.in"

    # Generate the adjacency relations and constraints
    neighbors, non_neighbors, not_equals = process_adjacency_matrix(adjacency_matrix, zone_count)

    # Find the % neighbor relations line in the file
    neighbor_relations_index = None
    for i, line in enumerate(lines):
        if line.strip() == "% neighbor relations":
            neighbor_relations_index = i
            break

    if neighbor_relations_index is None:
        print("Error: % neighbor relations line not found in the file.")
        return

    # Write the new file
    with open(new_file, 'w') as file:
        # Write the updated first line
        file.write(f"%file {new_count}\n")

        # Copy all lines before % neighbor relations
        file.writelines(lines[1:neighbor_relations_index + 3])

        # Insert the new neighbor relations
        for neighbor in neighbors:
            file.write(f"{neighbor}\n")

        # Insert the non-neighbor relations
        for non_neighbor in non_neighbors:
            file.write(f"{non_neighbor}\n")

        # Insert the not-equals constraints at the end of the file
        for constraint in not_equals:
            file.write(f"{constraint}\n")

        # Copy the remaining lines after % neighbor relations
        file.writelines(lines[neighbor_relations_index + 1:])

    print(f"File {new_file} has been created.")
    run_mace4(new_file)

def run_mace4(file_name):

    command = f"wsl mace4 -f {file_name} > 4color.out"
    try:
        subprocess.run(command, shell=True, check=True)
        print("Mace4 executed successfully, and the output was written to 4color.out.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command execution failed with error: {e}")


def extract_color_indices_from_file(file_path):
    """
    Searches the 4color.out file for the exact line containing 'function(color(_), [...])'
    and extracts the list of color indices from it.

    Args:
    - file_path: Path to the 4color.out file.

    Returns:
    - A list of color indices extracted from the file, or None if not found.
    """
    try:
        # Open the file and read it line by line
        with open(file_path, 'r') as file:
            for line in file:
                # Check if the line contains the pattern we're looking for
                if 'function(color(_), [' in line:
                    # Extract the part inside the brackets (color indices)
                    match = re.search(r'function\(color\(_\), \[(.*?)\]\)', line)
                    if match:
                        indices_str = match.group(1)  # The matched string inside the brackets
                        # Convert the string to a list of integers
                        color_indices = list(map(int, indices_str.split(',')))
                        return color_indices
        
        # If no match was found
        print(f"Pattern not found in the file {file_path}")
        return None

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None

################################################################################


        # END OF INPUT PROCESING FUNCTIONS

################################################################################




################################################################################


        # COLORING FUNCTIONS

################################################################################

def bfs(start_x, start_y, visited, zone_id, zone_matrix):
    """
    Perform BFS to both find connected white nodes and label zones with a unique ID.

    Parameters:
    - start_x, start_y: Starting coordinates for BFS.
    - visited: A set to track visited nodes.
    - zone_id: The unique ID for the current zone (used for labeling zones).
    - zone_matrix: The matrix to label zones.
    """
    queue = deque([(start_x, start_y)])
    visited.add((start_x, start_y))
    zone_matrix[start_y][start_x] = zone_id

    while queue:
        x, y = queue.popleft()

        # Check all 4 neighbors (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if (nx, ny) not in visited and grid[ny][nx] == WHITE:
                    visited.add((nx, ny))
                    zone_matrix[ny][nx] = zone_id
                    queue.append((nx, ny))


def bfs_color(start_x, start_y, target, replacement):
    """Perform a BFS to flood fill an area starting from a specific point."""
    if target == replacement or grid[start_y][start_x] != target:
        return
    
    queue = deque([(start_x, start_y)])
    grid[start_y][start_x] = replacement
    
    while queue:
        x, y = queue.popleft()
        
        # Check all 4 neighbors (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == target:
                grid[ny][nx] = replacement
                queue.append((nx, ny))

def color_shapes_with_list(color_indices):
    """Color the shapes based on the given color index list."""
    if len(color_indices) != len(shapes):
        print("Error: The length of the color index list does not match the number of saved shapes.")
        return

    # Randomly assign the numbers 0, 1, 2, 3 to the 4 colors
    colors = [ORANGE, YELLOW, GREEN, BLUE]
    random.shuffle(colors)
    color_map = {i: colors[i] for i in range(4)}
    
    # Iterate through the shapes and color them
    for index, (start_x, start_y) in enumerate(shapes):
        try:
            target_color = color_map[color_indices[index]]
        except KeyError:
            print(f"Error: Color index {color_indices[index]} is out of range. Assigning RED.")
            target_color = RED
        bfs_color(start_x, start_y, WHITE, target_color)

################################################################################


        # END OF COLORING FUNCTIONS

################################################################################

def main():
    running = True
    drawing = False

    while running:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button (drawing)
                    drawing = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // GRID_SIZE
                    grid_y = mouse_y // GRID_SIZE
                    grid[grid_y][grid_x] = BLACK  # Draw a black square
                elif event.button == 3:  # Right mouse button (flood fill)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = mouse_x // GRID_SIZE
                    grid_y = mouse_y // GRID_SIZE
                    bfs_color(grid_x, grid_y, WHITE, RED)  # Flood-fill with red
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
            # Save button click detection
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    save_shapes()  # Save the shapes when the button is clicked
                    color_indices = extract_color_indices_from_file("4color.out")
                    color_shapes_with_list(color_indices)  # Color shapes after saving
            # Draw the grid and current colors
            if drawing:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE
                grid[grid_y][grid_x] = BLACK  # Draw a black square as the mouse drags

        draw_grid()
        draw_button()

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()