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

https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=ME405%20Lab3%20Task%20Diagram.drawio#R%3Cmxfile%3E%3Cdiagram%20id%3D%22C5RBs43oDa-KdzZeNtuy%22%20name%3D%22Page-1%22%3E7Vtbd9o4EP4t%2B8A57QM9li8EHpPQJNtNd9OQbbpPPQILo8VYRBYB8ut3ZMvGssFciltnyTlJsEbyyJrv08xoTBrW5WRxzfF09Jm5xG%2BYhrtoWN2GabZRB%2F5KwTIW2LIlBR6nbixCK0GPvhAlNJR0Rl0SagMFY76gU104YEFABkKTYc7ZXB82ZL4%2B6xR7pCDoDbBflD5SV4zUssyzlfyGUG%2BUzIxaasETnAxWKwlH2GXzjMj62LAuOWMivposLokvbZfY5fH35aN%2FO25df%2FoSPuG%2FL%2F54%2BPNrM1Z2tc8t6RI4CcTBql%2FGw6ubr%2Fa%2F36Z3V1%2FmxvV5%2F1NT3WI8Y3%2Bm7PWAw3HDOgdhjwQhDTy1eLFMLBrO6cTHAbQuhiwQPdVjQBv71AvgegAPSjgIngkXFMA4Vx2CTUE6GFHfvcVLNpPLCQUejJPWxYhx%2BgJqsQ9dCATQzYXildnSRvTknWpqTkIYc5fYCKWiWxwKNWbAfB9PQ9qPHlgOmWDu0eCCCcEmiSI2C1ziqlYKetQQnI1TGsn7d0RGISitQRYZXiqkrgmbEMGXMET1mo4d36J2HUpIOF9xGLWUbJTl71lb7R21b7xUdzrdPewzHHhghNV8lqHPZ%2B84HyCiTYd9AD7AglxIM4ZZRsJFZqkrUcTTPTiLCpy94uQp5ixCxs1LgbFgdJFhp0%2BGYiM3wykeAOtvozFdeyW5V4uWIgb3Dv2IFyPquiSIeCOwwP10L0wZDURkFecCfsB2l8YHp%2BHAA11CG63a8COHc3HJAqAYphGXCPB2TiR317CsdDNvZ9lSB29fkLOc0tDdF0qrAOUdpwpJ%2BH3XwxPy%2Fn8HZ4mHGYmJry6rAt0xfzHo6Kwk6MSwmMZnJhiHT7AhOF3%2FLQj9giDkGO0Dg1DbOCQIOc4rCkLtkihknnAQSnd3LaNQ8%2BH%2Be%2F8p%2BMvrItR7uHHxbPqpiewClg2z5YvY7IEGY%2BtpJvN9uYvBP0Voc6%2F%2FThoWLpOP95G9DOmZmkM8of4yHnpD%2FGci8c70h5FXiUKeOV1kO%2BJJZU%2FA%2BET6orTvGXOK4RNYg8WMywNW6bgBnm4aMlcmlp22EUcewycCtlBTsa54J%2BPTEQ6USjOWSYI3Fb3PIx1Dkemh4NACNY%2BRLDTqAbYF4RC0J%2FNEbj1mRHT%2By0wyZ9zVHyvVBSvpjymokzpjL9lUnNLGzUdUkEhHat05HH3jzj44cy%2Fyvs0cxKaDYnSzF%2B8zy3DJgHEsKAuaYkQH44CE6tlpQAVNTJcfm4G5dFzmcbRxLg2nPl4mPT4NpEv9jU7kZsaBggAcBRY5%2ByZchitPfq7NveJ9APsq3grxyE3OLTJtL7ZsVxlVpTTrA9WRXMiuOY1dEpd%2ByIWUnaMjL%2F6W0dQho0G5BOM0E5r1QfAtnynd2a8nnTELSL4dqjcfqo8D%2Bs88VK%2FfvsX9W4CYBO65rKjLSOLjMKQDPTzrJiQLKr5lrv%2BR1wBG3OouMl3dpWq4OBxFCvZ34iGb8QEpywricRC2PFKGnRpHXO29QBG5DFTOGqQSGSc%2B5F%2FP%2BtuEkjBwJymdiThtPQSYtqWriNet7sqW77coQp1cSIoNU1B0tPhQdCsP0mUUSAZ2v8V94uvc2prCTMBHSB1xerHRR3R338RoU3qQvmxSszSy73PWpQ3GB8O09VpIUro8lB7JEDYchqQawJwCYFHOdyqIOab%2BCqVpH2dD6zdUiF%2Bndh494k9xwkh8Rf3Nx7wyx18TR51%2F4xYVcw5y1GdGuaKKHbW55ixac0edMP00HbVZTN3cmVjengpir91Rm8XycX8pSD3g26tusjd6JjI%2BdDrtjmmfWQi1zbajIYlalZ1xi8lNXOE8BaMbnTKjQ3dVRm%2FVLiN5pamGpSOWL0vvnGok31XbpKjqVGPNm%2Fx6pxophU801Si%2BtYaZvoNeD9c53zgqbBXlG7lQVyGIxYPhCcW%2Bdmnss6uKfda67wgcJfahQ2MfmJwv0%2BgpGxkVsrnSEbUSJfthdkhdtvQbMzUJwnZHj51puX7fIOwYucKsk%2BNgxUHYKmZlda%2FzpZupxu68mdOa%2B1p1de7dKiZVP%2Bhp1nuNJtgOObrrODPQFucRte4Ip7BMyRb1An%2BnuiA89cFVwu2vfex6uZfkSyw%2FWk7Mu5efXU60itmGrE7d19m9bPr%2BUJ3cC9K15mJGde7FLpaHT6VaZTulyWN11Sq7WOE9mYx9i9Grq1bZZqVxdD871iYqbSkY7R6V7HJFFUclu3gcSwsZdQ5NKSnrHJpaulaUg7bC2HTCVX3bcY5d2YDm6r%2BTY4xW%2F%2BJtffwP%3C%2Fdiagram%3E%3C%2Fmxfile%3E


## Romi Results
[ROMI Trial Video](https://youtu.be/yMir0CIqmmk "@embed")
