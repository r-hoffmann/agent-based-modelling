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

Hereby it is important to note that Python 3 is used to run the program.
If your browser doesn't open automatically, point it to [http://localhost:8523/](http://localhost:8523/). When the visualization loads, press Reset, then Run.

## How to run the jupyter notebook for graphs

To launch the jupyter notebook, run:

```
    $ jupyter notebook
```

If your browser doesn't open automatically, point it to [http://localhost:8888/](http://localhost:8888/) and open any of the iPython notebooks for interactivity. 

## Files
./assets
This folder contains assets for the mesa server.

./data
This folder contains the generated data of the model.

./lib
This folder contains the source code of the model.

## Further Reading

[1] Ana LC Bazzan and Franziska Kl¨ugl. “A review on agent-based technology for
traffic and transportation”. In: The Knowledge Engineering Review 29.3 (2014),
pp. 375–403.

[2] Steven J Davis, Ken Caldeira, and H Damon Matthews. “Future CO2 emissions and climate change from existing energy infrastructure”. In: Science 329.5997 (2010), pp. 1330–1333.

[3] ID Greenwood, RC Dunn, and RR Raine. “Estimating the effects of traffic congestion on fuel consumption and vehicle emissions based on acceleration noise”. In: Journal of Transportation Engineering 133.2 (2007), pp. 96–104.

[4] Volker Grimm et al. “The ODD protocol: a review and first update”. In: Ecological modelling 221.23 (2010), pp. 2760–2768.

[5] Igor Tchappi Haman et al. “Towards an multilevel agent-based model for traffic simulation”. In: Procedia Computer Science 109 (2017), pp. 887–892.

[6] Dirk Helbing and Michael Schreckenberg. “Cellular automata simulating experimental properties of traffic flow”. In: Physical review E 59.3 (1999), R2505.

[7] LH S Immers Logghe. Course H 111 Verkeerskunde Basis Traffic Flow Theory. Tech. rep. 2002. url: https : / / www . mech . kuleuven . be / cib / verkeer / dwn / H111part3.pdf.

[8] Martin Liebner et al. “Driver intent inference at urban intersections using the intelligent driver model”. In: Intelligent Vehicles Symposium (IV), 2012 IEEE. IEEE. 2012, pp. 1162–1167.

[9] Michael James Lighthill and Gerald Beresford Whitham. “On kinematic waves II. A theory of traffic flow on long crowded roads”. In: Proc. R. Soc. Lond. A 229.1178 (1955), pp. 317–345.

[10] Ch Mallikarjuna and K Ramachandra Rao. “Cellular automata model for heterogeneous traffic”. In: Journal of Advanced Transportation 43.3 (2009), pp. 321–345.

[11] Tom V Mathew and Padmakumar Radhakrishnan. “Calibration of microsimulation models for nonlane-based heterogeneous traffic at signalized intersections”.
In: Journal of Urban Planning and Development 136.1 (2010), pp. 59–66.

[12] Birgit M¨uller et al. “Describing human decisions in agent-based models–ODD+ D, an extension of the ODD protocol”. In: Environmental Modelling & Software 48 (2013), pp. 37–48.

[13] Agata Rakowska et al. “Impact of traffic volume and composition on the air quality and pedestrian exposure in urban street canyon”. In: Atmospheric Environment 98 (2014), pp. 260–270.

[14] Matthias Sweet. “Traffic congestion’s economic impacts: evidence from US metropolitan regions”. In: Urban Studies 51.10 (2014), pp. 2088–2110.

[15] Martin Treiber, Ansgar Hennecke, and Dirk Helbing. “Congested traffic states in empirical observations and microscopic simulations”. In: Physical review E 62.2 (2000), p. 1805.

[16] Dick de Waard et al. “Effect of road layout and road environment on driving performance, drivers’ physiology and road appreciation”. In: Ergonomics 38.7 (1995), pp. 1395–1407.

[17] LA Wastavino et al. “Modeling traffic on crossroads”. In: Physica A: Statistical Mechanics and its Applications 381 (2007), pp. 411–419.

