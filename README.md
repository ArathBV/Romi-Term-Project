# Romi-Term-Project
Cal Poly ME 405 Final Project. Differential Drive Romi-bot.

![IMG_5083](https://github.com/user-attachments/assets/6634316a-27ad-42bf-85a4-1a34ac572fc5)

## Romi Software Design
The motor control tasks (1 and 2) were designed according to the finite state machine below. The four motor states, following
initialization, cycle between Start, Maintain, Stop, and Wait. It relies on the 'start' flag to be set or cleared from the sense
task. The important state for motor control is the Maintain state. This state is responsible for the Feed-forward + Integral controller, 
that quickly gets up to speed and maintains low error at steady state. Our Kff and Ki values were determined through testing and tuning.

![ME405 FSM Tasks 1 and 2](https://github.com/user-attachments/assets/33f364ec-16d3-458c-8956-a4ce0f9edb17)

The sensor task (3) design is represented in the finite state machine below. It is an involved task with several states responsible
for the line following, bump detection, and overall course navigation of Romi. The Init Speed state is used to set Romi's speed to drive
forward in a straight line. This state immediately transitions into the Line Sense state, which handles the line sensor reading, centroid
calculation, and set speed adjustments enabling Romi to successfully follow lines: including dashed and tight-radius. For the majority of
the course, Romi resides in the Line Sense state. Once the bump sensors are triggered, Romi executes a series of 4 states designed to 
navigate out and around the wall obstacle. This involves timed transitions between the Backup, Turn 90deg, Large Arc, Turn 180deg, and
Straight states. Following the completion of the Straight state, Romi transitions back to the Init Speed state to correct the speed,
driving straight and intersecting with the line. Romi navigates the remainder of the course in the Line Sense state, only transitioning
to the final Turn 180deg state when the finish line has been reached.

![ME405 FSM Task 3](https://github.com/user-attachments/assets/fa52ffe9-b5a6-4174-966f-9bf72126dee4)

These three tasks work cooperatively to control Romi, and require certain shared variables, or 'shares' to successfully work together.
The five shares used by these tasks include start, dutyL, dutyR, set_omegaL, and set_omegaR. The interraction between the tasks and 
shares are shown below. One challenge with our Romi was the delay in capacitor discharge of our DC line sensor. The threshold for a 
black line for each of our eight sensors was around 4500us. We implemented a cutoff at this threshold to save on time above that, but
still had difficulty running our Sense task faster than 100-110Hz. Given that, we set the priorities between all three tasks to be even,
since motor control and sensor reading needed to coincide for successful course navigation.

![Screenshot 2024-12-13 181541](https://github.com/user-attachments/assets/b38e1101-1e7c-4fd9-a60b-7d1e1baf820e)

## Romi Hardware Design

The sensors and components we used are as follows: 1 HC-06 bluetooth module, 1 QTR-8RC reflectance sensor array, 2 Pololu mini snap-action
switches (used as bump sensors), and a BNO055 inertial measurement unit (functional with our driver class but unemployed for term project).
The reflectance sensor array is supported with zip-ties through front holes of Romi's chassis, and the bump sensors are mounted with M2 
screws and nuts. To extend beyond the front of the reflectance sensor array, the bump sensors were outfit with extension wires attached using
hot-glue. The IMU was attached using provided M2.5 standoffs and screws; all sensor attachment can be seen below.

![IMG_5081](https://github.com/user-attachments/assets/92791398-eb6c-4855-a269-e412c57ecfee)

## Romi Results
Shown below is the course designed for Romi to navigate, featuring different challenges for line sensors, bump sensors, and overall navigation.
![IMG_5084](https://github.com/user-attachments/assets/4c6f6fb1-14a9-436e-be9a-9cc8aaa613dd)

[ROMI Trial Video](https://youtu.be/yMir0CIqmmk "@embed")

## Challenges and Improvements
This term project was a challenging but rewarding experience, during which we learned a lot about control structures, sensor data collection,
and cooperative multitasking. A major hurdle of ours was the burning out of our first RC line sensor, following its implementation, two days 
before the final trials. We adapted by modifying the first sensor to use two of the operational sensors to calibrate our white/black threshold
and test motor speed changes while awaiting the arrival of the new sensor. Unfortunately, this work seemed inconsequential since the new sensor
had entirely different response times, which should have been anticipated. That being said, we are proud to have accomplished a successful line
following, wall-navigating robot that made it to, and almost over, the finish line.

Some improvements we would like to make, given more time, would include writing a series of interrupts to avoid blocking operations while waiting
for line sensor readings. This would reduce our Sensor class period, allowing us to run it more frequently. This would allow Romi the ability to
navigate the course successfully at higher speeds. We also would like to have implemented inertia measurement unit data to provide a specific
heading for Romi to spin to while finding its way back to start.
