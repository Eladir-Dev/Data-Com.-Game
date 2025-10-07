import pygame
import sys

"""
This code made using BlackBox AI it is ment to work as an example =.
"""

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 50
GRID_COLS = 10
GRID_ROWS = 4
TOP_GRID_Y = 100
BOTTOM_GRID_Y = 400
X_START = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
COLORS = [(255, 0, 0), (255, 100, 100), (0, 0, 255), (100, 100, 255), (0, 255, 0), (255, 255, 0), (255, 255, 100), (100, 255, 100), (255, 100, 255), (100, 255, 255)]

# Piece class: Encapsulates position, rank, and dragging behavior.
class Piece:
    def __init__(self, rank, flat_index, grid_y_base):
        self.rank = rank  # 1-10 for Stratego ranks (simplified; real game has specific counts like 8 scouts).
        # Position calculation: flat_index (0-39) maps to 4x10 grid.
        # col = flat_index % GRID_COLS (0-9 horizontal).
        # row = flat_index // GRID_COLS (0-3 vertical, integer division).
        # This flattens the 2D grid into 1D for easy initialization, ensuring pieces fill rows left-to-right, top-to-bottom.
        # E.g., index 0: row=0, col=0; index 10: row=1, col=0; index 39: row=3, col=9.
        # Positions relative to grid_y_base (TOP or BOTTOM) for separate grids.
        col = flat_index % GRID_COLS
        row = flat_index // GRID_COLS
        self.rect = pygame.Rect(
            X_START + col * CELL_SIZE,
            grid_y_base + row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        self.original_rect = self.rect.copy()  # Copy for snapping back on invalid drops.
        self.dragging = False
        self.offset = (0, 0)
        self.color = COLORS[(rank - 1) % len(COLORS)]

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text = font.render(str(self.rank), True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    # start_drag: Calculates offset for smooth dragging (prevents jump to cursor tip).
    # Offset = mouse_pos - rect top-left. E.g., center-click: offset=(25,25).
    # Sets dragging=True to enable motion updates. Called only on valid mouse-down hit.
    def start_drag(self, mouse_pos):
        self.offset = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        self.dragging = True

    # update_drag: Repositions rect to follow mouse during motion events.
    # New pos = mouse_pos - offset (maintains relative click point).
    # Called per MOUSEMOTION if dragging. No bounds clamping (can drag off-screen; add min/max for polish).
    def update_drag(self, mouse_pos):
        if self.dragging:
            self.rect.x = mouse_pos[0] - self.offset[0]
            self.rect.y = mouse_pos[1] - self.offset[1]

    # stop_drag: Core drop logic—validates and snaps on mouse-up.
    # Loops over top grid slots (4x10). Checks overlap with tolerance (inflate slot by 10px for easier aiming).
    # If overlap + empty slot: Snap to slot, update original_rect, occupy deck_slots[row][col], remove from available_pieces.
    # Removal prevents re-dragging (simulates "placed" state). First match wins (no multi-overlap handling).
    # If no valid drop (e.g., off-grid, occupied, or bottom area): Snap back to original_rect.
    # Modifies deck_slots and available_pieces as side effects. In Stratego extensions: Add rank validation (e.g., no duplicate marshals).
    def stop_drag(self, deck_slots, available_pieces):
        if not self.dragging:
            return
        self.dragging = False
        dropped = False
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                slot_rect = pygame.Rect(
                    X_START + col * CELL_SIZE,
                    TOP_GRID_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                # Tolerance: inflate(10,10) expands slot for forgiving drop detection (avoids pixel-perfect requirement).
                tolerant_slot = slot_rect.inflate(10, 10)
                # colliderect: True if rects overlap. AND slot empty (None).
                if tolerant_slot.colliderect(self.rect) and deck_slots[row][col] is None:
                    self.rect = slot_rect
                    self.original_rect = slot_rect
                    deck_slots[row][col] = self
                    # remove(self): Finds and deletes this instance from list (O(n) but fine for 40 items).
                    # If not in list (edge case), raises ValueError—safe here since called from available_pieces.
                    available_pieces.remove(self)
                    dropped = True
                    break
            if dropped:
                break
        if not dropped:
            self.rect = self.original_rect

# Main function: Handles setup, game loop (events, updates, rendering).
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stratego Piece Dragger")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # deck_slots: 2D list (4 rows x 10 cols) of None (empty). List comp avoids shallow-copy issues.
    # Each cell holds Piece ref or None. Tracks occupancy for drop validation.
    deck_slots = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # available_pieces: 1D list of 40 draggable pieces, positioned in bottom grid.
    # ranks: Cycles 1-10 x4 (simulates Stratego variety; adjust for exact counts: e.g., 1 spy, 8 scouts).
    # flat_index=i ensures sequential filling (row-major order).
    available_pieces = []
    ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 4
    for i, rank in enumerate(ranks):
        piece = Piece(rank, i, BOTTOM_GRID_Y)
        available_pieces.append(piece)

    running = True
    selected_piece = None  # Tracks current drag (None or Piece ref).

    while running:
        # Event loop: Processes input queue. Non-blocking; handles one type at a time.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # MOUSEBUTTONDOWN: Detects click on available piece (bottom only).
            # collidepoint: Checks if mouse_pos inside rect (inclusive).
            # Use available_pieces[:] (copy) to prevent runtime error if list modified during iteration (rare but safe).
            # Sets selected_piece and starts drag. Breaks on first hit (single selection).
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for piece in available_pieces[:]:
                    if piece.rect.collidepoint(mouse_pos):
                        selected_piece = piece
                        piece.start_drag(mouse_pos)
                        break
            # MOUSEBUTTONUP: Ends drag, processes drop.
            # Calls stop_drag (modifies slots/lists). Clears selected_piece for next interaction.
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_piece:
                    selected_piece.stop_drag(deck_slots, available_pieces)
                    selected_piece = None
            # MOUSEMOTION: Updates drag position if active.
            # get_pos() fetches live mouse (even mid-frame).
            elif event.type == pygame.MOUSEMOTION:
                if selected_piece:
                    selected_piece.update_drag(pygame.mouse.get_pos())

        # Rendering: Full redraw each frame (simple 2D; efficient for small scene).
        # Layers: Background > grids > pieces (ensures pieces overlay lines).
        screen.fill(WHITE)

        # Top grid outline: Horizontal/vertical lines for visual slots.
        for row in range(GRID_ROWS + 1):
            y = TOP_GRID_Y + row * CELL_SIZE
            pygame.draw.line(screen, LIGHT_GRAY, (X_START, y), (X_START + GRID_COLS * CELL_SIZE, y), 2)
        for col in range(GRID_COLS + 1):
            x = X_START + col * CELL_SIZE
            pygame.draw.line(screen, LIGHT_GRAY, (x, TOP_GRID_Y), (x, TOP_GRID_Y + GRID_ROWS * CELL_SIZE), 2)

        # Bottom grid outline: Identical to top for consistency.
        for row in range(GRID_ROWS + 1):
            y = BOTTOM_GRID_Y + row * CELL_SIZE
            pygame.draw.line(screen, LIGHT_GRAY, (X_START, y), (X_START + GRID_COLS * CELL_SIZE, y), 2)
        for col in range(GRID_COLS + 1):
            x = X_START + col * CELL_SIZE
            pygame.draw.line(screen, LIGHT_GRAY, (x, BOTTOM_GRID_Y), (x, BOTTOM_GRID_Y + GRID_ROWS * CELL_SIZE), 2)

        # Draw available pieces: Bottom grid (draggables). During drag, rect may be offset but still drawn.
        for piece in available_pieces:
            piece.draw(screen, font)

        # Draw deck pieces: Top grid (placed). Nested loop over 2D slots; skip None.
        for row in deck_slots:
            for piece in row:
                if piece:
                    piece.draw(screen, font)

        # Labels: Static text for UI clarity. Larger font; blitted above grids.
        label_font = pygame.font.Font(None, 36)
        top_label = label_font.render("Deck (Top Grid - Empty Initially)", True, BLACK)
        screen.blit(top_label, (X_START, 50))
        bottom_label = label_font.render("Available Pieces (Bottom Grid)", True, BLACK)
        screen.blit(bottom_label, (X_START, 350))

        # Flip: Shows back buffer (double-buffering avoids flicker).
        pygame.display.flip()
        # Tick: Caps at 60 FPS for smooth, consistent motion (e.g., dragging).
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()