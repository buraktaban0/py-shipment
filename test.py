


class A:

	def f1(self):
		pass

	def f2(self):
		self.f1()
		print('f2')

class B(A):
	
	def f1(self):
		print('f1b')

	def f2(self):
		super().f2()
		print('f2b')			



b = B()

b.f2()		