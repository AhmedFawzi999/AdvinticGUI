from imports import * 

# Class Graph that is used to plot the points selected by the user 
class Graph(pg.GraphItem):

    """
    This class is responsible to set the data of the points and draw them it also handles the movements of the points
    when the user drags on point.
    """

    def __init__(self,arr,idxx):
        """
        Intializing of all the variables needed in this class and the actions.
        """
        self.dragPoint = None
        self.dragOffset = None
        self.lst=arr
        self.indexArr=idxx
        self.pointDel=0
        self.Updating=False
        self.Area=0
        self.DelVar=False
        self.allpts=[]
        self.translate=False
        pg.GraphItem.__init__(self)
        self.scatter.sigClicked.connect(self.clicked)
        self.scatter.setData(hoverable="True")
        self.DragStop=False


    # Set Data Function 
    def setData(self, **kwds):
        """
        Set the data of the the user input points
        """
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        self.updateGraph()
        

    # Update Graph Function
    def updateGraph(self):
        """
        This function is reponsible to update the graph when any action is done to the points
        """
        
        self.Updating=True
        pg.GraphItem.setData(self, **self.data)

        
    # Mouse Drag Function
    def mouseDragEvent(self, ev):

        """
        This function is reponsible to listen to the mouse drag event of the points, handle it , and update the position 
        of the point to the new position
        """
        if self.DragStop == False:
            # Check if the event is a left button event
            if ev.button() != QtCore.Qt.LeftButton:
                ev.ignore()
                return
            
            # Checks if the event started and calculated the offset the point is dragged with
            if ev.isStart():
                # the position of the point dragged
                pos = ev.buttonDownPos()

                # get the point dragged and all other points in the list
                self.allpts = self.scatter.points()

                self.pts = self.scatter.pointsAt(pos)
                if len(self.pts) == 0:
                    ev.ignore()
                    return
                self.dragPoint = self.pts[0]
                ind = self.pts[0].data()[0]

                # Calculates the dragoffset of the point dragged
                self.dragOffset = self.data['pos'][ind] - pos

            # checks if the event is finished
            elif ev.isFinish():
                self.dragPoint = None
                return
            # Ignore the event if no drag happens
            else:
                if self.dragPoint is None:
                    ev.ignore()
                    return

            # This part is resonsible to set the new position of the point dragged and also to check if the user 
            # is requesting to translate all the points together by the same offset

            ind = self.dragPoint.data()[0]
            beforex=self.data['pos'][ind].copy()
            # set the data of the point dragged 
            self.data['pos'][ind] = ev.pos() + self.dragOffset
            difference=beforex-self.data['pos'][ind]
            indecies=[i for i,val in enumerate(self.lst[2]) if val==self.indexArr]


            x=indecies[ind]
            self.lst[0][x]=self.data['pos'][ind][0]
            self.lst[1][x]=self.data['pos'][ind][1]

            # Checks if the user wants to translate all the points and loops on the list of points except for the dragged 
            # point and translate all other points by the same drag offset
            if self.translate==True:
                for i in range(len(self.allpts)):
                    if self.allpts[i]!=self.pts:
                        dragPoint = self.allpts[i]
                        ind = dragPoint.data()[0]
                        self.data['pos'][ind] = self.data['pos'][ind] - difference
                        indecies=[i for i,val in enumerate(self.lst[2]) if val==self.indexArr]

                        x=indecies[ind]
                        self.lst[0][x]=self.data['pos'][ind][0]
                        self.lst[1][x]=self.data['pos'][ind][1]
                    
            # Update the Graph       
            self.updateGraph()
            ev.accept()
        

            
    # def hovered(self):
    #     print("jhhhhg")
    
    # Clicked Point Function
    def clicked(self,plot, pts):
        """
        This function is mainly needed for the delete of a point it is called when a point is clicked and then 
        sets the self.pointDel variable with the data of the point clicked.
        """
        self.DelVar=True
        for point in pts:
            self.pointDel=pts[0].data()[0]
            print(pts[0].data()[0],point.pos())
        

#****************************************************************************************************************#

# This is the Main Application Window that is responsible for every thing in the GUI and all user interactions

class ApplicationWindow(QtWidgets.QMainWindow):

    """
    This class is the superclass of the Application it is responsible to show the GUI, capture user interactions
    , read and upload the dicom files , do actions selected by the user. 
    """

    # Initialization of the Whole Application and Variables
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()
        # self.setGeometry(600, 300, 400, 200)
        self.setWindowTitle('Dicom Viewer')
        pg.setConfigOption('background', 'w')



        # Intialize the View Window and set the axis and Aspect of the ViewPort
        self.ui.View.viewport().installEventFilter(self)
        self.ui.View.setAspectLocked(lock=True, ratio=1)
        self.ui.View.invertY(True)
        self.ui.View.getPlotItem().hideAxis('left')
        self.ui.View.getPlotItem().hideAxis('bottom')
        self.ui.View.setAntialiasing(True)
        self.temp=[0,0,0]

        # Intialize the Varaibles needed throughout the Application
        self.ArrayDicom = [] # Store the Dicom Images
        self.ConstPixelSpacing = [] # Array to Store the Spacing between pixels
        self.indexView = 0 # The Current Slice index
        self.zoomVar=False # Variable to check if zoom action is toggled or no
        self.pointdelBool=False # Variable to check if delete single point action is toggled or no
        self.DrawpointsVar=False # Variable to check if draw points action is toggled or no
        self.pointslst  = [ [None]*0 for _ in range(3)]  # Array to store the x,y,z of each point
        self.pointerlist  = [ [None]*0 for _ in range(3)]  # Array to store the x,y,z of each point
        self.pointslst1  = [ [None]*0 for _ in range(3)]  # Array to store the x,y,z of each point
        self.pointslst2  = [ [None]*0 for _ in range(3)]  # Array to store the x,y,z of each point

        self.pointtoDel=0  # A variable to store the point to delete
        self.x_after_interpolate=[]  # An Array to store the x interpolated points
        self.y_after_interpolate=[]  # An Array to store the y interpolated points
        self.x_after_interpolate1=[]  # An Array to store the x interpolated points
        self.y_after_interpolate1=[]  # An Array to store the y interpolated points
        self.x_after_interpolate2=[]  # An Array to store the x interpolated points
        self.y_after_interpolate2=[]  # An Array to store the y interpolated points
        self.range_of_points=[] # An Array to store range of points used to obtain x,y interpolated and segments
        x, y = np.meshgrid(np.arange(512), np.arange(512)) 
        x, y = x.flatten(), y.flatten()
        self.mespoints = np.vstack((x,y)).T 
        self.DistanceArray=[]  # Array to store distances between points
        self.firstime=[]  # Array to store is a slice is visited before by the user and will help in the deleting and insertions
        self.scaleVar=False # Variable to check if scale action is toggled or no
        self.scaleYVar=False # Variable to check if scaleYaction is toggled or no
        self.scaleXVar=False # Variable to check if scaleXaction is toggled or no
        self.circleVar=False # Variable to check if circleaction is toggled or no
        self.ellipseVar=False  # Variable to check if ellipseaction is toggled or no
        self.drawEditvar=False  # Variable to check if Freehand Draw is toggled or no
        self.first=0           # variable to cehck
        self.RoundPointerVar=False  # Variable to check if RoundPointer action is toggled or no
        self.sizeo=50               # initial size of the pointer
        self.MousePressVar=False    # Variable to detect mouse press event
        self.space=0                 # Variable to set the space of used in the round pointer
        self.collor=0                # Variable to set the color of the pointer
        self.newEllipseVar=False     ## Variable Unused yet
        self.ellipsecounter=0
        self.masko=[]     ##mask of the outer image
        self.maski=[]     ##mask of the inner image
        self.gtrouth=[]   ## gtrouth image of the wall
        # Toggled and connecting each action button to its fucntion
        self.ui.actionZoom.toggled.connect(self.ZoomToogle)
        self.ui.actionOpen_Dicom.toggled.connect(self.UploadImage)
        self.ui.actionaddPoints.toggled.connect(self.PointsToggle)
        self.ui.actiondeleteShape.triggered.connect(self.DeleteAllPoints)
        self.ui.actionDelPoint.toggled.connect(self.DeleteSinglePoint)
        self.ui.actionTranslate.toggled.connect(self.Translate)
        self.ui.actionscale.toggled.connect(self.Scale)
        self.ui.actionYscale.toggled.connect(self.Yscale)
        self.ui.actionactionXscale.toggled.connect(self.Xscale)
        self.ui.actioncircle.toggled.connect(self.circle)
        self.ui.actionelipse.toggled.connect(self.ellipse)
        self.ui.actionedit.triggered.connect(self.drawEdit)
        self.ui.actionRoundPointer.toggled.connect(self.RoundPointer)
        self.ui.actionouter.toggled.connect(self.switch1)
        self.ui.actioninner.toggled.connect(self.switch2)
        # self.ui.actionnewellipse.toggled.connect(self.togglenewEllipse)
        self.ui.actionregions.triggered.connect(self.drawregions)

        # Creating two objects of Class Graph one to draw the user input points and the other for the interpolated points
        self.points=Graph(self.pointslst,self.indexView)
        self.pointsTrue=Graph(self.pointslst,self.indexView)
        self.points1=Graph(self.pointslst1,self.indexView)
        self.pointsTrue1=Graph(self.pointslst1,self.indexView)
        
        self.points2=Graph(self.pointslst2,self.indexView)
        self.pointsTrue2=Graph(self.pointslst2,self.indexView)

        self.firstime1=[]
        self.firstime2=[]

        self.x1,self.y1,self.x2,self.y2=0,0,0,0

        self.pointer=Graph(self.pointerlist,self.indexView)
        self.pointerlist[0].append(0)
        self.pointerlist[1].append(0)
        self.pointerlist[2].append(0)

        self.outter=False
        self.inner=False
        self.pointss=[]

        colorButton = QtWidgets.QPushButton("Colors")
        exitAct = QtWidgets.QAction('Exit', self)

        ## Initializing the 12 lines and array to hold the interpolated points in them
        self.interpointssarr1=[]
        self.interpointssarr2=[]
        self.segs  = [ [None]*0 for _ in range(12)] 
        for mini  in self.segs:
            # xx=[ [None]*0 for _ in range(2)]
            for i in range(2):
                # print(counter)
                mini.append([])
        self.line1= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line2= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line3= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line4= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line5= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line6= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line7= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line8= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line9= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line10= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line11= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.line12= pg.LineSegmentROI([[0,0,], [0, 0]], movable=False,rotatable=True, resizable=True)
        self.lines = [self.line1, self.line2, self.line3, self.line4,self.line5,self.line6,self.line7,self.line8,self.line9,self.line10,self.line11,self.line12]
        for lines in self.lines:
            # lines.stateChanged(finish=True)
            lines.sigRegionChanged.connect(self.whichline)
            lines.sigRegionChangeFinished.connect(self.finished)
    
    def finished(self,obj):
        print("hiiiiiiii")

    ## which line function
    def whichline(self,obj):
        """
        This Function is called to update the lines when the user changes them and to save the new regions

        """
        ## first check which line the user is chaning 
        objindex=0
        for i in range(len(self.lines)):
            if obj==self.lines[i]:
                objindex=i
        

        print(objindex)
        
        # saving the old x,y values of both handles of the line
        tempx1=self.x1
        tempy1=self.y1
        tempx2=self.x2
        tempy2=self.y2

        ## now get the new values of the line handle
        self.x1=obj.listPoints()[0][0]
        self.y1=obj.listPoints()[0][1]
        self.x2=obj.listPoints()[1][0]
        self.y2=obj.listPoints()[1][1]
        
        # these variables are used to determin which handle is being moved the first or the second
        first=False
        second=False

        # determine which handles
        if tempx1!= self.x1 or tempy1!=self.y1:
            first=True
            print("First")
        elif tempx2!= self.x2 or tempy2!=self.y2:
            second=True
            print("Second")
        
        ## now we want to move the handle along the border of the inner or outter 
        ## to do that we check for the x,y of the handle moved then we calc the distance to the nearest point on the border
        ## then move the handle to that point 
        ## this will make an effect of moving along the border
        min=sys.maxsize
        if first==True:
            for i in range(len(self.interpointssarr2[self.indexView][0])):
                d=self.calc_distance([self.x1, self.y1],[self.interpointssarr2[self.indexView][0][i],self.interpointssarr2[self.indexView][1][i]])
                if d<min:
                    min=d
                    index=i
            ## move the point to the nearest point on the border
            obj.movePoint(0,[self.interpointssarr2[self.indexView][0][index],self.interpointssarr2[self.indexView][1][index]])
        min=sys.maxsize
        ## do the same for the seconf handle if it is the one moving
        if second==True:
            for j in range(len(self.interpointssarr1[self.indexView][0])):
                d=self.calc_distance([self.x2, self.y2],[self.interpointssarr1[self.indexView][0][j],self.interpointssarr1[self.indexView][1][j]])
                if d<min:
                    min=d
                    index=j
            obj.movePoint(1,[self.interpointssarr1[self.indexView][0][index],self.interpointssarr1[self.indexView][1][index]])


        ## now we have the index of the line we could get the index before and index after
        indexafter=objindex+1
        indexbefore=objindex-1
        if objindex==0:
            indexbefore=len(self.lines)-1
        if objindex==len(self.lines)-1:
            indexafter=0
        
        print(indexbefore)
        print(indexafter)

        ## create a list with the same shape as that of the segments to store the new values
        twosegs  = [ [None]*0 for _ in range(12)] 
        for mini  in twosegs:
            # xx=[ [None]*0 for _ in range(2)]
            for i in range(2):
                # print(counter)
                mini.append([])
 
        ## do the same for the index before handles
        # x1=self.lines[indexbefore].listPoints()[0][0]
        # y1=self.lines[indexbefore].listPoints()[0][1]
        # x2=self.lines[indexbefore].listPoints()[1][0]
        # y2=self.lines[indexbefore].listPoints()[1][1]

        ## now we obtain the values of the segments of that before the line and after the line
        
        data1=np.column_stack([self.segs[objindex][0], self.segs[objindex][1]])
        print(len(self.segs[objindex][0]),len(self.segs[objindex][1]))
        data2=np.column_stack([self.segs[indexbefore][0], self.segs[indexbefore][1]])
        print(len(self.segs[indexbefore][0]),len(self.segs[indexbefore][1]))

        datan=np.vstack((data2,data1))

        ## no check for the points that fall in the segment that is to the left or right or on the line
        for i in range(len(datan)):
            v1 = (self.x2-self.x1, self.y2-self.y1)   # Vector 1
            # v2 = (self.x2-275, self.y2-377)   # Vector 2
            v2 = (self.x2-datan[i][0], self.y2-datan[i][1])   # Vector 2

            xp = v1[0]*v2[1] - v1[1]*v2[0]  # Cross product
            if xp > 0:
                print('shemalha')
                twosegs[indexbefore][0].append(datan[i][0])
                twosegs[indexbefore][1].append(datan[i][1])            
            elif xp < 0:
                print('yemenha')
                twosegs[objindex][0].append(datan[i][0])
                twosegs[objindex][1].append(datan[i][1])
            else:
                print('on the same line!')
                twosegs[objindex][0].append(datan[i][0])
                twosegs[objindex][1].append(datan[i][1])
            
        # save the new points
        if first ==True or second==True:
            self.segs[indexbefore]=twosegs[indexbefore].copy()
            self.segs[objindex]=twosegs[objindex].copy()
            np.save('segs.npy',self.segs,allow_pickle=True)
            # print(obj.getLocalHandlePositions())
            # print(obj.getLocalHandlePositions()[0][1][1])

    def drawregions(self):

        """
        This Function is called to get the regions or sectors of 30 degrees around a circle and get the coordinates of the lines that divided this regions

        """

        # get the indicies of points in this slice and check if they are less than 2
        indecies1=[i for i,val in enumerate(self.pointslst1[2]) if val==self.indexView]

        # if the indicies are less than 2 then do nothing elseget the interpolated x and y points and then create the mask of the outer 
        if len(indecies1) > 2:
            xx=self.interpointssarr1[self.indexView][0]
            yy=self.interpointssarr1[self.indexView][1]
            # create the mask
            self.masko = np.zeros([512, 512], dtype="uint8")
            data1=np.column_stack([xx, yy])
            # fill the mask using the contour
            cv2.fillPoly(self.masko, np.int32([data1]), 1)
            # center1=(sum(self.x_after_interpolate) / len(self.x_after_interpolate), sum(self.y_after_interpolate) / len(self.x_after_interpolate))
            # print("Center Outter:",center1)
            np.save('pointslst1.npy', [xx,yy],allow_pickle=True)



        # if the indicies are less than 2 then do nothing elseget the interpolated x and y points and then create the mask of the inner 
        indecies2=[i for i,val in enumerate(self.pointslst2[2]) if val==self.indexView]

        if len(indecies2) > 2:
            xx=self.interpointssarr2[self.indexView][0]
            yy=self.interpointssarr2[self.indexView][1]
            # create the mask
            self.maski = np.zeros([512, 512], dtype="uint8")
            data2=np.column_stack([xx, yy])
            # fill the mask using the contour
            cv2.fillPoly(self.maski, np.int32([data2]), 1)
            # center2=(sum(self.interpointssarr2[self.indexView][0][i]) / len(self.x_after_interpolate), sum(self.y_after_interpolate) / len(self.x_after_interpolate))
            # print("Center Inner:",center2)
            np.save('pointslst2.npy', [xx,yy],allow_pickle=True)

        # if the indicies of the outter and the inner are both greater than 2 then generate the groound truth mask of the wall that is the difference between them
        if len(indecies2) > 2 and len(indecies1) > 2 :

            ## the difference generates the mask of the wall
            self.gtrouth=self.masko-self.maski
            self.gtrouth[self.gtrouth==1]=255

            #apply threshold
            ret,thresh1 = cv2.threshold(self.gtrouth,150, 255, cv2.THRESH_BINARY)
            # find the contours by this way we do have the contours of both the outer and inner and then we could get the mask of each easy
            contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            hierarchy = hierarchy[0]

            ## create list that will hold the points of the contours
            lst  = [ [None]*0 for _ in range(len(contours))] 
            for mini  in lst:
                # xx=[ [None]*0 for _ in range(2)]
                for i in range(2):
                    mini.append([])
            centerx=[]
            centery=[]
            i=0

            ## now loop on the contours and then calculate the center of each the inner and the outer using the contour points
            for component in zip(contours, hierarchy):
                currentContour = component[0]
                currentHierarchy = component[1]
                # print(currentHierarchy)
                M = cv2.moments(currentContour)
                cX = M["m10"] / M["m00"]
                cY = M["m01"] / M["m00"]
                centerx.append(cX)
                centery.append(cY)
                for corner in currentContour[:, 0, :]:
                    ## appending the coordinates of the points
                    corner_coords = tuple(corner.tolist())
                    lst[i][0].append(corner_coords[0])
                    lst[i][1].append(corner_coords[1])

                i+=1
            ## now find where the wall is 255(white) and get the coordinates 
            arr=np.where(self.gtrouth==255)
            arr=np.transpose(np.array(arr))
            Groundx=[]
            Groundy=[]
            for i in range(len(arr)):
                Groundx.append(arr[i][1])
                Groundy.append(arr[i][0])
            
            ## Array to store the points of each segment 
            self.segs  = [ [None]*0 for _ in range(12)] 
            for mini  in self.segs:
                # xx=[ [None]*0 for _ in range(2)]
                for i in range(2):
                    # print(counter)
                    mini.append([])
            ## Array to store the x,y of the start and end of each line
            self.pointss  = [ [None]*0 for _ in range(12)] 
            for mini  in self.pointss:
                # xx=[ [None]*0 for _ in range(2)]
                for i in range(2):
                    # print(counter)
                    mini.append([])
            max=-sys.maxsize - 1
            ## no loop on the groundtruth points and calclate the distance between the center and the points to get the one with the max distance
            for i in range(len(Groundx)):
        
                distance=self.calc_distance([Groundx[i],Groundy[i]],[centerx[1],centery[1]])
                if distance>max:
                    max=distance
                    maxi=i
            ## now set the radius with this max distance plus any value to make sure the radius covers all the parts of the shape
            radius=max +10

            # check the points belong to which seg
            self.checkPoint(radius,centerx,centery,Groundx,Groundy,self.segs)
            
            startAngle=0
            endAngle = startAngle+30

            # now get the verticies of each line dividing the segments
            for j in range(len(self.pointss)):

                # calculate the end of each line by the set angle and radius
                endy = centery[1] + radius * mathh.sin(mathh.radians(startAngle))
                endx = centerx[1]+radius * mathh.cos(mathh.radians(startAngle))

                norm = np.linalg.norm
                p1=np.array([centerx[1],centery[1]])
                p2=np.array([endx,endy])
                min=sys.maxsize

                # now check the point with the min distance from the line and set it as the first vertex of the line ( on the wall of inner)
                for i in range(len(self.interpointssarr2[self.indexView][0])):
                    
                    p3=np.array([self.interpointssarr2[self.indexView][0][i],self.interpointssarr2[self.indexView][1][i]])
                    d = self.DistancePointLine(p3[0],p3[1],p1[0],p1[1],p2[0],p2[1])

                    if d < min:
                        min=d
                        point1=p3.copy()
                        self.pointss[j][0]=[self.interpointssarr2[self.indexView][0][i],self.interpointssarr2[self.indexView][1][i]]
                min=sys.maxsize
                # now check the point with the min distance from the line and set it as the second vertex of the line ( on the wall of outter)
                for k in range(len(self.interpointssarr1[self.indexView][0])):
                    
                    p3=np.array([self.interpointssarr1[self.indexView][0][k],self.interpointssarr1[self.indexView][1][k]])
                    d = self.DistancePointLine(p3[0],p3[1],p1[0],p1[1],p2[0],p2[1])
                    # print(d)
                    if d < min:
                        min=d
                        # print(min)
                        point2=p3.copy()
                        self.pointss[j][1]=[self.interpointssarr1[self.indexView][0][k],self.interpointssarr1[self.indexView][1][k]]
                        # print(point2,"henaaaaaa")



                startAngle=endAngle
                endAngle = startAngle+30

            # now draw the lines
            for i in range(len(self.pointss)):
                self.ui.View.removeItem(self.lines[i])
                self.lines[i] = pg.LineSegmentROI([[self.pointss[i][0][0], self.pointss[i][0][1],], [self.pointss[i][1][0], self.pointss[i][1][1]]], pen="white",movable=False,rotatable=True, resizable=True)
                self.ui.View.addItem(self.lines[i])

                # print(self.lines[3].getLocalHandlePositions())
                # self.lines[i].stateChanged(finish=True)
                self.lines[i].sigRegionChanged.connect(self.whichline)
                self.lines[i].sigRegionChangeFinished.connect(self.finished)

                # self.lines[i].getSceneHandlePositions
                # self.lines[i].sigHoverEvent.connect(self.whichline)
        
                # self.ui.View.removeItem(self.lines[3])

                # print(self.lines[2].getHandles())



    # def togglenewEllipse(self):
    #     if self.newEllipseVar==False:
    #         self.newEllipseVar=True
    #     else:
    #         self.newEllipseVar=False

    # def newellipse(self,x,y):
    #     center=self.CalculateCenter(x,y)


    # Round Pointer Variable Update Function
    def RoundPointer(self):
        """
        This Function is called to toggle roundpointer
        """
        if self.RoundPointerVar == True:
            self.RoundPointerVar=False
            self.ui.View.removeItem(self.pointer)

        else:
            self.RoundPointerVar=True

    # Free Hand Draw Variable Update Function
    def drawEdit(self):
        """
        This Function is called to toggle drawEdit var (free hand draw)
        """
        if self.drawEditvar == True:
            print(self.drawEditvar)

            self.drawEditvar=False
        else:
            print(self.drawEditvar)

            self.drawEditvar=True

    # circle orelipse Variable Update Functions
    def circle(self):
        """
        This Function is called to toggle circle var 
        """
        if self.circleVar == True:
            self.circleVar=False
        else:
            self.circleVar=True
    def ellipse(self):
        """
        This Function is called to toggle elipse var 
        """
        if self.ellipseVar == True:
            self.ellipseVar=False
        else:
            self.ellipseVar=True
    
    ## Switch 1 is a function that is resonsible to set the variabel and arrays to that of the outter region 
    def switch1(self):

        """
        This Function is resonsible to set the variable and arrays to that of the outter region 

        """
        ## if it is already true turn it off
        if self.outter == True:
            # self.pointsTrue2.DragStop=False
            self.outter=False
            if self.inner ==False and self.outter==False:
                self.pointsTrue1.DragStop=True
                self.pointsTrue2.DragStop=True

            self.DrawPoints()

            print("etafet1")
        # else we stop draging of the inner points and set the variabel to those of the outter part
        else:
            self.outter=True
            self.pointsTrue2.DragStop=True
            self.pointsTrue1.DragStop=False

            self.points=self.points1
            self.pointsTrue=self.pointsTrue1
            self.x_after_interpolate=self.x_after_interpolate1
            self.y_after_interpolate=self.y_after_interpolate1

            self.firstime=self.firstime1
            self.pointslst=self.pointslst1
            self.ui.actioninner.setChecked(False)
            self.inner=False
            self.collor=1
            self.pointsTrue2.DragStop=True

            self.DrawPoints()
            self.pointsTrue.Updating=False


    ## Switch 2 is a function that is resonsible to set the variable and arrays to that of the inner region 
    def switch2(self):
        """
        This Function is resonsible to set the variabel and arrays to that of the inner region 

        """
        ## if it is already true turn it off

        if self.inner == True:
            # self.pointsTrue1.DragStop=True
            self.inner=False
            if self.inner ==False and self.outter==False:
                self.pointsTrue1.DragStop=True
                self.pointsTrue2.DragStop=True

            self.DrawPoints()

            print("etafet2")
        # else we stop draging of the inner points and set the variabel to those of the inner part
        else:
            self.inner=True
            self.pointsTrue1.DragStop=True
            self.pointsTrue2.DragStop=False

            self.points=self.points2
            self.pointsTrue=self.pointsTrue2
            self.firstime=self.firstime2
            self.pointslst=self.pointslst2
            self.x_after_interpolate=self.x_after_interpolate2
            self.y_after_interpolate=self.y_after_interpolate2

            self.ui.actionouter.setChecked(False)
            self.outter=False
            self.collor=2
            self.pointsTrue1.DragStop=True

            self.DrawPoints()
            self.pointsTrue.Updating=False






    def DrawEllipse(self,ClickedX,ClickedY):
        """
        This Function is called to draw the ellipse shape 
        """
        ## determining the number of points needed to construct the elipse
        M = 10
        ## the angle for each point from the center
        angle = np.exp(1j * 2 * np.pi / M)
        angles = np.cumprod(np.ones(M + 1) * angle)
        ## making the x and y array
        x, y = np.real(80*angles), np.imag(40*angles)

        ## calculating the center of the elipse from the points 
        center=self.CalculateCenter(x,y)
        ## shift the center from the origin to the clicked point
        differenceX=ClickedX-center[0]
        differenceY=ClickedY-center[1]
        print(center)
        ## shiffting all the points from the center origin to the new xy of the clicked origin
        x=x+differenceX
        y=y+differenceY
        x=x.tolist()
        y=y.tolist()
        x.pop()
        y.pop()

        # self.pointslst[0]=x
        # self.pointslst[1]=y
        ## appending the x,y z of the points
        for i in range(len(x)):
            self.pointslst[2].append(self.indexView)
            self.pointslst[0].append(x[i])
            self.pointslst[1].append(y[i])
            self.firstime[self.indexView]+=1


        print(len(self.pointslst[0]),len(self.pointslst[1]),len(self.pointslst[2]))
        # calling the draw function
        self.DrawPoints()

    def DrawCircle(self,ClickedX,ClickedY):
        """
        This Function is called to draw the circle shape 
        """

        ## determining the number of points needed to construct the circle
        M = 12
        ## the angle for each point from the center
        angle = np.exp(1j * 2 * np.pi / M)
        angles = np.cumprod(np.ones(M + 1) * angle)

        ## making the x and y array
        x, y = np.real(50*angles), np.imag(50*angles)

        ## calculating the center of the elipse from the points 
        center=self.CalculateCenter(x,y)
        ## shift the center from the origin to the clicked point
        differenceX=ClickedX-center[0]
        differenceY=ClickedY-center[1]
        print(center)
        ## shiffting all the points from the center origin to the new xy of the clicked origin
        x=x+differenceX
        y=y+differenceY
        x=x.tolist()
        y=y.tolist()
        x.pop()
        y.pop()


        ## appending the x,y z of the points
        for i in range(len(x)):
            self.pointslst[2].append(self.indexView)
            self.pointslst[0].append(x[i])
            self.pointslst[1].append(y[i])
            self.firstime[self.indexView]+=1

        print(len(self.pointslst[0]),len(self.pointslst[1]),len(self.pointslst[2]))
        # calling the draw function
        self.DrawPoints()

    # YScale Variable Update Function
    def Yscale(self):
        """
        This Function is called to update the scale varibale when the user clicks its action button 
        """
        if self.scaleYVar==True:
            self.scaleYVar=False
        else:
            self.scaleYVar=True
    
        # XScale Variable Update Function
    def Xscale(self):
        """
        This Function is called to update the scale varibale when the user clicks its action button 
        """
        if self.scaleXVar==True:
            self.scaleXVar=False
        else:
            self.scaleXVar=True
        
    # Scale Variable Update Function
    def Scale(self):
        """
        This Function is called to update the scale varibale when the user clicks its action button 
        """
        if self.scaleVar==True:
            self.scaleVar=False
        else:
            self.scaleVar=True
    
    
    # Translate All points Variable Update Function
    def Translate(self):
        """
        This Function is called to update the translate varibale when the user clicks its action button 
        """

        if self.pointsTrue.translate==True:
            self.pointsTrue.translate=False
        else:
            self.pointsTrue.translate=True


    # Upload Dicom Dataset and display images
    def UploadImage(self):

        """
        This Function is responsible to upload the Dicom dataset selected by the user and read it and display it to the user
        """

        # The path of the data set
        self.path= QFileDialog.getExistingDirectory()


        # Checks for the selected folder if it contains dicom images of no and alerts the user if not
        onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        for i in onlyfiles:
            if os.path.splitext(i)[-1].lower() !='.dcm':
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Choose Dicom Files Only!')
                break
        
        # After the Path is selected load_and_calculate_Thickness to read the dicom images and caluculate the thickness of slices
        slices=self.load_and_calculate_Thickness(self.path)
        self.slicedata=slices[0]


        # Setting the ConstPixelDims from the dataset uplaoded
        ConstPixelDims = (int(slices[0].Rows), int(slices[0].Columns), len(slices))
        
        # Setting the ConstPixelSpacing from the dataset uplaoded to use else where in the code
        self.ConstPixelSpacing = (float(slices[0].PixelSpacing[0]), float(slices[0].PixelSpacing[1]), float(slices[0].SliceThickness))

        # Initializing the ArrayDicom shape to store the slices and easy acces them from numpy array
        self.ArrayDicom = np.zeros(ConstPixelDims, dtype=slices[0].pixel_array.dtype)
        idx=len(slices)-1
        # Setting the Image Data
        self.SetImagedata(self.ArrayDicom,slices,idx)

        # TO ASK DOCTOR AHMED
        self.ArrayDicom=np.rot90(self.ArrayDicom,1)
        self.ArrayDicom=numpy.flipud(self.ArrayDicom)
        
        # Display First Slice from the Dicom Array
        img=self.ArrayDicom[:,:,0]
        self.image = pg.ImageItem(img)      
        self.ui.View.addItem(self.image)
        
        self.image.mouseClickEvent = self.getPosandInsert
        self.firstime=np.zeros(self.ArrayDicom.shape[2])
        self.firstime1=np.zeros(self.ArrayDicom.shape[2])
        self.firstime2=np.zeros(self.ArrayDicom.shape[2])
        self.interpointssarr1 = [ [None]*0 for _ in range(self.ArrayDicom.shape[2])] 
        for mini  in self.interpointssarr1:
            # xx=[ [None]*0 for _ in range(2)]
            for i in range(2):
                mini.append([])
        self.interpointssarr2 = [ [None]*0 for _ in range(self.ArrayDicom.shape[2])] 
        for mini  in  self.interpointssarr2:
            # xx=[ [None]*0 for _ in range(2)]
            for i in range(2):
                mini.append([])

    # Set Image Data Function that takes the meta data and construct the 3d numpy array
    def SetImagedata(self, ArrayDicom,slices,idx):
                
        """
        This Function is responsible to construct the 3d numpy array from the metadata array
        """
        for s in slices:
            ArrayDicom[:,:,idx] = s.pixel_array
            idx-=1

    # load and calculate Thickness Function
    def load_and_calculate_Thickness(self, path):

        """
        This Function is responsible to load the dicom files calculate the thickness of the slices by seeing the position
        of the slice from the metadata and compare it to the position of the next slice and calculate the thickness 
        form the difference.

        """
        slices = [pydicom.dcmread(path + '/' + s) for s in os.listdir(path)]
        # slices = [s for s in slices if 'SliceLocation' in s]
        slices.sort(key = lambda x: int(x.InstanceNumber))
        try:
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2]-slices[1].ImagePositionPatient[2])
        except:
            slice_thickness = np.abs(slices[0].SliceLocation-slices[1].SliceLocation)
        for s in slices:
            s.SliceThickness = slice_thickness
        return slices



    def CalculateCenter(self,x, y):
        """
        This Function is responsible to calculate the center x,y of any shape drawn by the user
        """
        diff = x[:-1] * y[1:] - x[1:] * y[:-1]
        coef = 1 / (diff.sum() * 3)
        return coef * ((x[:-1] + x[1:]) * diff).sum(), coef * ((y[:-1] + y[1:]) * diff).sum()


    def unstack(self,a, axis=0):
        """
        This Function unstacks the data into x and y columns
        """
        return np.moveaxis(a, axis, 0)


    # Scale Up and Down Function 
    def ScaleUpDown(self,var,action):

        """
        This Function is responsible to increase the scale of the shape drawn by the user it increases it or decreases it
        """

        # Get the data of the current shape drawn by the user in this particular slice 
        indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]

        xarr= [self.pointslst[0][i] for i in indecies]
        yarr= [self.pointslst[1][i] for i in indecies]
        data=np.column_stack([xarr, yarr])
        data=np.vstack((data,data[0]))
        pos = np.array(self.CalculateCenter(*data.T))

        # Check if the user wants to increase or decrease the scale
        if var == "inc":
            mul = 1+0.05    # Zoom in 0.05
        else:
            mul = 1-0.05    # Zoom out 0.05
        
        # change the data of the shape by the new scale according to which action if 1 all shape scale 2 x scale only 3 y scale only
        if action==1:
            new_data = (data - pos) * mul + pos

        elif action == 2:

            dataxnew=(data[:,0]-pos[0])*mul+pos[0]
            new_data=np.column_stack([dataxnew,data[:,1]])

        elif action == 3:

            dataynew=(data[:,1]-pos[1])*mul+pos[1]
            new_data=np.column_stack([data[:,0],dataynew])

        # Call Unstcak Function to separate data into x and y columns
        An, Bn, = self.unstack(new_data, axis=1)
        An=An.tolist()
        Bn=Bn.tolist()
        An.pop()
        Bn.pop()
        for idx, i in enumerate(indecies):
            self.pointslst[0][i]=An[idx]
            self.pointslst[1][i]=Bn[idx]

        self.pointsTrue.indexArr=self.indexView
        # Draw the new points 
        self.DrawPoints()


    # Main Event Filter Function

    def eventFilter(self, watched, event):
        """
        This Function is responsible to listen to every event or action the user does with the mouse and do action according to
        """

        # First Event is that the user action is a mouse scroll and also the zoomvar and scale var is False
        # So the action now is to scroll through the slices
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.Wheel and self.zoomVar==False and self.scaleVar==False and self.scaleXVar==False and self.scaleYVar==False):
            
            # Check is the scroll is forward + (positive direction)
            if event.angleDelta().y() > 0:

                # Increment the index of the view and draw the new slice 
                self.indexView+=1

                # Check if it is already the last slice do nothing
                if(self.indexView>self.ArrayDicom.shape[2]-1):
                    self.indexView=self.ArrayDicom.shape[2]-1
                # Draw new slice
                else:
                    img=self.ArrayDicom[:,:,self.indexView]  
                    self.image = pg.ImageItem(img)      
                    self.ui.View.addItem(self.image)
            # Check is the scroll is backward - (negative direction)
            else:
                # Decrement the index of the view and draw the new slice 
                self.indexView-=1
                
                # Check if it is already the first slice do nothing
                if(self.indexView<0):
                    self.indexView=0
                # Draw new slice
                else:
                    img=self.ArrayDicom[:,:,self.indexView]  
                    self.image = pg.ImageItem(img)      
                    self.ui.View.addItem(self.image)
            self.pointsTrue.indexArr=self.indexView
            # Draw the points of the current slice if there is any inserted by the user
            # self.DrawPoints()
            # if self.outter==True:
            self.DrawPoints(pointslst=self.pointslst2,points=self.points2,pointsTrue=self.pointsTrue2,collor=2)
            self.DrawPoints(pointslst=self.pointslst1,points=self.points1,pointsTrue=self.pointsTrue1,collor=1)

            self.drawEditvar=False

            return True

        # Second event is that if the user is scrolling the mouse wheel and the scale var is true so increasing of 
        # decreasing the scale of the shape
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.Wheel and self.zoomVar==False and self.scaleVar==True and self.scaleXVar==False and self.scaleYVar==False):

            # Increase the Scale of the shape
            if event.angleDelta().y() > 0:
                self.ScaleUpDown("inc",1)
            # Decrease the Scale of the shape
            else:
                self.ScaleUpDown("dec",1)
            return True

        # Third event is that if the user is scrolling the mouse wheel and the scaleXvar is true so increasing of 
        # decreasing the scale of the shape
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.Wheel and self.zoomVar==False and self.scaleVar==False and self.scaleXVar==True and self.scaleYVar==False):

            # Increase the Scale of the shape
            if event.angleDelta().y() > 0:
                self.ScaleUpDown("inc",2)
            # Decrease the Scale of the shape
            else:
                self.ScaleUpDown("dec",2)
            return True


        # Fourth event is that if the user is scrolling the mouse wheel and the scaleYvar is true so increasing of 
        # decreasing the scale of the shape
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.Wheel and self.zoomVar==False and self.scaleVar==False and self.scaleXVar==False and self.scaleYVar==True):

            # Increase the Scale of the shape
            if event.angleDelta().y() > 0:
                self.ScaleUpDown("inc",3)
            # Decrease the Scale of the shape
            else:
                self.ScaleUpDown("dec",3)
            return True

        # Fifth Event is that the user drags a point so the entire shape is updated
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseMove and self.pointsTrue.Updating==True and self.drawEditvar==False):
            self.DrawPoints()
            self.pointsTrue.Updating=False
            self.drawEditvar=False
        
        # Sixth event is that the user double clicks a point and the delete action is pressed so it deletes the current clicked point
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseButtonDblClick and self.pointdelBool==True ):
            self.pointtoDel=self.pointsTrue.pointDel

            self.pointsTrue.indexArr=self.indexView
            indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
            # check if there is only one point call delete function or if is there multiple points so it deletes the point clicked
            x=indecies[self.pointtoDel]
            if len(indecies)==1:
                self.DeleteAllPoints()
            else:
                self.pointslst[0].pop(x)
                self.pointslst[1].pop(x)
                self.pointslst[2].pop(x)

                self.firstime[self.indexView]-=1

                self.DrawPoints()
        # Seventh event is that the user clicks and draws free hand it detects the mouse press at first
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseButtonPress and self.drawEditvar==True and self.DrawpointsVar==False and (self.outter==True or self.inner==True)):

            # Getting the position of the clicked position
            pos=self.image.mapFromScene(event.pos())
            self.pointslst[0].append(pos.x())
            self.pointslst[1].append(pos.y())
            self.pointslst[2].append(self.indexView)

            indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
            x=indecies[0]

            ## Creating a temp variable that holds the first point the reason is that as the user drags ( draws ) the dragged point changes loaction
            self.temp[0]=self.pointslst[0][x]
            self.temp[1]=self.pointslst[1][x]
            self.temp[2]=self.pointslst[2][x]

            ## Updating the times the user visited the  
            self.firstime[self.indexView]+=1

            # drawing the clicked point
            self.pointsTrue.indexArr=self.indexView
            self.DrawPoints()

            self.pointsTrue.Updating=False

        # Eight event is that the draws free hand it detects the mouse movement path
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseMove and self.drawEditvar==True and self.pointsTrue.Updating==True and (self.outter==True or self.inner==True)):

            indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
            x=indecies[0]

            ## a sleep var to get the mouse point every 0.09 ms
            time.sleep(0.09)
            # print("HALOOOOOO")
            
            ## Updating the first point to its original point
            self.pointslst[0][x]=self.temp[0]
            self.pointslst[1][x]=self.temp[1]     
            self.pointslst[2][x]=self.temp[2]


            ## Getting the position of the mouse on the image
            pos=self.image.mapFromScene(event.pos())

            self.pointslst[0].append(pos.x())
            self.pointslst[1].append(pos.y())
            self.pointslst[2].append(self.indexView)

            ## Updating the firsttime array
            self.firstime[self.indexView]+=1

            self.pointsTrue.indexArr=self.indexView
            ## drawing the points
            self.DrawPoints()


                # self.pointsTrue.Updating=False
            self.pointsTrue.Updating=False
        
        # Ninth event is that the user finishes drawing and is detected when the mouse release happens
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseButtonRelease and self.drawEditvar==True and (self.outter==True or self.inner==True) ):


            indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
            # print(indecies)
            x=indecies[0]
            # print(indecies)

            self.first=0
            ## Updating the first point to its original point

            self.pointslst[0][x]=self.temp[0]
            self.pointslst[1][x]=self.temp[1]     
            self.pointslst[2][x]=self.temp[2]

            self.pointslst[0].pop(x)
            self.pointslst[1].pop(x)
            self.pointslst[2].pop(x)

            self.firstime[self.indexView]-=1

            indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
            print(indecies)
            print(self.pointslst,"After")

            self.pointsTrue.indexArr=self.indexView
            # drawing the points
            self.DrawPoints()

            self.pointsTrue.Updating=False

            self.ui.View.setMouseEnabled(x=True, y=True)
            self.drawEditvar=False
            self.ui.actionedit.setChecked(False)
            self.drawEditvar=False


        # Tenth event is that the user moves the round pointer around 
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseMove and self.drawEditvar==False and self.pointsTrue.Updating==False and self.RoundPointerVar ):
            ## get the position of mouse
            pos=self.image.mapFromScene(event.pos())
            ## setting the indecies of the graph items
            self.pointsTrue.indexArr=self.indexView
            self.pointer.indexArr=self.indexView

   
            
            ## This variable is half the diameter of the round circle pointer
            hs=int(self.sizeo/2)
            # print(hs)

            ## Check if the pointer is withing the bounds of the image
            Checkooo=self.isWithin([0,0],[512,512],[pos.x()+hs,pos.y()+hs])
            Checkooo1=self.isWithin([0,0],[512,512],[pos.x()-hs,pos.y()-hs])
    

            
            ## if not within the bounds of the image do nothing
            if Checkooo==False or Checkooo1==False :
                ## set the variables to false and prevent dragging of the pointer
                if self.MousePressVar==True:
                    self.pointer.Updating=False
                    self.pointer.DragStop=True

            ## if within the bounds
            else:
                ## Allow drag of pointer
                self.pointer.DragStop=False
                self.pointer.Updating=True

                ## get the indices of the input points from the array 
                indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
                ## if indicies is empty do nothing
                if indecies == []:
                    print("fadya")
                else:
                    ## inializing variables needed in this part
                    minind1=0
                    minind2=0
                    indxarr=[]
                    min=sys.maxsize
                    min2 = sys.maxsize
                    space=0
                    tempsize=0
                    beforeidx=0
                    afteridx=0
                    distance=0
                    ## loop on all the points in the slice and get the distance that is min from the pointer location
                    for i in range(len(indecies)):
                        j=indecies[i]
                        distance=self.calc_distance([pos.x(),pos.y()],[self.pointslst[0][j],self.pointslst[1][j]])
                        # distance=self.calc_distance([pos.x()+hs,pos.y()+hs],[self.pointslst[0][j],self.pointslst[1][j]])

                        # get min and index of min 
                        if distance<min:
                            min=distance
                            minind1=i
                    ## if the mouse is not pressed and the pointer is moving change the size of the pointer according to the distance form the min distance point
                    if self.MousePressVar==False:
                        ## space is radius from the true input point we calculate it to make the pointer change radius and touch the true point circumference
                        self.space=1-(8/(min*2))
                        ## Update the size of the pointer
                        self.sizeo=min*2*self.space
                        hs=int(self.sizeo/2)
                        

                   # Loop on all the points again and check for points taht are around the pointer by a threshold
                    for i in range(len(indecies)):
                        j=indecies[i]
            
                        distance=self.calc_distance([pos.x(),pos.y()],[self.pointslst[0][j],self.pointslst[1][j]])
                        if distance <=self.sizeo/2 + ( 1-self.space):
                            # print(distance,"el distance el weird",min,"el min")
                            indxarr.append(i)
                        # if(distance < min2 and distance > min):
                        #     min2 = distance
                        #     minind2=i
                    ## loop on the indicies and get the point before and after the min distance point
                    for i in range(len(indecies)):
                        if i == minind1:
                            if i == 0:
                                beforeidx=len(indecies)-1
                            else:
                                beforeidx=i-1
                            if i == len(indecies)-1:
                                afteridx=0
                            else:
                                afteridx=i+1
                    print(beforeidx,afteridx,"EL indices el mafrod sa7 keda checkkkkkk")


                ## Setting the new Values of the pointer list 
                self.pointerlist[0][0]=pos.x()
                self.pointerlist[1][0]=pos.y()
                self.pointerlist[2][0]=self.indexView
                data2=np.column_stack([pos.x(), pos.y()])


                ## Drawing the new pointer at the new loacation and size
                self.ui.View.removeItem(self.pointer)
                # el 80 fel 25er de 0.31 men el 255
                self.pointer.setData(pos=data2,symbol='o',size=self.sizeo, pxMode=False,symbolBrush=pg.mkBrush(255, 255, 35, 80))
                self.ui.View.addItem(self.pointer)

                ## check is the mouse is pressed so we move the points and add new points to fix the shape
                if self.MousePressVar==True and indecies != []:
                    #get the indicies of the min and second min
                    x1=indecies[minind1]
                    x2=indecies[minind2]
                                        
                    ## calculate the distance from the point min to the point before it and after it to know which distance is greater to insert in it          
                    distancebefore=self.calc_distance([self.pointslst[0][indecies[beforeidx]],self.pointslst[1][indecies[beforeidx]]],[self.pointslst[0][x1],self.pointslst[1][x1]])
                    distanceafter=self.calc_distance([self.pointslst[0][indecies[afteridx]],self.pointslst[1][indecies[afteridx]]],[self.pointslst[0][x1],self.pointslst[1][x1]])
                    
                    ## if the distance before is greater so x2 is that point
                    if distancebefore>distanceafter:
                        x2=indecies[beforeidx]
                        distance=distancebefore
                        print(x2,"el x2")

                    else:
                        x2=indecies[afteridx]
                        distance=distanceafter
                        print(x2,"el x2")


                    print(x1,x2,"EL EXAt")
                    # print(x,x2)
                    
                    ## Now for all the points in the range of the circumrence of the pointer move them as the pointer moves 
                    for i in indxarr:
                        x=indecies[i]
                        # print(space)
                        # print((1-self.space)*(self.pointslst[0][x]-self.pointerlist[0][0]),"de elly enta shayefha")
                        self.pointslst[0][x]=self.pointslst[0][x]+((1-self.space))*(self.pointslst[0][x]-self.pointerlist[0][0])
                        self.pointslst[1][x]=self.pointslst[1][x]+((1-self.space))*(self.pointslst[1][x]-self.pointerlist[1][0])


                    print(distance,"EL distance been 2 largets points")

                    # check if the distance is greater than a trehsold insert a point in between
                    print(self.sizeo,"el size ya beeeh")
                    ## could be changed to a defult value 25 for ex
                    if distance > self.sizeo/2:

                        # calculate the middle between the points
                        midx=(self.pointslst[0][x2] + self.pointslst[0][x1]) / 2
                        midy=(self.pointslst[1][x2] + self.pointslst[1][x1]) / 2
                        
                        ## determining which place to insert the point exactly in according to different cases and the way of drawing the points
                        if (x2<x1):
                            if x2==indecies[0] and x1==indecies[len(indecies)-1]:
                                self.pointslst[0].insert(x1+1,midx+(1-self.space)*(midx-self.pointerlist[0][0]))
                                self.pointslst[1].insert(x1+1,midy+(1-self.space)*(midy-self.pointerlist[1][0]))
                                self.pointslst[2].insert(x1+1,self.indexView)
                            elif x2==indecies[0] and x1==indecies[1]:
                                self.pointslst[0].insert(x2+1,midx+(1-self.space)*(midx-self.pointerlist[0][0]))
                                self.pointslst[1].insert(x2+1,midy+(1-self.space)*(midy-self.pointerlist[1][0]))
                                self.pointslst[2].insert(x2+1,self.indexView)
                            else:
                                self.pointslst[0].insert(x1,midx+(1-self.space)*(midx-self.pointerlist[0][0]))
                                self.pointslst[1].insert(x1,midy+(1-self.space)*(midy-self.pointerlist[1][0]))
                                self.pointslst[2].insert(x1,self.indexView)
                            
                        else:

                            if x1==indecies[0] and x2==indecies[len(indecies)-1]:
                                self.pointslst[0].insert(x2+1,midx+(1-self.space)*(midx-self.pointerlist[0][0]))
                                self.pointslst[1].insert(x2+1,midy+(1-self.space)*(midy-self.pointerlist[1][0]))
                                self.pointslst[2].insert(x2+1,self.indexView)
                                
                            else:
                                self.pointslst[0].insert(x2,midx+(1-self.space)*(midx-self.pointerlist[0][0]))
                                self.pointslst[1].insert(x2,midy+(1-self.space)*(midy-self.pointerlist[1][0]))
                                self.pointslst[2].insert(x2,self.indexView)

                        self.firstime[self.indexView]+=1



                    # draw the points
                    self.DrawPoints()
                    # np.save('pointslst.npy', self.pointslst,allow_pickle=True)

                    # print("ana shagal sa7")

                self.pointer.Updating=False
                # self.ui.View.setMouseEnabled(x=True, y=True)

        # Eleventh event is that the user presses the mouse and the round pointer is active  
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseButtonPress and self.drawEditvar==False and self.pointsTrue.Updating==False and self.RoundPointerVar ):
            # setting the variable need to true and the index of the slice to the graph item point
            self.pointer.Updating=True
            self.MousePressVar=True         
            self.pointer.indexArr=self.indexView
            self.pointsTrue.indexArr=self.indexView

            # self.ui.View.setMouseEnabled(x=False, y=False)

            # get the position
            pos=self.image.mapFromScene(event.pos())
            hs=int(self.sizeo/2)
            # setting the position
            self.pointerlist[0][0]=pos.x()
            self.pointerlist[1][0]=pos.y()
            self.pointerlist[2][0]=self.indexView

            # check if the point pressed is and it is in the bounds of the image
            Checkooo=self.isWithin([0,0],[512,512],[pos.x()+hs,pos.y()+hs])
            Checkooo1=self.isWithin([0,0],[512,512],[pos.x()-hs,pos.y()-hs])
            # if false set the update va to False
            if Checkooo==False or Checkooo1==False:
                # print("henaa")
                self.pointer.Updating=False       
        # Twelveth event is that the user releases the mouse and the round pointer is active  
        if (watched == self.ui.View.viewport() and 
                    event.type() == QtCore.QEvent.MouseButtonRelease and self.drawEditvar==False and self.RoundPointerVar==True ):
                # setting all the variables to false 
                self.MousePressVar=False            
                self.pointer.DragStop=False
                self.pointer.indexArr=self.indexView
                self.pointsTrue.indexArr=self.indexView

                # self.ui.View.setMouseEnabled(x=True, y=True)


        return super().eventFilter(watched, event)

    # isWithin Function
    def isWithin(self,bl,tr,p):

        """
        This Function is responsible check if a point is within the bounds of an image
        """

        if (p[0] > bl[0] and p[0] < tr[0] and p[1] > bl[1] and p[1] < tr[1]) :
            return True
        else :
            return False

    # Draw Points Function
    def DrawPoints(self,pointslst=None,points=None,pointsTrue=None,collor=None):
        
        """
        This Function is responsible to draw the points on the GUI
        """
        # remove all the lines from the  GUI 
        for i in range(len(self.pointss)):
            self.ui.View.removeItem(self.lines[i]) 

        # this checks that if the user did not change the default values of the drawing then it sets them to the defult values
        if pointslst == None:
            docalc=True
            pointslst=self.pointslst
            points=self.points
            pointsTrue=self.pointsTrue
            collor=self.collor
        # else:
        #     docalc=False


        indecies=[i for i,val in enumerate(pointslst[2]) if val==self.indexView]

        xarr= [pointslst[0][i] for i in indecies]
        yarr= [pointslst[1][i] for i in indecies]

        # check if the array to draw is not emptty so it sets the data and draws it
        if ( len(xarr)!=0):
            self.data=[]
            self.data=np.column_stack([xarr, yarr])
            if collor==1:
                pointsTrue.setData(pos=self.data,symbol='o',size=8, pxMode=False,symbolPen="red",symbolBrush="red")
            else:
                pointsTrue.setData(pos=self.data,symbol='o',size=8, pxMode=False,symbolPen="blue",symbolBrush="blue")

            datafake=[]
            xarr.append(xarr[0])
            yarr.append(yarr[0])
            datafake=np.column_stack([xarr, yarr])



            # We create the adjacency array to connect the points together if and only if there is more than 1 point
            adj=[]
            if(len(xarr)-1>1):
                self.InterpolateData(datafake,xarr,yarr)
                x  = [ [None]*0 for _ in range(len(self.x_after_interpolate))]
                for i in range(len(x)-1):
                    x[i]=[i,i+1]
                x[len(x)-1]=[len(x)-1,0]
                adj=x
                adj=np.asarray(adj)
                texts = ["Point %d" % i for i in range(1)]
                
                # Clearing the gui and then redrawing the new points again
                self.ui.View.removeItem(points)
                if collor==1 :
                    points.setData(pos=self.data,adj=adj,pen="blue",symbol='o',size=1, pxMode=True,symbolPen="blue",symbolBrush="blue")
                else:
                    points.setData(pos=self.data,adj=adj,pen="red",symbol='o',size=1, pxMode=True,symbolPen="red",symbolBrush="red")

                self.ui.View.addItem(points)
                self.ui.View.removeItem(pointsTrue)
                self.ui.View.addItem(pointsTrue)
            else:
                # Clearing the gui and then redrawing the new points again but here we do not have points to connect so we only draw the point clicked
                adj=np.asarray(adj)
                texts = ["Point %d" % i for i in range(1)]
                self.ui.View.removeItem(points)
                self.ui.View.removeItem(pointsTrue)
                self.ui.View.addItem(pointsTrue)

        

    def lineMagnitude(self,x1, y1, x2, y2):
        
        """
        This Function is responsible to get the magnitude of the line
        """
        lineMagnitude = mathh.sqrt(mathh.pow((x2 - x1), 2)+ mathh.pow((y2 - y1), 2))
        return lineMagnitude

    #Calc minimum distance from a point and a line segment (i.e. consecutive vertices in a polyline).
    def DistancePointLine (self,px, py, x1, y1, x2, y2):
        
        """
        Calc minimum distance from a point and a line segment (i.e. consecutive vertices in a polyline).
        """
        #http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
        LineMag = self.lineMagnitude(x1, y1, x2, y2)

        if LineMag < 0.00000001:
            DistancePointLine = 9999
            return DistancePointLine

        u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
        u = u1 / (LineMag * LineMag)

        if (u < 0.00001) or (u > 1):
            #// closest point does not fall within the line segment, take the shorter distance
            #// to an endpoint
            ix = self.lineMagnitude(px, py, x1, y1)
            iy = self.lineMagnitude(px, py, x2, y2)
            if ix > iy:
                DistancePointLine = iy
            else:
                DistancePointLine = ix
        else:
            # Intersecting point is on the line, use the formula
            ix = x1 + u * (x2 - x1)
            iy = y1 + u * (y2 - y1)
            DistancePointLine = self.lineMagnitude(px, py, ix, iy)

        return DistancePointLine

    def checkPoint(self,radius,Centerx,Centery,Groundx,Groundy,segs):
        """
        This Function is responsible to check if a point belongs to which sector of the shape
        """
        # set the starting angle with zero and then the end angle + 30 to make sectors of 30 deg angles
        startAngle=0
        endAngle = startAngle+30
        # now loop ont the segments and then check for each point if it meets the creiteria or no
        for j in range(len(segs)):

            # Calculate polar co-ordinates
            for i in range(len(Groundx)):
                polarradius = mathh.sqrt((Groundx[i] - Centerx[1])**2 + ((Groundy[i])- Centery[1])**2)
                Angle =self.calculate_angle((Groundy[i] - Centery[1]),(Groundx[i] - Centerx[1]))
                # print(Angle)
                # Check whether polarradius is less
                # then radius of circle or not and
                # Angle is between startAngle and
                # endAngle or not
                if (Angle >= startAngle and Angle <= endAngle
                                    and polarradius < radius):
                    segs[j][0].append(Groundx[i])
                    segs[j][1].append(Groundy[i])
            # now set the starting angle by the end and increase the end angle
            startAngle=endAngle
            endAngle = startAngle+30

    # Function to calculate the angle
    def calculate_angle(self,x, y):  
        """
        This Function is responsible to calculate the angle
        """
        angle = mathh.atan2(x, y)

        if angle < 0:
            angle += 2 * mathh.pi
        return (180 / mathh.pi) * angle

    def DeleteSinglePoint(self):
        
        """
        This Function is responsible to toggle the deletesingle point Variable
        """
        if self.pointdelBool==True:
            self.pointdelBool=False
        else:
            self.pointdelBool=True
        

    def PointsToggle(self):
        """
        This Function is responsible to toggle the insertion point Variable
        """
        if self.DrawpointsVar==False:
            self.DrawpointsVar=True
        elif self.DrawpointsVar==True:
            self.DrawpointsVar=False


    def ZoomToogle(self):
        """
        This Function is responsible to toggle the zoom option Variable
        """
        if self.zoomVar==False:
            self.zoomVar=True
        else:
            self.zoomVar=False
    



  #*****************************************   To be added later  ********************************************************#

    # def AreaCalculate(self,x_after_interpolate,y_after_interpolate):

    #     tupVerts=[]

    #     for i in range(len(x_after_interpolate)):
    #         n=(x_after_interpolate[i],y_after_interpolate[i])
    #         tupVerts.append(n)

    #     p = Path(tupVerts) # make a polygon
    #     grid = p.contains_points(self.mespoints)
    #     # mask = grid.reshape(512,512) # now you have a mask with points inside a polygon

    #     count = np.count_nonzero(grid)
    #     self.points.Area=count

  #**************************************************************************************************************************#




    # Delete All Points Function
    def DeleteAllPoints(self):
        
        """
        This Function is responsible to delete all the points in the current slice
        """
        
        # get the indecies of the points belonging to the current slice
        indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
        indecies = sorted(indecies, reverse=True)
        
        # loops on all the points and delete them
        for idx in indecies:
            if idx < len(self.pointslst[0]):
                self.pointslst[0].pop(idx)
                self.pointslst[1].pop(idx)
                self.pointslst[2].pop(idx)
        
        # clear the graphs and reset the firstime array of the current slice
        self.ui.View.removeItem(self.points)
        self.ui.View.removeItem(self.pointsTrue)

        for i in range(len(self.pointss)):
                self.ui.View.removeItem(self.lines[i])

        self.firstime[self.indexView]=0



    # Get Position and Insert Function
    def getPosandInsert(self , event):

        """
        This Function is responsible to get the position of the user click and insert a point is the Draw Points Var is True
        """

        # check if the draw points var is true so it inserts a point in the current position
        x = event.pos().x()
        y = event.pos().y()
        # print(x,y,"points clickedddd")
        z=self.indexView
        if self.DrawpointsVar==True and self.pointdelBool==False and self.circleVar==False and self.ellipseVar==False and self.drawEditvar==False and (self.outter==True or self.inner==True):

            # get the x,y,z of the user click

            # setting the index of the todraw points with the slice number
            self.pointsTrue.indexArr=self.indexView
            # get the number of times the user inserted in this slice
            newl=self.firstime[self.indexView]

            # check if it is first time or has not been visited before so we insert the point directly else we check if the point is between 
            # existing points and see to which segment it belongs and insert between the points of that segment
            if newl!=0 and newl!=1:

                # check to which segment the new point belongs
                p1=[x,y]
                self.DrawPoints()
                ind=self.towhichseg(p1,self.DistanceArray,self.range_of_points)

                indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
                x=indecies[ind]
                # print(indecies)
                # Insert the point in its new correct location in the pointlst array 
                self.pointslst[0].insert(x+1,p1[0])
                self.pointslst[1].insert(x+1,p1[1])
                self.pointslst[2].insert(x+1,z)
            
            # Insert the points directly in the array
            else:
                
                self.pointslst[0].append(x)
                self.pointslst[1].append(y)
                self.pointslst[2].append(z)

            # increase the number of times the slice has points in
            self.firstime[self.indexView]+=1

            # appending the z slice number

            # drawing the points
            self.DrawPoints()


            # saving the points for expiremental functions 
            np.save('pointslst.npy', self.pointslst,allow_pickle=True)
        # Check if the draw circle option is selected then a circle is drawn
        elif self.DrawpointsVar==True and self.pointdelBool==False and self.circleVar==True and self.ellipseVar==False and (self.outter==True or self.inner==True):
            self.DeleteAllPoints()
            self.DrawCircle(x,y)

        # Check if the draw circle option is selected then an elipse is drawn
        elif self.DrawpointsVar==True and self.pointdelBool==False and self.circleVar==False and self.ellipseVar==True and (self.outter==True or self.inner==True):
            self.DeleteAllPoints()
            self.DrawEllipse(x,y)

        else:
            if  self.newEllipseVar== True:
                
                if self.counter >=3:

                    self.newellipse()
                self.ellipsecounter+=1
            else:
             return None
    
    # calculate the distance between two given points
    def calc_distance(self,p1, p2):
        return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)


    # Interpoated Data Function
    def InterpolateData(self,data,xarr,yarr):

        """
        This Function is responsible to interpolate the data and get new x and y interpolated arrays
        """
        x=[0]
        # calculate the distance between each corresponding points 
        for j in range(0,len(xarr)-1):
            
            distance=self.calc_distance(data[j],data[j+1])
            x.append(x[j]+distance)

        self.DistanceArray=x.copy()
        spacing=0.12

        x=np.asarray(x)

        # get a range of points between the min and max distance with constant spacing
        self.range_of_points =  np.arange(0, max(x),0.15)


        x=np.asarray(x)

        # use cubic spline to calculate new interpolated x points
        cs_x = CubicSpline(x, xarr)
        self.x_after_interpolate=cs_x(self.range_of_points)
        
        # use cubic spline to calculate new interpolated y points
        cs_y = CubicSpline(x, yarr)
        self.y_after_interpolate=cs_y(self.range_of_points)

        # make the data array the new x,y interpolated points to be used in drawing
        self.data=np.column_stack([self.x_after_interpolate,self.y_after_interpolate])

        # it then sets the interpolated data arr to that of the outer or inner shapes to be later used in the region function
        if self.inner==True:
            self.interpointssarr2[self.indexView][0]=self.x_after_interpolate
            self.interpointssarr2[self.indexView][1]=self.y_after_interpolate
        elif self.outter == True:
            self.interpointssarr1[self.indexView][0]=self.x_after_interpolate
            self.interpointssarr1[self.indexView][1]=self.y_after_interpolate

    # To which Segment Function

    def towhichseg(self,p1,DistArray,range_of_points):

        """
        This Function is responsible to check the new point is closer to which segment and returns the index of this segment
        """

        minind=0
        min=sys.maxsize
        for i in range(len(self.x_after_interpolate)):
            
            # claulate the distance between the point and every other point in the interpolated data
            # then it checks which point is closer to the inserted point and then then the point belongs to the segment the interpolated x,y falls on
            distance=self.calc_distance(p1,[self.x_after_interpolate[i],self.y_after_interpolate[i]])
            if distance<min:
                min=distance
                minind=i
        # get the index of the segment the new point falls on
        for j in range(len(DistArray)):
            if DistArray[j] <= range_of_points[minind] <= DistArray[j+1]:
                return j


    
def main():

    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()
    
    

if __name__ == '__main__':
    main()

