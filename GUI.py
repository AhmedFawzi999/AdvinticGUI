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

        # Intialize the Varaibles needed throughout the Application
        self.ArrayDicom = [] # Store the Dicom Images
        self.ConstPixelSpacing = [] # Array to Store the Spacing between pixels
        self.indexView = 0 # The Current Slice index
        self.zoomVar=False # Variable to check if zoom action is toggled or no
        self.pointdelBool=False # Variable to check if delete single point action is toggled or no
        self.DrawpointsVar=False # Variable to check if draw points action is toggled or no
        self.pointslst  = [ [None]*0 for _ in range(3)]  # Array to store the x,y,z of each point
        self.pointtoDel=0  # A variable to store the point to delete
        self.x_after_interpolate=[]  # An Array to store the x interpolated points
        self.y_after_interpolate=[]  # An Array to store the y interpolated points
        self.range_of_points=[] # An Array to store range of points used to obtain x,y interpolated and segments
        x, y = np.meshgrid(np.arange(512), np.arange(512)) 
        x, y = x.flatten(), y.flatten()
        self.mespoints = np.vstack((x,y)).T 
        self.DistanceArray=[]  # Array to store distances between points
        self.firstime=[]  # Array to store is a slice is visited before by the user and will help in the deleting and insertions
        self.scaleVar=False # Variable to check if scale action is toggled or no


        # Toggled and connecting each action button to its fucntion
        self.ui.actionZoom.toggled.connect(self.ZoomToogle)
        self.ui.actionOpen_Dicom.toggled.connect(self.UploadImage)
        self.ui.actionaddPoints.toggled.connect(self.PointsToggle)
        self.ui.actiondeleteShape.triggered.connect(self.DeleteAllPoints)
        self.ui.actionDelPoint.toggled.connect(self.DeleteSinglePoint)
        self.ui.actionTranslate.toggled.connect(self.Translate)
        self.ui.actionscale.toggled.connect(self.Scale)


        # Creating two objects of Class Graph one to draw the user input points and the other for the interpolated points
        self.points=Graph(self.pointslst,self.indexView)
        self.pointsTrue=Graph(self.pointslst,self.indexView)






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
    def ScaleUpDown(self,var):

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
        if var ==1:
            mul = 1+0.05    # Zoom in 0.05
        else:
            mul = 1-0.05    # Zoom out 0.05
        
        # change the data of the shape by the new scale
        new_data = (data - pos) * mul + pos
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
            event.type() == QtCore.QEvent.Wheel and self.zoomVar==False and self.scaleVar==False):
            
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
            self.DrawPoints()
            return True

        # Second event is that if the user is scrolling the mouse wheel and the scale var is true so increasing of 
        # decreasing the scale of the shape
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.Wheel and self.zoomVar==False and self.scaleVar==True):

            # Increase the Scale of the shape
            if event.angleDelta().y() > 0:
                self.ScaleUpDown(1)
            # Decrease the Scale of the shape
            else:
                self.ScaleUpDown(2)
            return True

        # Third Event is that the user drags a point so the entire shape is updated
        if (watched == self.ui.View.viewport() and 
            event.type() == QtCore.QEvent.MouseMove and self.pointsTrue.Updating==True):
            
            self.DrawPoints()
            self.pointsTrue.Updating=False
        
        # Fourth event is that the user double clicks a point and the delete action is pressed so it deletes the current clicked point
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

        return super().eventFilter(watched, event)


    # Draw Points Function
    def DrawPoints(self):

        """
        This Function is responsible to draw the points on the GUI
        """
        indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]

        xarr= [self.pointslst[0][i] for i in indecies]
        yarr= [self.pointslst[1][i] for i in indecies]

        # check if the array to draw is not emptty so it sets the data and draws it
        if ( len(xarr)!=0):
            self.data=[]
            self.data=np.column_stack([xarr, yarr])
            self.pointsTrue.setData(pos=self.data,symbol='o',size=15, pxMode=True,symbolPen="red",symbolBrush="red")

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
                self.ui.View.removeItem(self.points)
                self.points.setData(pos=self.data,adj=adj,pen="blue",symbol='o',size=1, pxMode=True,symbolPen="blue",symbolBrush="blue")
                self.ui.View.addItem(self.points)
                self.ui.View.removeItem(self.pointsTrue)
                self.ui.View.addItem(self.pointsTrue)
            else:
                # Clearing the gui and then redrawing the new points again but here we do not have points to connce so we only draw the point clicked
                adj=np.asarray(adj)
                texts = ["Point %d" % i for i in range(1)]
                self.ui.View.removeItem(self.points)
                self.ui.View.removeItem(self.pointsTrue)
                self.ui.View.addItem(self.pointsTrue)


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
        self.firstime[self.indexView]=0



    # Get Position and Insert Function
    def getPosandInsert(self , event):

        """
        This Function is responsible to get the position of the user click and insert a point is the Draw Points Var is True
        """

        # check if the draw points var is true so it inserts a point in the current position
        if self.DrawpointsVar==True and self.pointdelBool==False:

            # get the x,y,z of the user click
            x = event.pos().x()
            y = event.pos().y()
            z=self.indexView
            # setting the index of the todraw points with the slice number
            self.pointsTrue.indexArr=self.indexView
            # get the number of times the user inserted in this slice
            newl=self.firstime[self.indexView]

            # check if it is first time or has not been visited before so we insert the point directly else we check if the point is between 
            # existing points and see to which segment it belongs and insert between the points of that segment
            if newl!=0 and newl!=1:

                # check to which segment the new point belongs
                p1=[x,y]
                ind=self.towhichseg(p1,self.DistanceArray,self.range_of_points)

                indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
                x=indecies[ind]
                # Insert the point in its new correct location in the pointlst array 
                self.pointslst[0].insert(x+1,p1[0])
                self.pointslst[1].insert(x+1,p1[1])
            
            # Insert the points directly in the array
            else:
                
                self.pointslst[0].append(x)
                self.pointslst[1].append(y)
            # increase the number of times the slice has points in
            self.firstime[self.indexView]+=1

            # appending the z slice number
            self.pointslst[2].append(z)

            # drawing the points
            self.DrawPoints()


            # saving the points for expiremental functions 
            np.save('pointslst.npy', self.pointslst,allow_pickle=True)

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
        self.range_of_points =  np.arange(0, max(x),15)


        x=np.asarray(x)

        # use cubic spline to calculate new interpolated x points
        cs_x = CubicSpline(x, xarr)
        self.x_after_interpolate=cs_x(self.range_of_points)
        
        # use cubic spline to calculate new interpolated y points
        cs_y = CubicSpline(x, yarr)
        self.y_after_interpolate=cs_y(self.range_of_points)

        # make the data array the new x,y interpolated points to be used in drawing
        self.data=np.column_stack([self.x_after_interpolate,self.y_after_interpolate])

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

