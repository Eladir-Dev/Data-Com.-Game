import pygame
import pygame_menu



class game_settings():
    def __init__(self):
        # Custom theme
        self.theme = pygame_menu.themes.THEME_DARK.copy()
        self.theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
        self.theme.title = False  # Optional: hide title
        self.theme.widget_font_size = 25

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
        # Main loop
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            surface.fill((50, 50, 50))  # Background

            # You can draw other UI elements here (e.g., game canvas on the right)
            pygame.draw.rect(surface, (100, 100, 200), (300, 50, 575, 500))  # Example UI panel

            game_settings.menu.update(events)
            game_settings.menu.draw(surface)
            pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    surface = pygame.display.set_mode((900, 600))
    game_settings.main(self=game_settings())