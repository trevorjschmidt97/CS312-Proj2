from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

	# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
	# Some helper methods that make calls to the GUI, allowing us to send updates
	# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	

	# This is the method that gets called by the GUI and actually executes
	# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE // DONE
		points.sort(key=lambda point: point.x())
		
		# Debugging by printing all points
		print('\nAll points:')
		count = 1
		for point in points: 
			print('\t#', count, point.x(), point.y())
			count += 1
		print('')

		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		self.i = 1
		self.j = 1
		finalList = divide(self, points)
		print('FINAL LIST:')
		for point in finalList:
			print(point)
		polygon = [QLineF(finalList[i],finalList[(i+1)%len(finalList)]) for i in range(len(finalList))]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))


def divide(self, points):
	#Debugging check
	assert( type(points) == list )

	#Base case
	if len(points) <= 1:
		return points

	#Debugging for division checks
	print(self.i, 'Divide')
	print('\tLeft', type(points), points[0:len(points)//2])
	print('\tRight', type(points), points[len(points)//2:])
	self.i += 1

	# Recursive Calls
	leftHalf = divide(self, points[0:len(points)//2])
	rightHalf = divide(self, points[len(points)//2:])

	# Call to merge function
	return merge(self, leftHalf, rightHalf)

def merge(self, leftHalf, rightHalf):
	#Debugging Checks
	assert ( type(leftHalf) == list and type(rightHalf) == list)
	print(self.j, 'Merge')
	self.j += 1
	print('\tLeft', type(leftHalf), leftHalf)
	print('\tRight', type(rightHalf), rightHalf)

	#Grab rightmostofleft/leftmostofright points
	rightmostOfLeft = max(leftHalf, key = lambda point:point.x())
	indexRightMostOfLeft = 0
	for i in range(len(leftHalf)):
		if leftHalf[i] == rightmostOfLeft:
			indexRightMostOfLeft = i

	leftmostOfRight = min(rightHalf, key = lambda point:point.x())
	indexLeftMostOfRight = 0
	for i in range(len(rightHalf)):
		if rightHalf[i] == leftmostOfRight:
			indexLeftMostOfRight = i
	#Debugging checks
	print('\tRightMostOfLeft:', rightmostOfLeft)
	print('\tIndexRightMostOfLeft:', indexRightMostOfLeft)
	print('\tLeftMostOfRight:', leftmostOfRight)
	print('\tIndexLeftMostOfLeft:', indexLeftMostOfRight)

	#Next step is find utl, utr, btl, btr
	#Debugging initial slope
	print('\tInitial Slope:', getSlope(rightmostOfLeft, leftmostOfRight))
	
	currentLeftIndex = indexRightMostOfLeft
	currentRightIndex = indexLeftMostOfRight

	nextLeftIndex = 0
	if currentLeftIndex == 0:
		nextLeftIndex = len(leftHalf) - 1
	else:
		nextLeftIndex = currentLeftIndex - 1

	nextRightIndex = 0
	if currentRightIndex == len(rightHalf) - 1:
		nextRightIndex = 0
	else:
		nextRightIndex = currentRightIndex + 1

	currentSlope = getSlope(leftHalf[currentLeftIndex], rightHalf[currentRightIndex])

	done = 0
	while not done:
		#Assume we're done unless we have to change a point
		done = 1

		# Left half while loop
		while(getSlope(leftHalf[nextLeftIndex], rightHalf[currentRightIndex]) < currentSlope):
			currentSlope = getSlope(leftHalf[nextLeftIndex], rightHalf[currentRightIndex])

			#Reset current left index 
			currentLeftIndex = nextLeftIndex

			#Reset next left index
			if currentLeftIndex == 0:
				nextLeftIndex = len(leftHalf) - 1
			else:
				nextLeftIndex = currentLeftIndex - 1

			done = 0

		# Right half while loop
		while(getSlope(leftHalf[currentLeftIndex], rightHalf[nextRightIndex]) > currentSlope):
			currentSlope = getSlope(leftHalf[currentLeftIndex], rightHalf[nextRightIndex])

			#Reset current right index
			currentRightIndex = nextRightIndex

			#Reset next right index
			if currentRightIndex == len(rightHalf) - 1:
				nextRightIndex = 0
			else:
				nextRightIndex = currentRightIndex + 1

			done = 0

	# Set UpperLeftTangent(ult) and UpperRightTangent(urt)
	ult = currentLeftIndex
	urt = currentRightIndex
	print('\tult:', ult)
	print('\turt:', urt)


	# Finding lower tangents
	currentLeftIndex = indexRightMostOfLeft
	currentRightIndex = indexLeftMostOfRight

	nextLeftIndex = 0
	if currentLeftIndex == len(leftHalf) - 1:
		nextLeftIndex = 0
	else:
		nextLeftIndex = currentLeftIndex + 1

	nextRightIndex = 0
	if currentRightIndex == 0:
		nextRightIndex = len(rightHalf) - 1
	else:
		nextRightIndex = currentRightIndex - 1

	currentSlope = getSlope(leftHalf[currentLeftIndex], rightHalf[currentRightIndex])

	done = 0
	while not done:
		# assume were done unless something changes
		done = 1

		# go through left half
		while(getSlope(leftHalf[nextLeftIndex], rightHalf[currentRightIndex]) > currentSlope):
			#reset slope
			currentSlope = getSlope(leftHalf[nextLeftIndex], rightHalf[currentRightIndex])

			#reset current left index
			currentLeftIndex = nextLeftIndex

			#reset next left index
			if currentLeftIndex == len(leftHalf) - 1:
				nextLeftIndex = 0
			else:
				nextLeftIndex = currentLeftIndex + 1

			done = 0

		# go through right half
		while(getSlope(leftHalf[currentLeftIndex], rightHalf[nextRightIndex]) < currentSlope):
			#reset slope
			currentSlope = getSlope(leftHalf[currentLeftIndex], rightHalf[nextRightIndex])

			# reset current right index
			currentRightIndex = nextRightIndex

			#reset next right index
			if currentRightIndex == 0:
				nextRightIndex = len(rightHalf) - 1
			else:
				nextRightIndex = currentRightIndex - 1

			done = 0

	# Set LowerLeftTangent(llt) and LowerRightTangent(lrt)
	llt = currentLeftIndex
	lrt = currentRightIndex

	#Debugging Prints
	print('\tllt:', llt)
	print('\tlrt:', lrt)
	
	#loop through adding the new points in a clockwise rotation
	returnList = []

	i = 0
	while(i != ult):
		returnList.append(leftHalf[i])
		i += 1
	returnList.append(leftHalf[ult])

	#Debugging Prints
	print('\tFirst While Loop:')
	for point in returnList:
		print('\t', point)

	i = urt
	while(i != lrt):
		returnList.append(rightHalf[i])
		i += 1
	#returnList.append(rightHalf[lrt])

	#Debugging Prints
	print('\tSecond While Loop:')
	for point in returnList:
		print('\t', point)

	i = llt
	while(i != len(leftHalf) - 1):
		returnList.append(leftHalf[i])
		i += 1
	#returnList.append(leftHalf[i])


	#Debugging Prints
	print('\tFinal List:')
	for point in returnList:
		print('\t', point)


	#return that new list, ensureing the first point is the left most point
	return returnList

def getSlope(point1, point2):
	m = (point2.y() - point1.y())/(point2.x() - point1.x())
	return m
