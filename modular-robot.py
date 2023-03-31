#from ure import DOTALL
from machine import Pin, PWM
from time import sleep

class Servo:
    def __init__(self,pin = 0) -> None:
        self._pwm = PWM(Pin(pin))
        self._duty_ms = 20
        self._pwm.freq(int(1000/self._duty_ms))
        self._duty_max = 255*255 # 65025
        self._min_width_ms = 0.5 # 0 degree pulse width in ms
        self._max_width_ms = 2.5 # full degree pulse width in ms
        self._min_pos = 0
        self._max_pos = 180
        
        self._position = 0
        
        #speed up calcs
        self._offset = int(self._min_width_ms / self._duty_ms * self._duty_max)
        self._scale  = int(( self._max_width_ms - self._min_width_ms ) / self._duty_ms * self._duty_max)
        self._top    = int(self._max_width_ms / self._duty_ms * self._duty_max)
    
    def GetPosition(self):
        return self._position

    def SetPosition(self,pos):
        if pos < 0 : pos = self._min_pos
        if pos > self._max_pos : pos = self._max_pos
        
        self._position = pos
        
        percents = pos/self._max_pos
        
        duty = int(percents*self._scale + self._offset)
        if duty < self._offset : duty = self._offset
        if duty > self._top : duty = self._top
    
        #print("set pos = {deg} ({dut})".format(deg = pos,dut = duty))
    
        self._pwm.duty_u16(duty)


Motion = []
Points = []

def clear(): #Czyszczenie okna terminala
    print("\x1B\x5B2J", end="")
    print("\x1B\x5BH", end="")

def int_input(): #Zabezpieczony input liczb by przy wprowadzeniu złego znaku nie psuło programu
    while True:
        x = input("-> ")
        try: int(x)
        except ValueError:
            print("To nie jest liczba!")
        else:
            y = int(x)
            return y

def float_input(): #Zabezpieczony input liczb by przy wprowadzeniu złego znaku nie psuło programu
    while True:
        x = input("-> ")
        try: float(x)
        except ValueError:
            print("To nie jest liczba!")
        else:
            y = float(x)
            return y

def move(pos, Servo): #Zmiana pozycji serwa o określony kąt
    Servo.SetPosition(Servo.GetPosition() + pos)
    print('Pozycja po obrocie =',Servo.GetPosition())

def show_position(Motion, ileModulow):
     for i in range(0, ileModulow):
        print('M',ileModulow-i,'->',Motion[(i*2)-2].GetPosition(),',',Motion[(i*2)-1].GetPosition(),';')   

def show_point(Point, punkt, ileModulow): #Wyświetlenie punktu
    print('Punkt P[', punkt,']')
    for i in range(0, ileModulow):
        print('M',ileModulow-i,'->',Point[(i*2)-2].GetPosition(),',',Point[(i*2)-1].GetPosition(),';')

def show_points(Points, ileModulow): #Lista punktów
    for i in range(0, len(Points)):
        show_point(Points[i], i, ileModulow)

def manipulation(Motion): #Sterowanie robotem - obrót o kąt
    while True:
        print("\nWybierz numer modulu, ktorym chcesz wykonac obrot")
        wybor = int_input()
        if wybor <= (len(Motion)/2) and wybor > 0:
            break
        print("Nie ma takiego modulu!\n")

    print('\nMODUL ',wybor)
    numerPortu = (wybor*2)- 1

    print('Serwo 1 (PORT',numerPortu-1,'), Pozycja = ', Motion[numerPortu-1].GetPosition())
    print("Wprowadz kat obrotu")
    pos = int(int_input())
    move(pos, Motion[numerPortu-1])

    print('\nSerwo 2 (PORT',numerPortu,'), Pozycja = ', Motion[numerPortu].GetPosition())
    print("Wprowadz kat obrotu")
    pos = int(int_input())
    move(pos, Motion[numerPortu])
    return Motion 

def position(Motion): #Sterowanie robotem - ustawienie na określoną pozycję
    while True:
        print("\nWybierz numer modulu, ktorego pozycje chcesz zmienic")
        wybor = int_input()
        if wybor <= (len(Motion)/2) and wybor > 0:
            break
        print("Nie ma takiego modulu!\n")

    print('\nMODUL ',wybor)
    numerPortu = (wybor*2)- 1

    print('Serwo 1 (PORT',numerPortu-1,'), Pozycja = ', Motion[numerPortu-1].GetPosition())
    print("Okresl pozycje")
    pos = int(int_input())
    Motion[numerPortu - 1].SetPosition(pos)

    print('\nSerwo 2 (PORT',numerPortu,'), Pozycja = ', Motion[numerPortu].GetPosition())
    print("Okresl pozycje")
    pos = int(int_input())
    Motion[numerPortu].SetPosition(pos)
    return Motion     

def save_point(Points, Motion, ileModulow): #Zapis punktu
    Motion_add = [] #Tablica pomocnicza
    PointNumber = 1

    for i in range(0, 2*ileModulow): # Tablica ta musi mieć taki sam rozmiar co tablica Motion
        Motion_add.append(Servo(i))
        Motion_add[i].SetPosition(Motion[i].GetPosition())
    
    if len(Points) == 0:
        Points.append(Motion_add)
        PointNumber = 0
    else:
        print("\nWybierz, w ktorym miejscu chcesz dodac nowy punkt\n1 - Na koniec listy\n2 - Przed wybranym punktem\n")
        choose1 = int_input()
        if choose1 == 1:
            Points.append(Motion_add)
            PointNumber = len(Points) - 1
        if choose1 == 2:
            print("Podaj, w ktorym miejscu (przed ktorym punktem) ma byc zapisany nowy punkt")
            choose = int_input()
            Points.insert(choose,Motion_add)
            PointNumber = choose

    print('Zapisano jako P',PointNumber,'\n')
    show_point(Points[len(Points)-1], PointNumber, ileModulow)
    return Points

def delete_point(Points):
    print("Wybierz punkt ,ktory chcesz usunac")
    delete = int_input()
    Points.pop(delete)
    return Points

def road(Points, Motion, ileModulow, speed): #Odtwarzanie wyznaczonej trajektori 
    if len(Points) != 0:
        for i in range(0, len(Points)):
            sleep(speed)
            show_point(Points[i], i, ileModulow)
            for j in range(0, 2*ileModulow):
                Point = Points[len(Points)-1-i]
                Motion[j].SetPosition(Point[j].GetPosition())
    else:
        print("Brak wyznaczonych punktow!")

#Main
while True:
    print("Wprowadz ilosc podlaczonych modulow")
    ileModulow = int(int_input())
    if ileModulow <= 8 and ileModulow > 0:
        break
sleep(0.5)
clear()

for i in range(0, 2*ileModulow):
    Motion.append(Servo(i))
    Motion[i].SetPosition(15)

while True: #Menu
    print("//-----------------------------------------//")
    print("//   *******   ROBOT MODULARNY   *******   //")
    print("//-----------------------------------------//\n")
    print("1 - Sterowanie robotem - obrot o kat")
    print("2 - Sterowanie robotem - okresl pozycje\n")
    print("3 - Wyswietl aktualna pozycje robota")
    print("4 - Odtworz zapisana trajektorie\n")
    print("5 - Pokaz zapisane punkty")
    print("6 - Zapisz punkt")
    print("7 - Usun punkt\n")
    print("8 - Wyjdz z programu\n")
    x = int_input()

    if x == 1: # STEROWANIE ROBOTEM
        clear()
        Motion = manipulation(Motion)
        input("Nacisnij Enter by kontynuowac")
        clear()

    if x == 2: # STEROWANIE ROBOTEM - ZMIANA POZYCJI
        clear()
        Motion = position(Motion)
        input("Nacisnij Enter by kontynuowac")
        clear()

    if x == 3: # POZYCJA ROBOTA
        clear()
        print("Aktualna pozycja robota:")
        show_position(Motion, ileModulow)
        input("Nacisnij Enter by kontynuowac")
        clear()

    if x == 4: #TRAJEKTORIA
        clear()
        print("Okresl czas w sekundach oczekiwania miedzy ruchami")
        speed = float_input()
        road(Points, Motion, ileModulow, speed)
        input("Nacisnij Enter by kontynuowac")
        clear()

    if x == 5: #LISTA PUNKTÓW
        clear()
        print("Lista zapisanych punktow:")
        show_points(Points, ileModulow)
        input("Nacisnij Enter by kontynuowac")
        clear()

    if x == 6: #ZAPIS PUNKTU
        clear()
        show_points(Points, ileModulow)
        Points = save_point(Points, Motion, ileModulow)
        input("Nacisnij Enter by kontynuowac")
        clear()

    if x == 7: #USUŃ PUNKT
        clear()
        show_points(Points, ileModulow)
        Points = delete_point(Points)
        clear()

    if x == 8: #ZAKOŃCZ PROGRAM
        break

    if x > 8 or x < 1:
        clear()
        print("Nie ma takiej opcji!\n")
        input("Nacisnij Enter by kontynuowac")
        clear()

    






