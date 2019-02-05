# Intersection Model

## Summary

A simple model of an intersection with cars as agents. All agents start at one of four starting points at its maximum velocity. The four roads lead towards an intersection of which we would like the dynamics. There are four types of intersections; 

### Fourway
This intersection type uses a first come first serve principle. Cars with a high enough Better Move out of my Way factor (BMW factor) will not honour this rule and go immediately.

### Equivalent
This intersection type implies that a car coming from the right has priority. 

### Traffic lights
This intersection type uses simple traffic lights to regulate the traffic. All the roads will have red light except for one. The green light cycles through the roads clockwise where each road will have green light for a fixed number of steps.

### Smart traffice lights
This intersection is equivalent to the simple traffic lights. The difference is that the smart traffic lights keep track of the waiting cars and gives priority to the lane with the most cars.

## How to run the mesa server

To launch the mesa server, run:

```
    $ python run.py
```

If your browser doesn't open automatically, point it to [http://localhost:8523/](http://localhost:8523/). When the visualization loads, press Reset, then Run.

## How to run the jupyter notebook for graphs

To launch the jupyter notebook, run:

```
    $ jupyter notebook
```

If your browser doesn't open automatically, point it to [http://localhost:8888/](http://localhost:8888/) and open graphs.ipynb for interactivity. 

## Files
./assets
This folder contains assets for the mesa server.

./data
This folder contains the generated data of the model.

./lib
This folder contains the source code of the model.




## Further Reading


