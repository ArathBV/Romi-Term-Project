# Romi-Term-Project
Cal Poly ME 405 Final Project. Differential Drive Romi-bot.

## Romi Tasks Design
The motor control tasks (1 and 2) were designed according to the finite state machine below. The four motor states, following
initialization, cycle between Start, Maintain, Stop, and Wait. It relies on the 'start' flag to be set or cleared from the sense
task. The important state for motor control is the Maintain state. This state is responsible for the Feed-forward + Integral controller, 
that quickly gets up to speed and maintains low error at steady state. Our Kff and Ki values were determined through testing and tuning.

![ME405 FSM Tasks 1 and 2](https://github.com/user-attachments/assets/33f364ec-16d3-458c-8956-a4ce0f9edb17)

The sensor task (3) design is represented in the finite state machine below. It is an involved task with several states responsible
for the line following, bump detection, and overall course navigation of Romi. The Init Speed state is used to set Romi's speed to drive
forward in a straight line. This state immediately transitions into the Line Sense state, which handles the line sensor reading, centroid
calculation, and set speed adjustments enabling Romi to successfully follow lines: including dashed and tight-radius.
## Romi Results
[ROMI Trial Video](https://youtu.be/yMir0CIqmmk "@embed")
