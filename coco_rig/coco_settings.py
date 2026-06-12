COCO_Joint_Name = [
'Nose',
'Neck',

'Shoulder.R',
'Elbow.R',
'Wrist.R',

'Shoulder.L',
'Elbow.L',
'Wrist.L',

'Hip.R',
'Knee.R',
'Ankle.R',

'Hip.L',
'Knee.L',
'Ankle.L',

'Eye.R',
'Eye.L',
'Ear.R',
'Ear.L',
]


COCO_Joint_Color = [
0xFF0000, #Nose
0xFF5500, #Neck

0xFFAA00, #Shoulder.R
0xFFFF00, #Elbow.R
0xAAFF00, #Wrist.R

0x55FF00, #Shoulder.L
0x00FF00, #Elbow.L
0x00FF55, #Wrist.L

0x00FFAA, #Hip.R
0x00FFFF, #Knee.R
0x00AAFF, #Ankle.R

0x0055FF, #Hip.L
0x0000FF, #Knee.L
0x5500FF, #Ankle.L

0xAA00FF, #Eye.R
0xFF00FF, #Eye.L
0xFF00AA, #Ear.R
0xFF0055, #Ear.L
]

COCO_Pair_Link = [
#Shoulder    
(1,2),
(1,5),

#Hand.R
(2,3),
(3,4),

#Hand.L
(5,6),
(6,7),

#Leg.R
(1,8),
(8,9),
(9,10),

#Leg.L
(1,11),
(11,12),
(12,13),

#Head
(1,0),
(0,14),
(14,16),
(0,15),
(15,17),
]



COCO_Pair_Color = [
0x990000,
0x993300,
0x996600,
0x999900,
0x669900,
0x339900,
0x009900,
0x009933,
0x009966,
0x009999,
0x006699,
0x003399,
0x000099,
0x330099,
0x660099,
0x990099,
0x990066,
]


