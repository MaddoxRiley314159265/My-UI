class c:
    def __init__(self, x, y = None) -> None:
        try:
            self.x = x[0]
            self.y = x[1]
        except:
            self.x = x
            self.y = y

    def t(self):
        return (self.x, self.y)
    
    def __eq__(self, other):
        if isinstance(other, c):
            return self.x==other.x and self.y==other.y
        return False

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    def __int__(self):
        return c(int(self.x, int(self.y)))
    def __getitem__(self, index : int):
        if isinstance(index, int):
            if index==0: return self.x
            elif index==1: return self.y
        return None
    
    def __add__(self, other):
        if isinstance(other, c):
            return c(self.x+other.x, self.y+other.y)
        return None
    def __sub__(self, other):
        if isinstance(other, c):
            return c(self.x-other.x, self.y-other.y)
        return None
    
    def __mul__(self, scalar):
        if isinstance(scalar, int) or isinstance(scalar, float):
            return c(self.x*scalar, self.y*scalar)
        return None
    def __div__(self, scalar):
        if isinstance(scalar, int) or isinstance(scalar, float):
            return c(self.x/scalar, self.y/scalar)
        return None
    def __floordiv__(self, scalar):
        if isinstance(scalar, int) or isinstance(scalar, float):
            return c(int(self.x/scalar), int(self.y/scalar))
        return None
