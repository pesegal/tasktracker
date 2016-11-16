# TaskTracker++

Task tracker is the todo list app that I have always wanted. I wanted it to be simple enough that it didn't get in the way of getting stuff done. But I wanted some more advanced features that most task apps are lacking. 

This includes a timer to help keep focus and statistical tracking to see how much time you dedicated to each task. See stats of what you worked on and how long tasks and projects take you.


## TODO:
### Task Screen
#### Functionality:
+ Deletion of projects
+ ~~Deletion of tasks~~
+ ~~Right click bubble popup~~
+ Visualization of task selected for work and visual indicator of progress.
+ Sorting capabilities. (Alphabetical, By Project, Age, ect..) 


#### Theme:
+ Task creation screen 
+ Project Screen
+ Project Spinner Buttons

### Timer Screen
#### Functionality:
+ ~~Loading a task to be worked on by timer.~~
+ Select new task to be loaded to the timer screen.
+ ~~Database interfaces for start, stop, pause and reset.~~
+ Adding in the ability to check if a timer has been forgotten.

#### Theme:
+ ~~Task holder slot empty view.~~
+ ~~Buttons, up state and down state.~~
+ Clock font

### Stats Screen
#### Design:
+ Summary Stats
+ Single Task Stats
+ Single Project Stats

### Other:
+ Settings Screen with user configurable information.
+ Figure out how to set-up packaging for cross platform systems.

#### Potential Future Features
+ Organization buttons to organize tasks by date / project.
+ Ability to categorize tasks into groups (epics) that will will provide statistical summary of tasks contained within.
+ Graphs and other Visualizations that can provide interesting insights where your time is spent.
+ Ability to log-in and store data in the cloud.

## Bug List:
+ ~~Windows sqlite3 database write speed slowdown causing UX issues when click-drag.~~
+ Task screen not resizing correctly when not focused on task screen.
+ ~~Crash when project selector spinner is open and the edit button is pressed.~~
+ ~~Fix Multi Touch Task repositioning.~~
+ Make sure that swapping lists is multi-touch protected.
+ ~~Menu Button color not reset to transparent with clicking dragging away.~~
+ ~~Tasklist Label jumping incorrect amount when scroll view active on release of task~~
