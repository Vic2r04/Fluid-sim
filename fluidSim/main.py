import pygame
import math
from functions import *
from cell import Cell
import random

# Settings
kcfl = 1
fps = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# initialize pygame
pygame.init()

screenHeight = 1200
screenWidth = 1200

screen_size = (screenWidth, screenHeight)
 
# create a window
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Fluid simulation")
programIcon = pygame.image.load("./images/droplet.png")
pygame.display.set_icon(programIcon)
 
# clock is used to set a max fps
clock = pygame.time.Clock()
running = True

cellSize = 30 # length of all sides
gridHeight = math.floor(screenHeight/cellSize)
gridWidth = math.floor(screenWidth/cellSize)
grid = [[Cell(x, y) for x in range(gridWidth)] for y in range(gridHeight)]

particles = [[random.randint(0, screenWidth), random.randint(0, screenHeight)] for x in range(3000)]

def drawVelVec():
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            current = grid[y][x]
            xVel = current.vel[0] * 20
            yVel = current.vel[1] * 20

            pygame.draw.line(screen, RED, [x*cellSize, y*cellSize+cellSize/2], [x*cellSize+xVel, y*cellSize+cellSize/2], width=3)
            pygame.draw.line(screen, RED, [x*cellSize+cellSize/2, y*cellSize], [x*cellSize+cellSize/2, y*cellSize+yVel], width=3)


def drawGrid():
    # paint densities
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            c = [max(grid[y][x].density/10 * i, 0) for i in [255, 255, 255]]
            pygame.draw.rect(screen, c, pygame.Rect(x*cellSize, y*cellSize, cellSize, cellSize))
    
    # draw lines
    for i in range(1, gridHeight):
        pygame.draw.line(screen, WHITE, (0, i*int(screenHeight/gridHeight)), (screenWidth, i*int(screenHeight/gridHeight)))
    
    for i in range(1, gridWidth):
        pygame.draw.line(screen, WHITE, (i*int(screenWidth/gridWidth), 0), (i*int(screenWidth/gridWidth), screenHeight))

def drawParticles():
    for p in particles:
        pygame.draw.circle(screen, (0,0,255), p, 5)

def pressureSolve():
    highestDivergence = math.inf
    while highestDivergence > .1:
        highestDivergence = 0
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                current = grid[y][x]

                s = 0    
                
                xDivergence = 0
                if x > 0:
                    xDivergence += current.vel[0]
                    s += 1
                if x < len(grid[y]) - 1:
                    right = grid[y][x+1]
                    xDivergence -= right.vel[0]
                    s += 1

                yDivergence = 0                
                if y > 0:
                    yDivergence += current.vel[1]
                    s += 1
                if y < len(grid) - 1:
                    below = grid[y+1][x]
                    yDivergence -= below.vel[1]
                    s += 1

                divergence = (xDivergence + yDivergence)*1.9


                if divergence > highestDivergence:
                    highestDivergence = divergence

                if x > 0:
                    current.vel[0] -= divergence/s
                else:
                    current.vel[0] *= -1
                if x < len(grid[y]) - 1:
                    right.vel[0] += divergence/s
                else:
                    right.vel[0] *= -1
                if y > 0:
                    current.vel[1] -= divergence/s
                else:
                    current.vel[1] *= -1
                if y < len(grid) - 1:
                    below.vel[1] += divergence/s
                else:
                    below.vel[1] *= -1


def convect(timestep):
    for row in grid:
        for cell in row:
            # solving for x-velocity
            xPos = cellSize*cell.x
            yPos = cellSize*cell.y + 0.5*cellSize

            yVel = getInterpolatedValue(grid, xPos/cellSize-0.5, yPos/cellSize, 1)
            xVel = cell.vel[0]

            cell.nextVel[0] = getInterpolatedValue(grid, (xPos-xVel*timestep)/cellSize, (yPos-yVel*timestep)/cellSize-0.5, 0)

            # solving for y-velocity
            xPos = cellSize*cell.x + 0.5*cellSize
            yPos = cellSize*cell.y

            xVel = getInterpolatedValue(grid, xPos/cellSize, yPos/cellSize-0.5, 0)
            yVel = cell.vel[1]

            cell.nextVel[1] = getInterpolatedValue(grid, (xPos-xVel*timestep)/cellSize-0.5, (yPos-yVel*timestep)/cellSize,1)

def updateParticles():
    for i in range(len(particles)):
        p = particles[i]
        xVel = getInterpolatedValue(grid, p[0]/cellSize, p[1]/cellSize-0.5, 0)
        yVel = getInterpolatedValue(grid, p[0]/cellSize-0.5, p[1]/cellSize, 1)
        
        p[0] += xVel
        p[1] += yVel

def calculateTimeStep():
    maxVel = grid[0][0].vel[0]
    for row in grid:
        for cell in row:
            for v in cell.vel:
                if v > maxVel:
                    maxVel = v

    return kcfl*cellSize/maxVel

def applyGravity(time_step):
    for row in grid:
        for cell in row:
            cell.vel[1] += 9.82 * time_step


def updateVel():
    for row in grid:
        for cell in row:
            cell.vel = cell.nextVel.copy()
            cell.nextVel = [0, 0]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #clear the screen
    screen.fill((0, 0, 0))

    # update time step
    time_step = calculateTimeStep()
    for i in range(math.ceil((1/fps)/time_step)):

        # advance velocity field
        convect(time_step)
        applyGravity(time_step)
        updateVel()
        pressureSolve()

        # update particles
        updateParticles()

    # draw to the screen
    drawGrid()
    drawVelVec()
    drawParticles()

    if pygame.mouse.get_pressed()[0]:
        x,y = pygame.mouse.get_pos()
        x /= cellSize
        y /= cellSize

        grid[int(y)][int(x)].border = True

 
    # flip() updates the screen to make our changes visible
    pygame.display.flip()
    pygame.display.update()
     
    # how many updates per second
    clock.tick(fps)
 
pygame.quit()