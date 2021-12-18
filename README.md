This repo is a python implementation of red light green light game in Squid game.

- It is a simple game where a player is supposed to move when the doll turns back and green light is turned on,
  And stop when it displays red light.
- If a player is caught moving when there is a red light, then the player is dead.
- How ever there is also a time-limit to reach the winning position and player is expected to reach before the timer runs out.

Implemention OverView.

- This game uses pygame module which is a 2D game library for python.
- It uses a thread based implementation, Since there are many things to handle parallely.
  Basically there are 4 threads init_thread, timer_thread, player_thread, doll_thread.
- Let me explain the idea on a high level behind each thread.
  init_thread: This is the initialiser thread, sets the initial position for the player, turns the backgroud music
               and listens for keys pressed by the player. When ever any key is pressed the desired location is
               inserted into the Queue for the player_thread to consume and update its position.
  timer_thread: This thread only does the countdown of time. Currently set to 90 secs. if the timer runs-out it
                signals the other threads to stop.
  player_thread: This listens for player positions to set when any key is pressed from the queue.
                 It is the init_thread job to push to the queue the ne location of the player.
  doll_thread: This thread swaps the doll front, doll back, red light, green light images on the screen.
               Pauses the background music when there is a red light.

How  to play:
- Once the project is cloned, just run python3 red_light_green_light.py

![Demo](red_light_green_light/game.gif)
