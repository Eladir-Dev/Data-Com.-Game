import pygame
import pygame_menu

pygame.init()
surface = pygame.display.set_mode((1000, 600))  # Wider screen for extra UI

# Custom theme
theme = pygame_menu.themes.THEME_DARK.copy()
theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
theme.title = False  # Optional: hide title
theme.widget_font_size = 25

# Create menu with left-side layout
menu_hight = 600
menu = pygame_menu.Menu(
    height=menu_hight,
    width=250,  # Sidebar width
    title='Game Options',
    theme=theme,
    center_content=False  # Disable auto-centering
)
menu.set_relative_position(0, 10)
# Add widgets with manual positioning
menu.add.label('==Game Options==', float=True).translate(5, 35)
button_spacing = 60
menu.add.text_input('Name: ', default='Player1', float=True).translate(20, 100)
menu.add.button('Start Game', lambda: print('Start'), float=True).translate(20, 100+button_spacing)
menu.add.selector('Type: ', [('Online', 1), ('Local', 2)], float=True).translate(20, 100+button_spacing*2)
menu.add.selector('Timer:  ', [('On', 1), ('Off', 2)], float=True).translate(20, 100+button_spacing*3)
menu.add.button('<- Return', pygame_menu.events.EXIT, float=True).translate(20, menu_hight-60)

# Main loop
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    surface.fill((50, 50, 50))  # Background

    # You can draw other UI elements here (e.g., game canvas on the right)
    pygame.draw.rect(surface, (100, 100, 200), (300, 50, 650, 500))  # Example UI panel

    menu.update(events)
    menu.draw(surface)
    pygame.display.flip()