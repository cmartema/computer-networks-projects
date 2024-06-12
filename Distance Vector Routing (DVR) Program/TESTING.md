[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/sJyArgKF)
# CSEE 4119 Spring 2024, Assignment 3
## Cristopher Marte Marte (cjm2301)
## Github Username: cmartema

## Trial 1: (3 Nodes)
`topology.dat` file:
- 10.128.0.8 10.128.0.9 7
- 10.128.0.8 10.128.0.10 2
- 10.128.0.9 10.128.0.10 3

### log_10.128.0.8.txt
```sh
<10.128.0.9>:7:<10.128.0.9><10.128.0.10>:2:<10.128.0.10>
<10.128.0.9>:5:<10.128.0.10><10.128.0.10>:2:<10.128.0.10>
```
### log_10.128.0.9.txt
```sh
<10.128.0.8>:7:<10.128.0.8><10.128.0.10>:3:<10.128.0.10>
<10.128.0.8>:5:<10.128.0.10><10.128.0.10>:3:<10.128.0.10>
```

### log_10.128.0.10.txt
```sh
<10.128.0.8>:2:<10.128.0.8><10.128.0.9>:3:<10.128.0.9>
```

### ACII - UI
```sh
VM  1 [DVR] Internal IP: 10.128.0.9
VM  1 [DVR] Node a has IP address 10.128.0.8
VM  1 [DVR] Node b has IP address 10.128.0.9
VM  1 [DVR] Node c has IP address 10.128.0.10
VM  1 [DVR] Distance Routing table for Node b
VM  1 [DVR] to a        (7, via a)      (∞, via c)
VM  1 [DVR] to c        (∞, via a)      (3, via c)
VM  1 [DVR] 
VM  2 [DVR] Internal IP: 10.128.0.10
VM  2 [DVR] Node a has IP address 10.128.0.8
VM  1 [DVR] Routing table updated by c: ip_addr 10.128.0.10
VM  0 [DVR] Internal IP: 10.128.0.8
VM  1 [DVR] Updated DV for node 10.128.0.9: {('a', 'c'): 5, ('c', 'c'): 3}
VM  0 [DVR] Node a has IP address 10.128.0.8
VM  1 [DVR] Distance Routing table for Node b
VM  0 [DVR] Node b has IP address 10.128.0.9
VM  1 [DVR] to a        (7, via a)      (5, via c)
VM  2 [DVR] Node b has IP address 10.128.0.9
VM  1 [DVR] to c        (∞, via a)      (3, via c)
VM  2 [DVR] Node c has IP address 10.128.0.10
VM  1 [DVR] 
VM  2 [DVR] Distance Routing table for Node c
VM  0 [DVR] Node c has IP address 10.128.0.10
VM  2 [DVR] to a        (2, via a)      (∞, via b)
VM  0 [DVR] Distance Routing table for Node a
VM  2 [DVR] to b        (∞, via a)      (3, via b)
VM  0 [DVR] to b        (7, via b)      (∞, via c)
VM  2 [DVR] 
VM  0 [DVR] to c        (∞, via b)      (2, via c)
VM  0 [DVR] 
VM  0 [DVR] Routing table updated by c: ip_addr 10.128.0.10
VM  0 [DVR] Updated DV for node 10.128.0.8: {('b', 'c'): 5, ('c', 'c'): 2}
VM  0 [DVR] Distance Routing table for Node a
VM  0 [DVR] to b        (7, via b)      (5, via c)
VM  0 [DVR] to c        (∞, via b)      (2, via c)
VM  0 [DVR] 
```

## Trial 2: (4 Nodes)
`topology.dat` file:
- 10.128.0.6 10.128.0.8 5
- 10.128.0.6 10.128.0.9 6
- 10.128.0.8 10.128.0.9 1
- 10.128.0.9 10.128.0.10 2

### log_10.128.0.6.txt
```sh
<10.128.0.8>:5:<10.128.0.8><10.128.0.9>:6:<10.128.0.9><10.128.0.10>:∞:<10.128.0.8>
<10.128.0.8>:5:<10.128.0.8><10.128.0.9>:6:<10.128.0.9><10.128.0.10>:8:<10.128.0.9>
```

### log_10.128.0.8.txt
```sh
<10.128.0.6>:5:<10.128.0.6><10.128.0.9>:1:<10.128.0.9><10.128.0.10>:∞:<10.128.0.6>
<10.128.0.6>:5:<10.128.0.6><10.128.0.9>:1:<10.128.0.9><10.128.0.10>:3:<10.128.0.9> 
```

### log_10.128.0.9.txt
```sh
<10.128.0.6>:6:<10.128.0.6><10.128.0.8>:1:<10.128.0.8><10.128.0.10>:2:<10.128.0.10>
```

### log_10.128.0.10.txt
```sh
<10.128.0.6>:∞:<10.128.0.6><10.128.0.8>:∞:<10.128.0.6><10.128.0.9>:2:<10.128.0.9>
<10.128.0.6>:8:<10.128.0.9><10.128.0.8>:3:<10.128.0.9><10.128.0.9>:2:<10.128.0.9>
```

### ACII - UI
```sh
VM  3 [DVR] Internal IP: 10.128.0.10
VM  3 [DVR] Node a has IP address 10.128.0.6
VM  3 [DVR] Node b has IP address 10.128.0.8
VM  3 [DVR] Node c has IP address 10.128.0.9
VM  3 [DVR] Node d has IP address 10.128.0.10
VM  3 [DVR] Distance Routing table for Node d
VM  3 [DVR] to a        (∞, via a)      (∞, via b)      (∞, via c)
VM  3 [DVR] to b        (∞, via a)      (∞, via b)      (∞, via c)
VM  3 [DVR] to c        (∞, via a)      (∞, via b)      (2, via c)
VM  3 [DVR] 
VM  2 [DVR] Internal IP: 10.128.0.9
VM  2 [DVR] Node a has IP address 10.128.0.6
VM  2 [DVR] Node b has IP address 10.128.0.8
VM  2 [DVR] Node c has IP address 10.128.0.9
VM  2 [DVR] Node d has IP address 10.128.0.10
VM  2 [DVR] Distance Routing table for Node c
VM  2 [DVR] to a        (6, via a)      (∞, via b)      (∞, via d)
VM  2 [DVR] to b        (∞, via a)      (1, via b)      (∞, via d)
VM  2 [DVR] to d        (∞, via a)      (∞, via b)      (2, via d)
VM  2 [DVR] 
VM  3 [DVR] Routing table updated by c: ip_addr 10.128.0.9
VM  3 [DVR] Updated DV for node 10.128.0.10: {('a', 'c'): 8, ('b', 'c'): 3, ('c', 'c'): 2}
VM  3 [DVR] Distance Routing table for Node d
VM  3 [DVR] to a        (∞, via a)      (∞, via b)      (8, via c)
VM  3 [DVR] to b        (∞, via a)      (∞, via b)      (3, via c)
VM  3 [DVR] to c        (∞, via a)      (∞, via b)      (2, via c)
VM  3 [DVR] 
VM  1 [DVR] Internal IP: 10.128.0.8
VM  1 [DVR] Node a has IP address 10.128.0.6
VM  1 [DVR] Node b has IP address 10.128.0.8
VM  1 [DVR] Node c has IP address 10.128.0.9
VM  1 [DVR] Node d has IP address 10.128.0.10
VM  1 [DVR] Distance Routing table for Node b
VM  1 [DVR] to a        (5, via a)      (∞, via c)      (∞, via d)
VM  1 [DVR] to c        (∞, via a)      (1, via c)      (∞, via d)
VM  1 [DVR] to d        (∞, via a)      (∞, via c)      (∞, via d)
VM  1 [DVR] 
VM  0 [DVR] Internal IP: 10.128.0.6
VM  0 [DVR] Node a has IP address 10.128.0.6
VM  0 [DVR] Node b has IP address 10.128.0.8
VM  0 [DVR] Node c has IP address 10.128.0.9
VM  0 [DVR] Node d has IP address 10.128.0.10
VM  0 [DVR] Distance Routing table for Node a
VM  0 [DVR] to b        (5, via b)      (∞, via c)      (∞, via d)
VM  0 [DVR] to c        (∞, via b)      (6, via c)      (∞, via d)
VM  0 [DVR] to d        (∞, via b)      (∞, via c)      (∞, via d)
VM  0 [DVR] 
VM  0 [DVR] Routing table updated by c: ip_addr 10.128.0.9
VM  0 [DVR] Updated DV for node 10.128.0.6: {('b', 'b'): 5, ('c', 'c'): 6, ('d', 'c'): 8}
VM  0 [DVR] Distance Routing table for Node a
VM  0 [DVR] to b        (5, via b)      (∞, via c)      (∞, via d)
VM  0 [DVR] to c        (∞, via b)      (6, via c)      (∞, via d)
VM  0 [DVR] to d        (∞, via b)      (8, via c)      (∞, via d)
VM  0 [DVR] 
VM  1 [DVR] Routing table updated by c: ip_addr 10.128.0.9
VM  1 [DVR] Updated DV for node 10.128.0.8: {('a', 'a'): 5, ('c', 'c'): 1, ('d', 'c'): 3}
VM  1 [DVR] Distance Routing table for Node b
VM  1 [DVR] to a        (5, via a)      (∞, via c)      (∞, via d)
VM  1 [DVR] to c        (∞, via a)      (1, via c)      (∞, via d)
VM  1 [DVR] to d        (∞, via a)      (3, via c)      (∞, via d)
VM  1 [DVR]
```
