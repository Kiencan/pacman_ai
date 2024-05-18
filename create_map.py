import tkinter as tk

# Define the tilesets
TILESETS = {
    "%": "Wall",
    ".": "Coin",
    "o": "Capsule",
    "G": "Ghost",
    "P": "Pacman",
    " ": "Empty"
}

class MapEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Map Editor")

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="white")
        self.canvas.pack()

        self.map_data = [
            "%%%%%%%%%%%%%%%%%%%%%%",
            "%............o......%",
            "%.%%%%.%%.%%%%%%%%%%%",
            "%......%%............%",
            "%.%%%%.%%.%%%%%%%%%%.%",
            "%......%%.o..........%",
            "%.%%%%.%%.%%%%%%%%%%.%",
            "%o.....%%............%",
            "%%%%%%%%%%%%%%%%%%%%%%"
        ]

        self.draw_map()

    def draw_map(self):
        self.canvas.delete("all")
        tile_size = 20
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile in TILESETS:
                    tile_name = TILESETS[tile]
                    self.canvas.create_rectangle(
                        x * tile_size,
                        y * tile_size,
                        (x + 1) * tile_size,
                        (y + 1) * tile_size,
                        fill="gray" if tile_name == "Wall" else "white",
                        outline="black"
                    )
                    self.canvas.create_text(
                        x * tile_size + tile_size // 2,
                        y * tile_size + tile_size // 2,
                        text=tile_name
                    )

root = tk.Tk()
app = MapEditor(root)
root.mainloop()