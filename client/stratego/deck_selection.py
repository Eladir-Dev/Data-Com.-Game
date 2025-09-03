import pygame
import pygame_menu
from .stratego_types import StrategoRenderedTile
# from "/stratego_types.py"
# class DeckSelection(pygame_menu.Menu):



class game_settings():
    def __init__(self):
        # Custom theme
        self.theme = pygame_menu.themes.THEME_DARK.copy()
        self.theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
        self.theme.title = False  # Optional: hide title
        self.theme.widget_font_size = 25

        rows = 10
        cols = 4
        self.pices = [[0 for _ in range(cols)] for _ in range(rows)]
        self.deck = [[0 for _ in range(cols)] for _ in range(rows)]
        """
            Encoding legend:
            * 'S' = Spy (1)
            * '1' = Marshal (1)
            * 'G' = General (1)
            * '2' = Coronel (2)
            * '3' = Major (3)
            * 'C' = Captain (4)
            * 'L' = Lieutenant (4)
            * '4' = Sargeant (4)
            * '8' = Scout (8)
            * '5' = Miner (5)
            * 'B' = Bomb (6)
            * 'F' = Flag (1)
            """
        unitAmountIdx = 0
        # unit[piece, amount]
        units = [('S', 1),('1', 1),('G', 1),('2', 2),('3', 3),('C', 4), ('L', 4),('4', 4),('8', 8),('5', 5),('B', 6),('F', 1)]
        for col in range(cols): # creats the 2d array TODO todavia no esta terminado
            for row in range(rows):
                unit = units[unitAmountIdx]
                amount = unit[1]
                if amount <= 0:
                    unitAmountIdx += 1
                self.pices[col][row] = unit[0] # adds string to 2d array
                amount = amount - 1
        print(self.pices)

        # Create menu with left-side layout
        menu_hight = 600
        self.menu = pygame_menu.Menu(
            height=menu_hight,
            width=275,  # Sidebar width
            title='Game Options',
            theme=self.theme,
            center_content=False  # Disable auto-centering
        )
        self.menu.set_relative_position(0, 10)
        # Add widgets with manual positioning
        self.menu.add.label('==Game Options==', float=True).translate(5, 35)
        button_spacing = 60
        self.menu.add.text_input('Name: ', default='Player1', float=True).translate(20, 100)
        self.menu.add.button('Start Game', lambda: print('Start'), float=True).translate(20, 100 + button_spacing)
        self.menu.add.selector('Type: ', [('Online', 1), ('Local', 2)], float=True).translate(20,
                                                                                              100 + button_spacing * 2)
        self.menu.add.selector('Timer:  ', [('On', 1), ('Off', 2)], float=True).translate(20, 100 + button_spacing * 3)
        self.menu.add.button('<- Return', pygame_menu.events.EXIT, float=True).translate(20, menu_hight - 60)


    def generate_screen(self):
        return game_settings()

    def main(self):
        #self.__init__()# TODO revisar coo mejora y si todo esta bien
        game_settings = self.generate_screen()
        #Main loop
        # while True:
        #     events = pygame.event.get()
        #     for event in events:
        #         if event.type == pygame.QUIT:
        #             exit()
        #
        #     surface.fill((50, 50, 50))  # Background
        #
        #     # You can draw other UI elements here (e.g., game canvas on the right)
        #     pygame.draw.rect(surface, (100, 100, 200), (300, 50, 575, 500))  # Example UI panel
        #
        #     game_settings.menu.update(events)
        #     game_settings.menu.draw(surface)
        #     pygame.display.flip()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                print(mouse_pos)

                for rendered_tile in rendered_tiles:
                    sprite_rect = rendered_tile.sprite_rect

                    if sprite_rect.collidepoint(mouse_pos):
                        # TODO: Do not print these out in an actual game, it
                        # would ruin the entire point of hiding the opponent's pieces.
                        print(rendered_tile.str_encoding)

                        if global_game_data.last_selected_piece is None:
                            # Select the tile.
                            global_game_data.last_selected_piece = rendered_tile

                        else:
                            from_pos = global_game_data.last_selected_piece.board_location
                            to_pos = rendered_tile.board_location

                            move_cmd = gen_move_cmd(from_pos, to_pos)

                            # Un-select the tile.
                            global_game_data.last_selected_piece = None
            #You can draw other UI elements here (e.g., game canvas on the right)
            pygame.draw.rect(surface, (100, 100, 200), (300, 50, 575, 500))  # Example UI panel

            game_settings.menu.update(events)
            game_settings.menu.draw(surface)
            pygame.display.flip()

        return move_cmd
def main():
    pygame.init()
    surface = pygame.display.set_mode((900, 600))
    game_settings.main(self=game_settings())

if __name__ == "__main__":
   main()