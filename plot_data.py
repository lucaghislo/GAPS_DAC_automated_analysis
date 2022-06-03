# importing the required module
import matplotlib.pyplot as plt

with open("readings.txt") as f:
    mylist = f.read().splitlines() 
  
# x axis values
x = [*range(1, 1, 256)]
# corresponding y axis values
y = [float(x) for x in mylist]

print(x)
print(y)

print(len(y))
  
# plotting the points 
plt.plot(x, y)
  
# naming the x axis
plt.xlabel('x - axis')
# naming the y axis
plt.ylabel('y - axis')
  
# giving a title to my graph
plt.title('My first graph!')
  
# function to show the plot
plt.show()