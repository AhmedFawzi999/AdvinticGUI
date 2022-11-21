# Advintic Gui Functions Documentation

## The GUI consists of two main Classes:
1- The Graph class inheriting from pg.GraphItem and it is used to draw the points and handle updating them.

2- The ApplicationWindow Class .This class is the superclass of the Application it is responsible to show the GUI, capture user interactions, read and upload the dicom files , do actions selected by the user. 

<p>&nbsp;</p>
<p>&nbsp;</p>

# Class Graph Functions

1- Init Function:

> This Function is responsible to intialize all the needed variables in this class and connecting each interaction or click to its function

2- SetData Function

> The main Function is to Set the data of the user input points and calls uodate Graph Function

3- UpdateGraph Function

> This Function is responsible to update the data of the points or the displaying of the points it self

4- Mouse Drag Event Function

> This function is reponsible to listen to the mouse drag event of the points, handle it , and update the position of the point to the new position. It first checks if the event is a left button event then get the position of the point dragged. It then calculates the offset of the drag and move the point to the new location.Also this Function has another function is that if the user wants to translate all the points together it translates them with the same offset and they move together. It then call the update graph function to update the data of the points.

5- Clicked Point Function
>  This function is mainly needed for the delete of a point it is called when a point is clicked and then sets the self.pointDel variable with the data of the point clicked.



<p>&nbsp;</p>
<p>&nbsp;</p>

# Class ApplicationWindow Functions

1- Init Function:

> This Function is responsible to intialize all the needed variables in this class and connecting each interaction or click to its function

2- Scale Function
> This Function is called to update the scale varibale when the user clicks its action button 

3- Translate Fucntion
> This Function is called to update the translate varibale when the user clicks its action button 

4- Upload Image Function
>This Function is responsible to upload the Dicom dataset selected by the user and read it and display it to the userIt first checks for the selected folder if it contains dicom images of no and alerts the user if not.After the Path is selected load_and_calculate_Thickness function is called to read the dicom images and caluculate the thickness of slicesThen the function sets the ConstPixelDims from the dataset uplaoded.After that the function creats the Array for the Dicom images and sets the data of each slice to be later used throughout the whole application

5- SetImagedata Function

>This Function is responsible to construct the 3d numpy array from the metadata array. It loops on all the slices and gets the pixel array from the metadata.


6-load_and_calculate_Thickness Function 

>This Function is responsible to load the dicom files calculate the thickness of the slices by seeing the position of the slice from the metadata and compare it to the position of the next slice and calculate the thickness 
form the difference.

7- Function CalculateCenter
> This Function is responsible to calculate the center x,y of any shape drawn by the user

8- Unstack Function
> This Function unstacks the data into x and y columns

9- ScaleUpDown Function
>This Function is responsible to increase the scale of the shape drawn by the user it increases it or decreases it.Then it gets the data of the current shape drawn by the user in this particular slice and Check if the user wants to increase or decrease the scale whether all the shape or in the X direction only or in the y direction only.It then changes the data of the shape by the new scale

10- EventFilter Function

>This Function is responsible to listen to every event or action the user does with the mouse and do action according to.First Event is that the user action is a mouse scroll and also the zoomvar and scale var is False So the action now is to scroll through the slices. If the Scroll is a forward scroll it gets the next slice if backward it gets the previous slice.

>Second event is that if the user is scrolling the mouse wheel and the scale var is true so increasing of 
decreasing the scale of the shape
 
> Third event is that if the user is scrolling the mouse wheel and the scaleXvar is true so increasing of 
decreasing the scale of the shape

> Fourth event is that if the user is scrolling the mouse wheel and the scaleYvar is true so increasing of 
decreasing the scale of the shape

>Fifth Event is that the user drags a point so the entire shape is updated

> Sixth event is that the user double clicks a point and the delete action is pressed so it deletes the current clicked point

> Seventh event is that the user clicks and draws free hand it detects the mouse press at first

> Eight event is that the draws free hand it detects the mouse movement path

> Ninth event is that the user finishes drawing and is detected when the mouse release happens

> Tenth event is that the user moves the round pointer around 

> Eleventh event is that the user presses the mouse and the round pointer is active  

>  Twelveth event is that the user releases the mouse and the round pointer is active  


11- DrawPoints Function

> This Function is responsible to draw the points on the GUI.It first checks if the array to draw is not emptty so it sets the data and draws it. Then it later checks that the array to draw is 2 points or more so that we could create an array of adjacent points and to pass to the graph class to connect these points. Then after the data has been set we clear the old drawing and draw new one.

12- DeleteSinglePoint Function
> This Function is responsible to toggle the deletesingle point Variable. The actuall deleting of a single point happens in the double click event. 

13-PointsToggle Function
> This Function is responsible to toggle the insertion point Variable to insert or no

14- ZoomToogle Function
> This Function is responsible to toggle the zoom option Variable

15- DeleteAllPoints Function
> This Function is responsible to delete all the points in the current slice.It gets the indecies of the points belonging to the current slice then loops on all the points and delete them. After that it clear the graphs and reset the firstime array of the current slice

16 - GetPosandInsert Function
> This Function is responsible to get the position of the user click and insert a point is the Draw Points Var is True. It then check if the draw points var is true so it inserts a point in the current position. then it gets the position of x,y,z of the point clicked.It then check if it is first time or has not been visited before so we insert the point directly else we check if the point is between 
existing points and see to which segment it belongs and insert between the points of that segment.If thge point is at end or begining it inserts at beginning or end

17 - Calc_distance Function
> calculate the distance between two given points

18- InterpolateData Function
> This Function is responsible to interpolate the data and get new x and y interpolated arrays. It first calculate the distance between each corresponding points.The create a range of points between the min and max distance with constant spacing.Then cubic splice function is used to create the x and y interpolated.

19- TowhichSeg Function
> This Function is responsible to check the new point is closer to which segment and returns the index of this segment.It claulates the distance between the point and every other point in the interpolated data
then it checks which point is closer to the inserted point and then this point belongs to the segment the interpolated x,y falls on.

20- RoundPointer Function
> Round Pointer Variable Update Function

21- DrawEdit Function 
> Free Hand Draw Variable Update Function

22- Circle Function
> Circle orelipse Variable Update Functions

23- DrawEllipse Function 
> This Function is called to draw the ellipse shape inside the function the number of points needed is set to 10 and the angle for each point from the center is calculated then x and y points are generated and then shiffted by a certain value from the center to the clicked point then the points are appended to the array and then drawn.

24- DrawCircle Function 
> This Function is called to draw the circle shape inside the function the number of points needed is set to 10 and the angle for each point from the center is calculated then x and y points are generated and then shiffted by a certain value from the center to the clicked point then the points are appended to the array and then drawn.

25- isWithin Function
> This Function is used to check if a point is within the bounds of an image.

26- drawregions Function

> This Function is called to get the regions or sectors of 30 degrees around a circle and get the coordinates of the lines that divided this regions. It first get the indicies of points in this slice and check if they are less than 2 then it creates the mask and fills it to obtain the outer and and inner regions then it gets the difference between the masks to obtain the wall and then these pixels are divided into subregions or segments with angles of 30 degrees from the center of the shape. Then this function draws lines to divide each subregion and show them to the user. 

27-  switch1 Function
>   Switch 1 is a function that is resonsible to set the variable and arrays to that of the outter region. 

28-  switch2 Function
>   Switch 2 is a function that is resonsible to set the variable and arrays to that of the inner region.

29 - which line Function

> This Function is called to update the lines when the user changes them and to save the new regions. First we check which line the user is changing then we determine which handle exactly it is moving after determining this we get the index of the line before and after so that we are able to get the segments of these lines then we check if the point is right or left or onthe line and update the points of the new segments .








 












