class Hey:
	class innerHey:
		def __init__(self,ok):
			self.yo = ok
		def something(self):
			print(super.hey)

	def __init__(self,ok,ok2):
		self.hey = ok
		self.inner = innerHey(ok2)



hey = Hey("hey","yop")
hey.inner.something()

