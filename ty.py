import turtle
turtle.speed(100)
turtle.color("blue")
for _ in range(36):
    for _ in range (3):
        turtle.pensize(5)
        turtle.forward(100)
        turtle.left(90)
    turtle.pensize(1)
    turtle.forward(100)
    turtle.left(80)
turtle.color("red")
for _ in range(4):
    for _ in range(36):
        for _ in range (3):
            turtle.forward(100)
            turtle.left(90)
            turtle.circle(50)
            turtle.left(10)
        turtle.forward(100)
        turtle.left(80)
    turtle.penup()
    turtle.left(90)
    turtle.forward(50)
    turtle.pendown()
turtle.pensize(3)
turtle.circle(50)




turtle.mainloop()