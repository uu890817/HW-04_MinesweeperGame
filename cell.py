from tkinter import Button, Label
import random
import settings
import ctypes
import sys


class Cell:
    all = []
    cell_count = settings.CELL_COUNT
    cell_count_label_object = None
    def __init__(self,x, y, is_mine=False):
        self.is_mine = is_mine
        self.is_opened = False
        self.is_mine_candidate = False
        self.cell_btn_object = None
        self.is_zero = False #(新增)周圍炸彈數量是否為0
        self.x = x
        self.y = y

        # Append the object to the Cell.all list
        Cell.all.append(self)

    def create_btn_object(self, location):
        btn = Button(
            location,
            width=12,
            height=4,
        )
        btn.bind('<Button-1>', self.left_click_actions ) # Left Click
        btn.bind('<Button-3>', self.right_click_actions ) # Right Click
        self.cell_btn_object = btn

    @staticmethod
    def create_cell_count_label(location):
        lbl = Label(
            location,
            bg='green',
            fg='white',
            text=f"Cells Left:{Cell.cell_count}",
            font=("", 30)
        )
        Cell.cell_count_label_object = lbl
#----------------第一次不要按到地雷----------------#
    @staticmethod
    def reset_mines():
        for pick_reset in Cell.all:
            pick_reset.is_mine = False
    def left_click_actions(self, event):

        print("\n-------點選位置:","(",self.x,",",self.y,")","是否為炸彈:",self.is_mine,"剩餘格數:",self.cell_count,"-------")     #DeBug用
        if self.is_mine == True and self.cell_count == settings.CELL_COUNT:     #判斷第一次點即是否為地雷
            print("------------觸發地雷重置------------")                        #DeBug用
            self.reset_mines()                                 #清除地雷
            Cell.randomize_mines()                             #重新排放地雷
            self.left_click_actions(event)                     
            return                                             
        #print(event)  #DeBug用
#----------------第一次不要按到地雷 END----------------#
        #for cell_zero in self.all:
        #    cell_zero.is_zero = False

        if self.is_mine:
            self.show_mine()
        else:
            if self.count_mines(self) == 0:
                self.around_show_cell(self)
                self.is_zero = True
                for cell_obj in self.get_surrounded_cells(self.x,self.y):
                    self.around_show_cell(cell_obj)
                    if self.count_mines(cell_obj) == 0:
                        cell_obj.is_zero = True
                        self.get_around_and_show_cell(cell_obj)
            self.around_show_cell(self)
            self.cell_btn_object.configure(bg='#66CCFF')#SystemButtonFace #標記按下位置
            
            # If Mines count is equal to the cells left count, player won
            if Cell.cell_count == settings.MINES_COUNT:
                ctypes.windll.user32.MessageBoxW(0, 'Congratulations! You won the game!', 'Game Over', 0)
                exit()

        # Cancel Left and Right click events if cell is already opened:
        self.cell_btn_object.unbind('<Button-1>')
        self.cell_btn_object.unbind('<Button-3>')

    def get_cell_by_axis(self, x,y):
        # Return a cell object based on the value of x,y
        for cell in Cell.all:
            if cell.x == x and cell.y == y:
                return cell
##-------------------------新增或修改部分-------------------------##
    def get_surrounded_cells(self,input_x,input_y): #取得周圍8格CELL #原本的surrounded_cells()
        cells = [
            self.get_cell_by_axis(input_x - 1, input_y -1 ), #左上
            self.get_cell_by_axis(input_x - 1, input_y    ), #左
            self.get_cell_by_axis(input_x - 1, input_y + 1), #左下
            self.get_cell_by_axis(input_x,     input_y - 1), #正上
            self.get_cell_by_axis(input_x + 1, input_y - 1), #右上
            self.get_cell_by_axis(input_x + 1, input_y    ), #右
            self.get_cell_by_axis(input_x + 1, input_y + 1), #右下
            self.get_cell_by_axis(input_x,     input_y + 1)  #正下
        ]
        cells = [cell for cell in cells if cell is not None]
        return cells

    def count_mines(self,input_cell): #計算周圍炸彈數量  #原本的surrounded_cells_mines_length()
        
        counter = 0
        for cell in self.get_surrounded_cells(input_cell.x,input_cell.y):
            if cell.is_mine:
                counter += 1
        return counter

    def get_around_and_show_cell(self,input_cell): #取得周圍並開啟為0的部分
        #print("\nget_around_and_show_cell ->","input_cell:",input_cell)
        cells = self.get_surrounded_cells(input_cell.x,input_cell.y)
        counter = self.count_mines(input_cell)
        if counter == 0 :
            for cell in cells:
                #解除cell的按鍵綁定
                cell.cell_btn_object.unbind('<Button-1>')
                cell.cell_btn_object.unbind('<Button-3>')
                if self.count_mines(cell) == 0 and cell.is_zero == False :
                    cell.is_zero = True
                    self.get_around_and_show_cell(cell)#遞迴
                self.around_show_cell(cell)    
        self.around_show_cell(input_cell)
    
        #print("get_around_and_show_cell ->",input_cell ,"counter:",counter)
        return

    def around_show_cell(self,input_cell): #原本的show_cell()
        if not input_cell.is_opened:
            #print("around_show_cell() -> 本次開啟:",input_cell,"周圍炸彈數量",self.count_mines(input_cell))
            Cell.cell_count -= 1
            input_cell.cell_btn_object.configure(text=self.count_mines(input_cell))
            if Cell.cell_count_label_object:
                Cell.cell_count_label_object.configure(text=f"Cells Left:{Cell.cell_count}")

            input_cell.cell_btn_object.configure(
                 bg='gray'#SystemButtonFace
                 )
            
        input_cell.is_opened = True
        

##------------------------新增或修改部分END------------------------##

    def show_mine(self):
        self.cell_btn_object.configure(bg='red')
        print("\n************爆炸************\n")
        ctypes.windll.user32.MessageBoxW(0, 'You clicked on a mine', 'Game Over', 0)
        sys.exit()


    def right_click_actions(self, event):
        if not self.is_mine_candidate:
            self.cell_btn_object.configure(
                bg='orange'
            )
            self.is_mine_candidate = True
        else:
            self.cell_btn_object.configure(
                bg='SystemButtonFace'
            )
            self.is_mine_candidate = False

    @staticmethod
    def randomize_mines():
        
        picked_cells = random.sample(
            Cell.all, settings.MINES_COUNT
        )

        for picked_cell in picked_cells:
            picked_cell.is_mine = True
            
        print("\n地雷位置:\n",picked_cells)#DeBug用
        
    def __repr__(self):
        return f"Cell({self.x}, {self.y})"