# Eliptic Curve Cryptography
class FieldElement:
  def __init__(self, num, prime):
    if num >= prime or num < 0:
      error = 'Num {} not in field range 0 to {}'.format(num, prime-1)
      raise ValueError(error)

    self.num = num
    self.prime = prime

  def __repr__(self):
    return 'FieldElement_{}({})'.format(self.prime, self.num)
  
  def __eq__(self, other):
    if other is None:
      return False
    return self.num == other.num and self.prime == other.prime

  def __ne__(self, other):
    return not (self == other)

  def __add__(self, other):
    if self.prime != other.prime:
      raise TypeError('Cannot add two numbers in different fields!')
    num = (self.num + other.num) % self.prime
    return self.__class__(num, self.prime)

  def __sub__(self, other):
    if self.prime != other.prime:
      raise TypeError('Cannot subtract two numbers in different fields!')
    num = (self.num - other.num) % self.prime
    return self.__class__(num, self.prime)

  def __mul__(self, other):
    if self.prime != other.prime:
      raise TypeError('Cannot multiply two numbers in different fields!')
    num = (self.num * other.num) % self.prime
    return self.__class__(num, self.prime)

  def __pow__(self, exponent):
    n = exponent % (self.prime - 1)
    num = pow(self.num, n, self.prime)
    return self.__class__(num, self.prime)

  def __truediv__(self, other):
    if self.prime != other.prime:
      raise TypeError('Cannot divide two numbers in different fields!')
    num = self.num * pow(other.num, self.prime - 2, self.prime) % self.prime
    return self.__class__(num, self.prime)

  def __rmul__(self, coefficient):
    num = (self.num * coefficient) % self.prime
    return self.__class__(num=num, prime=self.prime)

class Point:
  C1 = 2
  C2 = 3
  def __init__(self, x, y, a, b):
    self.a = a
    self.b = b
    self.x = x
    self.y = y
    
    if (self.x is None) and (self.y is None): #(None, None) is the infinity point
      return
    if self.y**2 != self.x**3 + a * x + b:
      raise ValueError('({}, {}) is not on the curve.'.format(self.x, self.y))

  def __repr__(self):
    if self.x is None:
      return 'Point(infinity)'
    return 'Point({}, {})_{}_{}'.format(self.x, self.y, self.a, self.b)

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b

  def __ne__(self, other):
    return not (self == other)

  def __add__(self, other):
    if (self.a != other.a) or (self.b != other.b):
      raise TypeError('Points {}, {} are not on the same curve'.format(self, other))

    if self.x is None:
      return other
    elif other.x is None:
      return self
    elif self.x == other.x and self.y != other.y:
      return self.__class__(None, None, self.a, self.b)
    elif self.x != other.x:
      s = (other.y - self.y)/(other.x - self.x)
      x3 = pow(s, 2) - self.x - other.x
      y3 = s * (self.x - x3) - self.y
      return self.__class__(x3, y3, self.a, self.b)
    elif self == other and self.y == 0 * self.x:
      return self.__class__(None, None, self.a, self.b)
    elif self == other:
      s = (3 * pow(self.x, 2) + self.a)/(2 * self.y)
      x3 = pow(s, 2) - 2 * self.x
      y3 = s * (self.x - x3) - self.y
      return self.__class__(x3, y3, self.a, self.b)
    else:
      raise ValueError('Addition definition not found for {} + {}'.format(self, other))

  def __rmul__(self, coefficient):
    coef = coefficient
    current = self
    result = self.__class__(None, None, self.a, self.b)
    while coef:
      if coef & 1:
        result += current
      current += current
      coef >>= 1
    return result


