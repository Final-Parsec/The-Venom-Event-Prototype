from random import randint


map_name = 'resources/maps/auto_gen_world.csv'

map_width = 2506
map_height = 687

map_matrix = [['' for x in xrange(map_width)] for y in xrange(map_height)]


# wrap a border around it
for width_index in xrange(map_width):
    map_matrix[0][width_index] = 'X'
    map_matrix[map_height-1][width_index] = 'X'

for height_index in xrange(map_height):
    map_matrix[height_index][0] = 'X'
    map_matrix[height_index][map_width-1] = 'X'


# draw boxes onto map
for i in xrange(100):
    collision = False

    width = randint(40, 150)
    height = randint(5, 20)

    top_left_x = randint(width, map_width-(width+1))
    top_left_y = randint(100, map_height-(height+1)) - randint(100, map_height-100)

    for x in xrange(width):
        collision = collision or map_matrix[top_left_y][top_left_x+x] == 'x'
        collision = collision or map_matrix[top_left_y+height][top_left_x+x] == 'x'

    for y in xrange(height):
        collision = collision or map_matrix[top_left_y+y][top_left_x] == 'x'
        collision = collision or map_matrix[top_left_y+y][top_left_x+width] == 'x'
    collision = collision or map_matrix[top_left_y+height][top_left_x+width] == 'g-1'

    if not collision:
        for x in xrange(width):
            map_matrix[top_left_y][top_left_x+x] = 'x'
            map_matrix[top_left_y+height][top_left_x+x] = 'x'

        for y in xrange(height):
            map_matrix[top_left_y+y][top_left_x] = 'x'
            map_matrix[top_left_y+y][top_left_x+width] = 'x'
        map_matrix[top_left_y+height][top_left_x+width] = ('g-1' if randint(0, 1) == 0 else 'destructible-4')


# draw 25x40 player
top_left_x = randint(25, map_width-25)
top_left_y = randint(40, map_height-40)
for x in xrange(25):
    map_matrix[top_left_y][top_left_x+x] = 'p'
    map_matrix[top_left_y+40][top_left_x+x] = 'p'

for y in xrange(40):
    map_matrix[top_left_y+y][top_left_x] = 'p'
    map_matrix[top_left_y+y][top_left_x+25] = 'p'
map_matrix[top_left_y+40][top_left_x+25] = 'pioneer-pioneer-0.0-2000.0'


# write to file
with open(map_name, 'wb') as output_file:
    for row in map_matrix:
        output_file.write(','.join(row) + '\n')