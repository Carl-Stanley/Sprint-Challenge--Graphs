from room import Room
from player import Player
from world import World

import random
from ast import literal_eval
import time
import os
import queue
import multiprocessing
import random

def get_path(path):
     
    directions = []

    for i in range(len(path) - 1):
        room = path[i]
        next_room = path[i + 1]

        for direction in room.get_exits():
            if next_room == room.get_room_in_direction(direction):
                directions.append(direction)

    return directions

def get_route_inbounds(world, limit=None):
     

    r = multiprocessing.Queue()
    jobs = []
    
    for i in range(1, os.cpu_count()):
        p = multiprocessing.Process(target=route_finder_dft, args=(world, r, limit))
        jobs.append(p)
        p.start()

    path = r.get(True)

    for p in jobs:
        p.kill()

    return path
    
def get_shortest_route(world):
     

    q = multiprocessing.Queue()
    r = multiprocessing.Queue()
    jobs = []

    q.put(([world.starting_room], set([world.starting_room.id])))    

    route_finder(world, q, r)

    min_length = None
    min_path = None
    for i in range(r.qsize()):
        path = r.get()
        path_len = len(path)
        if min_length == None or path_len < min_length:
            min_length = path_len
            min_path = path
    
    return min_path




def route_finder(world, q, r, limit=None):
     
    while True:
        try:
            path, visited = q.get(True, 0.5)
        except:
            break

        room = path[-1]

        if limit:
            if len(path) > limit:
                break

        if len(visited) < len(world.rooms):
            dead_end = True
            for direction in room.get_exits():
                next_room = room.get_room_in_direction(direction)
                if next_room:
                    if not next_room.id in visited:
                        next_path = [*path, next_room]
                        next_visited = visited.copy()
                        next_visited.add(next_room.id)
                        q.put((next_path, next_visited))
                        dead_end = False
            
            if dead_end:
                next_path = shortest_unvisited_route(path, visited, limit)
                if next_path:
                    q.put((next_path, visited))
                else:
                    break
        else:
            r.put(path)

def route_finder_dft(world, r, limit=None):
     
    while True:  
        room = world.starting_room
        path = [room]
        visited = set()
        visited.add(room.id)

        while True:  
            if len(visited) < len(world.rooms):
                room = path[-1]

                if limit:
                    if len(path) > limit:
                        break

                 
                rooms = map(room.get_room_in_direction, room.get_exits())
                rooms = [*filter(lambda room: not room.id in visited, rooms)]
                if len(rooms):
                    next_room = random.choice(rooms)
                    path.append(next_room)
                    visited.add(next_room.id)
                else:
                    path = shortest_unvisited_route(path, visited, limit)
                    if not path:
                        break
            else:
                r.put(path)
                break

def shortest_unvisited_route(path, visited, limit=None):
     
    temp_visited = set()
    q = queue.Queue()
    q.put(path)

    while True:
        path = q.get()
        room = path[-1]
        if limit:
            if len(path) > limit:
                return None
        if not room.id in temp_visited:
            temp_visited.add(room.id)
            for direction in room.get_exits():
                next_room = room.get_room_in_direction(direction)
                if not next_room.id in visited:
                    return path
                q.put([*path, next_room])

def main():
    
    world = World()

    # You may uncomment the smaller graphs for development and testing purposes.
    # map_file = "maps/test_line.txt"
    # map_file = "maps/test_cross.txt"
    # map_file = "maps/test_loop.txt"
    # map_file = "maps/test_loop_fork.txt"
    
    map_file = "maps/main_maze.txt"

    # Loads the map into a dictionary
    room_graph=literal_eval(open(map_file, "r").read())
    world.load_graph(room_graph)

    # Print an ASCII map
    world.print_rooms()

    player = Player(world.starting_room)

    # Fill this out with directions to walk
    # traversal_path = ['n', 'n']

    start_time = time.time()
    
    # traversal_path = get_path(get_shortest_route(world))
    traversal_path = get_path(get_route_inbounds(world, 960))
    
    print(f'{(time.time() - start_time):.2f}s')
    # print(f'traversal_path:\n{traversal_path}')

    # TRAVERSAL TEST
    visited_rooms = set()
    player.current_room = world.starting_room
    visited_rooms.add(player.current_room)

    for move in traversal_path:
        player.travel(move)
        visited_rooms.add(player.current_room)

    if len(visited_rooms) == len(room_graph):
        print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
    else:
        print("TESTS FAILED: INCOMPLETE TRAVERSAL")
        print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")

    #######
    # UNCOMMENT TO WALK AROUND
    #######
    # player.current_room.print_room_description(player)
    # while True:
    #     cmds = input("-> ").lower().split(" ")
    #     if cmds[0] in ["n", "s", "e", "w"]:
    #         player.travel(cmds[0], True)
    #     elif cmds[0] == "q":
    #         break
    #     else:
    #         print("I did not understand that command.")

if __name__ == "__main__":
    main()
