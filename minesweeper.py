from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core. window import Window
import random

class MinesweeperApp(App):
    def build(self):
        self.rows = 10
        self.cols = 10
        self.num_mines = 10
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.exposed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.mine_counts = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        layout = BoxLayout(orientation='vertical')
        self.grid = GridLayout(col=self.cols)
        layout.add_widget(self.grid)

        self.info_label = Label(text="Minesweeper", size_hint_y=0.1)
        layout.add_widget(self.info_label)

        for row in range(self.rows):
            for col in range(self.cols):
                button = Button(size_hint=(None, None), width=40, height=40)
                button.bind(on_release=self.reveal)
                self.grid.add_widget(button)
                self.buttons[row][col] = button

        self.place_mines()

        return layout

    def place_mines(self):
        mines_placed = 0
        while mines_placed < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if not self.mines[r][c]:
                self.mines[r][c] = True
                mines_placed += 1
                self.update_counts(r,c)

    def update_counts(self,r,c):
        for i in range(r - 1, r + 2):
            for j in range(c - 1, c + 2):
                if 0 <= i < self.rows and 0 <= j < self.cols and not self.mines[i][j]:
                    self.mine_counts[i][j] += 1

    def reveal(self, button):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.buttons[row][col]:
                    self.buttons[row][col].text = "M"
                    self.buttons[row][col].background_color = (1,0,0,1)
                    self.info_label.text = "Game Over!"
                    self.show_all_mines()
                else:
                    self.expose_cell(row, col)
                return

    def expose_cell(self,r,c):
        if self.exposed[r][c]:
            return

        self.exposed[r][c] = True
        count = self.mine_counts[r][c]
        if count > 0:
            self.buttons[r][c].text = str(count)
        else:
            self.buttons[r][c].text = ""
            for i in range(r - 1, r + 2):
                for j in range(c - 1, c + 2):
                    if 0 <= i < self.rows and 0 <= j < self.cols:
                        self.expose_cell(i, j)

    def show_all_mines(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.mines[row][col]:
                    self.buttons[row][col].text = "M"
                    self.buttons[row][col].background_color = (1,0,0,1)

if __name__ == '__main__':
    MinesweeperApp().run()