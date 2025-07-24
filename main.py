import tkinter as tk
from PIL import Image, ImageTk
import os
import webbrowser
import random
import time
import sys
import subprocess

# --- Global Variables ---
moving = True
target_x = None
target_y = None
dx = 0
dy = 0
step_size = 5 # How many pixels to move in each step

stop_timer_active = False
stop_start_time = 0
current_stop_duration = 0 # How long to stay stopped (in seconds)

# Define Sprite Names for Clarity
SPRITE_WALKING = "walking"
SPRITE_IDLE = "padrao" # Using padrao.png as the general idle/still sprite
SPRITE_SPAWN = "spawn" # Sprite for initial spawn animation
SPRITE_DISAPPEAR = "disappear" # Sprite for disappear command
SPRITE_STAY = "stay" # Sprite for "stay still" command
SPRITE_WALK_COMMAND = "walk_command" # Sprite for "walk" command
SPRITE_DRAGGING = "dragging" # Sprite for when the character is being dragged
SPRITE_GAME = "game" # Sprite for opening a game/executable

# Global variables for dragging and click detection
drag_start_x = 0
drag_start_y = 0
is_dragging = False # Flag to distinguish click from drag

# Flag for manual "stay still" mode
manual_stop_mode = False

# Global variable for current facing direction
current_facing_direction = "right" # Default starting direction

# Global variables for text display
speech_text_label = None
speech_bubble_active = False
speech_bubble_timer = None

# Phrases for random walking text (already existing)
walking_phrases = [
    "Que belo dia para caminhar!",
    "Para onde iremos agora?",
    "Explorando o mundo...",
    "Tenho um bom pressentimento!",
    "Andar faz bem!",
    "Um passo de cada vez...",
    "Onde a aventura nos espera?",
    "Observando o cenário."
]

# NOVA LISTA: Frases para fatos aleatórios (com espaços para você preencher)
random_fact_phrases = [
    "Sabia que [FATO 1]? É fascinante!",
    "Um fato interessante: [FATO 2].",
    "Você sabia que [FATO 3]? Incrível!",
    "Curiosidade do dia: [FATO 4].",
    "Pensei em um fato legal: [FATO 5]."
]
# --- End Global Variables ---


# --- Function Definitions ---

# Helper function to end a task silently
def end_task_silently(process_name):
    print(f"DEBUG: Attempting to silently end task: {process_name}")
    try:
        si = None
        if os.name == 'nt':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE

        subprocess.run(['taskkill', '/IM', process_name, '/F', '/T'], check=True, startupinfo=si)
        print(f"DEBUG: Successfully ended task: {process_name}")
        show_speech_bubble(f"Fechou {process_name}!")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Could not end task {process_name}. Error: {e}")
        print("Ensure the process name is correct and you have permissions.")
        show_speech_bubble(f"Erro ao fechar {process_name}!")
    except FileNotFoundError:
        print("ERROR: 'taskkill' command not found. This feature is for Windows only.")
        show_speech_bubble("'taskkill' não encontrado!")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while ending task: {e}")
        show_speech_bubble("Erro ao fechar o programa!")


# Function to show speech bubble (now just text to the side)
def show_speech_bubble(text, duration=3):
    global speech_text_label, speech_bubble_active, speech_bubble_timer

    if speech_text_label is None:
        speech_text_label = tk.Label(root, text="", font=("Arial", 9, "bold"), bg="#F0F0F0", fg="black", wraplength=160, justify="left")
        
    speech_text_label.config(text=text)

    if speech_bubble_timer:
        root.after_cancel(speech_bubble_timer)

    original_char_width = 150
    original_char_height = 200
    text_area_width_estimate = 180
    text_padding = 10

    new_root_width = original_char_width + text_padding + text_area_width_estimate
    new_root_height = original_char_height

    current_x = root.winfo_x()
    current_y = root.winfo_y()

    root.geometry(f"{new_root_width}x{new_root_height}+{current_x}+{current_y}")

    text_label_rel_x = original_char_width + text_padding
    text_label_rel_y = 20

    speech_text_label.place(x=text_label_rel_x, y=text_label_rel_y)

    speech_bubble_active = True

    if duration > 0:
        speech_bubble_timer = root.after(duration * 1000, hide_speech_bubble)

# Function to hide speech bubble (text) and shrink window back
def hide_speech_bubble():
    global speech_text_label, speech_bubble_active, speech_bubble_timer
    if speech_text_label:
        speech_text_label.place_forget()
    
    current_x = root.winfo_x()
    current_y = root.winfo_y()
    
    root.geometry(f"150x200+{current_x}+{current_y}")

    speech_bubble_active = False
    if speech_bubble_timer:
        root.after_cancel(speech_bubble_timer)
        speech_bubble_timer = None


# Function to resume movement after a command delay (used for commands like browser, music, files, game)
def resume_after_command():
    global moving, manual_stop_mode
    if not manual_stop_mode:
        moving = True
        determine_new_target()
        mudar_sprite(SPRITE_WALKING)
        print("DEBUG: Resuming movement after 8-second command delay.")
        show_speech_bubble("Movimento retomado!")
    else:
        moving = False
        mudar_sprite(SPRITE_STAY)
        print("DEBUG: Manual stop mode active. Reverting to STAY sprite after 8s delay.")
        show_speech_bubble("Aguardando novas instruções.", duration=5)


# Executing commands based on text input
def executar_comando(comando):
    global moving, stop_timer_active, manual_stop_mode
    print(f"DEBUG: Executing command: {comando}")
    hide_speech_bubble() # Hide any existing text when a new command is given

    if comando == "google":
        mudar_sprite("navegador")
        webbrowser.open("https://www.google.com")
        show_speech_bubble("Abrindo navegador")
    elif comando == "musica":
        mudar_sprite("musica")
        webbrowser.open("http://googleusercontent.com/spotify.com/9")
        show_speech_bubble("Vamos ouvir algo")
    elif comando == "arquivos":
        mudar_sprite("pasta")
        os.startfile("C:/")  # Opens the C: drive
        show_speech_bubble("Abrindo seus arquivos.")
    elif comando == "comandos":
        mudar_sprite("ajuda")
        show_speech_bubble("Aqui estão os comandos disponíveis")
    elif comando == "tchau": # Command to make the assistant disappear
        mudar_sprite(SPRITE_DISAPPEAR)
        moving = False
        stop_timer_active = False
        manual_stop_mode = False
        entrada.place_forget()
        print("DEBUG: Disappear command received. Assistant will vanish shortly.")
        show_speech_bubble("Até mais!", duration=1)
        root.after(1000, lambda: [root.destroy(), sys.exit()])
        return
    elif comando == "fique": # "STAY" command
        mudar_sprite(SPRITE_STAY)
        moving = False
        stop_timer_active = False
        manual_stop_mode = True
        print("DEBUG: STAY command received. Assistant is now in manual stop mode.")
        show_speech_bubble("Parado, mestre!")
        return
    elif comando == "levante": # "WALK" command
        mudar_sprite(SPRITE_WALK_COMMAND)
        manual_stop_mode = False
        moving = True
        stop_timer_active = False
        determine_new_target()
        print("DEBUG: WALK command received. Assistant is resuming normal movement.")
        show_speech_bubble("Vamos andar!")
        root.after(200, lambda: mudar_sprite(SPRITE_WALKING))
        mover_personagem_suave()
        return
    elif comando == "jogo": # Command to open a game via Steam URI
        mudar_sprite(SPRITE_GAME)
        steam_uri = "steam://rungameid/2357570"
        try:
            os.startfile(steam_uri)
            print(f"DEBUG: Attempting to open Steam game via URI: {steam_uri}")
            show_speech_bubble("Hora de jogar!")
            
            process_to_kill = "msedge.exe"
            print(f"DEBUG: Scheduling termination of '{process_to_kill}' in 5 seconds...")
            print("WARNING: This will close ALL Microsoft Edge windows!")
            root.after(5000, lambda: end_task_silently(process_to_kill))

        except Exception as e:
            print(f"ERROR: Could not open Steam game via URI: {e}")
            print("Make sure Steam is installed and the game (ID 2357570) is in your library.")
            show_speech_bubble("Erro ao abrir jogo!")
            mudar_sprite(SPRITE_IDLE)
    else: # If command is not recognized, go to idle sprite
        mudar_sprite(SPRITE_IDLE)
        print("DEBUG: Unrecognized command. Reverting to idle sprite.")
        show_speech_bubble("Comando não reconhecido.")

    moving = False
    stop_timer_active = False
    print("DEBUG: Command executed. Assistant will stay still for 8 seconds.")
    root.after(8000, resume_after_command)


# Function to change the character image
def mudar_sprite(nome):
    global current_facing_direction

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    try:
        sprite_path = os.path.join(base_path, "sprites", f"{nome}.png")
        imagem = Image.open(sprite_path).resize((150, 150))

        if nome in [SPRITE_WALKING, SPRITE_IDLE, SPRITE_STAY]:
            if current_facing_direction == "left":
                imagem = imagem.transpose(Image.FLIP_LEFT_RIGHT)
        
        imagem_tk = ImageTk.PhotoImage(imagem)
        label.config(image=imagem_tk)
        label.image = imagem_tk
    except FileNotFoundError:
        print(f"Error: Sprite file not found: {sprite_path}. Falling back to {SPRITE_IDLE}.png")
        fallback_sprite_path = os.path.join(base_path, "sprites", f"{SPRITE_IDLE}.png")
        imagem = Image.open(fallback_sprite_path).resize((150, 150))
        
        if current_facing_direction == "left":
            imagem = imagem.transpose(Image.FLIP_LEFT_RIGHT)

        imagem_tk = ImageTk.PhotoImage(imagem)
        label.config(image=imagem_tk)
        label.image = imagem_tk


# Function to determine a new random target position
def determine_new_target():
    global target_x, target_y, dx, dy
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    current_x = root.winfo_x()
    current_y = root.winfo_y()

    character_display_width = 150 
    
    target_x = random.randint(0, screen_width - character_display_width)
    target_y = random.randint(0, screen_height - root.winfo_height())

    dx = target_x - current_x
    dy = target_y - current_y

    distance = (dx**2 + dy**2)**0.5
    if distance > 0:
        dx = int(dx / distance * step_size)
        dy = int(dy / distance * step_size)
    else:
        determine_new_target()


# Function for smooth movement and random stopping
def mover_personagem_suave():
    global target_x, target_y, dx, dy, moving, stop_timer_active, stop_start_time, current_stop_duration, manual_stop_mode, current_facing_direction

    if manual_stop_mode:
        root.after(50, mover_personagem_suave)
        return

    if moving:
        # Randomly decide to stop (e.g., 0.5% chance every movement tick)
        if random.random() < 0.005:
            moving = False
            stop_timer_active = True
            stop_start_time = time.time()
            current_stop_duration = random.uniform(2, 8)
            mudar_sprite(SPRITE_IDLE)
            print(f"DEBUG: Randomly stopped for {current_stop_duration:.2f} seconds.")
            
            # NOVO: Aleatoriamente escolher entre frase de caminhada ou um fato
            if random.random() < 0.5: # 50% de chance de ser um fato
                random_fact = random.choice(random_fact_phrases)
                show_speech_bubble(random_fact, duration=4)
            
            root.after(50, mover_personagem_suave)
            return

        current_x = root.winfo_x()
        current_y = root.winfo_y()

        if target_x is None or (abs(current_x - target_x) < step_size and abs(current_y - target_y) < step_size):
            determine_new_target()

        new_x = current_x + dx
        new_y = current_y + dy

        if dx < 0 and current_facing_direction == "right":
            current_facing_direction = "left"
            mudar_sprite(SPRITE_WALKING)
        elif dx > 0 and current_facing_direction == "left":
            current_facing_direction = "right"
            mudar_sprite(SPRITE_WALKING)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        char_bound_width = 150 
        new_x = max(0, min(new_x, screen_width - char_bound_width))
        new_y = max(0, min(new_y, screen_height - root.winfo_height()))

        root.geometry(f"150x200+{new_x}+{new_y}")

    elif stop_timer_active:
        if time.time() - stop_start_time > current_stop_duration:
            moving = True
            stop_timer_active = False
            determine_new_target()
            mudar_sprite(SPRITE_WALKING)
            print(f"DEBUG: Random stop duration over. Resuming movement.")
            
            # NOVO: Aleatoriamente escolher entre frase de caminhada ou um fato ao retomar movimento
            if random.random() < 0.5: # 50% de chance de ser um fato
                random_fact = random.choice(random_fact_phrases)
                show_speech_bubble(random_fact, duration=3)
            else:
                random_phrase = random.choice(walking_phrases)
                show_speech_bubble(random_phrase, duration=3)

    root.after(50, mover_personagem_suave)

# Function to handle the initial mouse press (start of a click or drag)
def on_mouse_press(event):
    global drag_start_x, drag_start_y, is_dragging, moving, stop_timer_active
    print("DEBUG: Mouse button pressed.")

    is_dragging = False
    
    drag_start_x = event.x
    drag_start_y = event.y

    moving = False
    stop_timer_active = False
    entrada.place_forget()
    mudar_sprite(SPRITE_IDLE)
    hide_speech_bubble()

    label.bind("<B1-Motion>", on_motion_check)
    label.bind("<ButtonRelease-1>", on_mouse_release)

# Function to check for significant motion to confirm a drag
def on_motion_check(event):
    global is_dragging
    move_threshold = 5
    
    current_mouse_screen_x = root.winfo_x() + event.x
    current_mouse_screen_y = root.winfo_y() + event.y

    initial_click_screen_x = root.winfo_x() + drag_start_x
    initial_click_screen_y = root.winfo_y() + drag_start_y

    distance = ((current_mouse_screen_x - initial_click_screen_x)**2 + \
                (current_mouse_screen_y - initial_click_screen_y)**2)**0.5

    if not is_dragging and distance > move_threshold:
        is_dragging = True
        print("DEBUG: Drag initiated (movement detected).")
        mudar_sprite(SPRITE_DRAGGING)
        hide_speech_bubble()
        on_drag_motion(event)
    elif is_dragging:
        on_drag_motion(event)

# Function to handle dragging motion (actual window movement)
def on_drag_motion(event):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    new_x_window = root.winfo_x() + event.x - drag_start_x
    new_y_window = root.winfo_y() + event.y - drag_start_y

    char_width = 150
    char_height = 200

    new_x_window = max(0, min(new_x_window, screen_width - char_width))
    new_y_window = max(0, min(new_y_window, screen_height - char_height))

    root.geometry(f"150x200+{new_x_window}+{new_y_window}")


# Function to handle mouse button release (decide if it was click or drag)
def on_mouse_release(event):
    global is_dragging
    print("DEBUG: Mouse button released.")

    label.unbind("<B1-Motion>")
    label.unbind("<ButtonRelease-1>")

    if is_dragging:
        print("DEBUG: Drag operation finished.")
        on_drag_release()
    else:
        print("DEBUG: Click operation detected.")
        on_click_command_action()

# Function to resume movement after a drag
def on_drag_release():
    global moving, manual_stop_mode
    if manual_stop_mode:
        moving = False
        mudar_sprite(SPRITE_STAY)
        print("DEBUG: Returned to manual stop mode after drag.")
        show_speech_bubble("De volta ao meu posto.")
    else:
        moving = True
        determine_new_target()
        mudar_sprite(SPRITE_WALKING)
        mover_personagem_suave()
        print("DEBUG: Resumed normal movement after drag.")
        show_speech_bubble("Vamos passear!")

# Function to handle action for a confirmed click (show command input)
def on_click_command_action():
    global moving, stop_timer_active
    moving = False
    stop_timer_active = False
    entrada.place(x=10, y=160)
    entrada.focus()
    show_speech_bubble("Diga o comando:", duration=5)

# Function: To start walking after the idle phase (after initial spawn/idle)
def start_walking_after_idle():
    global moving
    moving = True
    determine_new_target()
    mudar_sprite(SPRITE_WALKING)
    mover_personagem_suave()
    print("DEBUG: Transitioned from idle after spawn, now walking.")
    show_speech_bubble("Olá, sou seu assistente!")

# Function: To handle the transition after the spawn sprite
def start_initial_movement():
    mudar_sprite(SPRITE_IDLE)
    print("DEBUG: Spawn sprite hidden, now in idle for 1 second.")
    root.after(1000, start_walking_after_idle)

# When pressing Enter in the command input field
def ao_digitar(event):
    global moving
    comando = entrada.get()
    print(f"DEBUG: Command received: '{comando}'")
    entrada.delete(0, 'end')
    entrada.place_forget()
    executar_comando(comando)

# --- End Function Definitions ---


# --- Main Program Execution ---
# Create floating window
root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "white")
root.geometry("150x200+10+10")
root.configure(bg="white")

# Initial image loading (using the PyInstaller-compatible path logic)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

initial_sprite_path = os.path.join(base_path, "sprites", f"{SPRITE_SPAWN}.png")
try:
    imagem = Image.open(initial_sprite_path).resize((150, 150))
except FileNotFoundError:
    print(f"ERROR: Could not find initial sprite: {initial_sprite_path}. Please ensure it exists.")
    imagem = Image.new('RGBA', (150, 150), (255, 255, 255, 0))
imagem_tk = ImageTk.PhotoImage(imagem)

label = tk.Label(root, image=imagem_tk, bg="black", borderwidth=0, highlightthickness=0)
label.place(x=0, y=0) 
label.bind("<Button-1>", on_mouse_press)

# Hidden input until clicked
entrada = tk.Entry(root, font=("Arial", 12), bg="#F0F0F0") 
entrada.bind("<Return>", ao_digitar)

# Schedule the spawn sprite to be shown for 0.5 seconds, then transition to idle
root.after(500, start_initial_movement)

root.mainloop()