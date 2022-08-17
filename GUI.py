from turtle import color, pen, pencolor
from sympy import symbols
from imports import * 


class Graph(pg.GraphItem):
    def __init__(self,arr,idxx):
        self.dragPoint = None
        self.dragOffset = None
        self.lst=arr
        self.indexArr=idxx
        # self.textItems = []
        pg.GraphItem.__init__(self)
        self.scatter.sigHovered.connect(self.clicked)
        self.scatter.setData(hoverable="True")
        
    def setData(self, **kwds):
        # self.text = kwds.pop('text', [])
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        # self.setTexts(self.text)
        self.updateGraph()
        
    # def setTexts(self, text):
    #     for i in self.textItems:
    #         i.scene().removeItem(i)
    #     self.textItems = []
    #     for t in text:
    #         item = pg.TextItem(t)
    #         self.textItems.append(item)
    #         item.setParentItem(self)
        
    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        # for i,item in enumerate(self.textItems):
        #     item.setPos(*self.data['pos'][i])
        
        
    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return
        
        if ev.isStart():

            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return
        
        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        
        print(self.data['pos'][ind][0],"heehehehehehehehehehsdijasmdsmd")

        indecies=[i for i,val in enumerate(self.lst[2]) if val==self.indexArr]
        # xarr= [self.pointslst[0][i] for i in indecies]
        # yarr= [self.pointslst[1][i] for i in indecies]

        x=indecies[ind]
        self.lst[0][x]=self.data['pos'][ind][0]
        self.lst[1][x]=self.data['pos'][ind][1]
        self.updateGraph()
        ev.accept()
        
    def clicked(self, pts):
        print("clicked: %s" % pts)


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()
        # self.setGeometry(600, 300, 400, 200)
        self.setWindowTitle('Dicom Viewer')
        pg.setConfigOption('background', 'w')

        # self.ui.Upload.clicked.connect(self.UploadImage)
        self.ui.actionZoom.toggled.connect(self.ZoomToogle)
        
        self.ArrayDicom = []
        self.ConstPixelSpacing = []
        self.indexView = 0

        self.ui.View.viewport().installEventFilter(self)
        self.ui.View.setAspectLocked(lock=True, ratio=1)
        self.ui.View.invertY(True)
        # self.ui.View.viewport().sigMouseMoved().connect(self.mouseover)
        # self.ui.View.setAspectLocked()
        self.ui.View.getPlotItem().hideAxis('left')
        self.ui.View.getPlotItem().hideAxis('bottom')
        # self.ui.View.setMouseEnabled(x=False, y=False)
        self.ui.actionOpen_Dicom.toggled.connect(self.UploadImage)

        self.zoomVar=False
        # self.ViewportVar=False

        # scatterplot = pg.ScatterPlotItem(xarr, yarr, symbol='o', size=7 ,pencolor="red")
        # scatterplot.setBrush(pg.mkBrush("red"))
        # self.ui.MPR1.addItem(scatterplot)
        self.ui.View.setAntialiasing(True)

        self.pointsVar=False
        self.ui.actionaddPoints.toggled.connect(self.PointsToggle)
        self.pointslst  = [ [None]*0 for _ in range(3)] 

        self.points=Graph(self.pointslst,self.indexView)
        self.pointsTrue=Graph(self.pointslst,self.indexView)


        # line = pg.LineSegmentROI([[100,265], [250, 170]], pen=(4,9)) 
        # self.ui.View.addItem(line)
        self.x_after_interpolate=[]
        self.y_after_interpolate=[]






    def mouseover(self):
        print("hiiii")
    def UploadImage(self):

        self.path= QFileDialog.getExistingDirectory()
        # print(self.path)
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        for i in onlyfiles:
            if os.path.splitext(i)[-1].lower() !='.dcm':
                print("ana hena")
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Choose Dicom Files Only!')
                break
        slices=self.load_and_calculate_Thickness(self.path)
        self.slicedata=slices[0]



        ConstPixelDims = (int(slices[0].Rows), int(slices[0].Columns), len(slices))

        self.ConstPixelSpacing = (float(slices[0].PixelSpacing[0]), float(slices[0].PixelSpacing[1]), float(slices[0].SliceThickness))

        self.ArrayDicom = np.zeros(ConstPixelDims, dtype=slices[0].pixel_array.dtype)

        idx=len(slices)-1
        self.SetImagedata(self.ArrayDicom,slices,idx)

        # TO ASK DOCTOR AHMED
        self.ArrayDicom=np.rot90(self.ArrayDicom,1)
        self.ArrayDicom=numpy.flipud(self.ArrayDicom)
        
        img=self.ArrayDicom[:,:,0]
                
        # self.indexView=int(self.ArrayDicom.shape[2]/2)

        self.image = pg.ImageItem(img)      
        self.ui.View.addItem(self.image)

        self.image.mouseClickEvent = self.getPosAxial

        


        # # ##################################axial view##############################

       
        # self.ui.View.addItem(self.horizontalLine)
        # self.ui.View.addItem(self.verticalLine)

    def SetImagedata(self, ArrayDicom,slices,idx):
        for s in slices:
            ArrayDicom[:,:,idx] = s.pixel_array
            idx-=1
    def load_and_calculate_Thickness(self, path):
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

    def eventFilter(self, watched, event):

            if (watched == self.ui.View.viewport() and 
                event.type() == QtCore.QEvent.Wheel and self.zoomVar==False):
                if event.angleDelta().y() > 0:
                    self.indexView+=1
                    if(self.indexView>self.ArrayDicom.shape[2]-1):
                        self.indexView=self.ArrayDicom.shape[2]-1
                    else:
                        img=self.ArrayDicom[:,:,self.indexView]  
                        self.image = pg.ImageItem(img)      
                        self.ui.View.addItem(self.image)
                else:
                    self.indexView-=1
                    if(self.indexView<0):
                        self.indexView=0
                    else:
                        img=self.ArrayDicom[:,:,self.indexView]  
                        self.image = pg.ImageItem(img)      
                        self.ui.View.addItem(self.image)
                indecies=[i for i,val in enumerate(self.pointslst[2]) if val==self.indexView]
                xarr= [self.pointslst[0][i] for i in indecies]
                yarr= [self.pointslst[1][i] for i in indecies]
                self.points=Graph(self.pointslst,self.indexView)
                self.data=[]
                self.data=np.column_stack([xarr, yarr])
                self.ui.View.removeItem(self.points)
                self.points.setData(pos=self.data,symbol='o',size=10, pxMode=True,symbolPen="red",symbolBrush="red")
                self.ui.View.addItem(self.points)

                # self.points=Graph.setData(xarr,yarr)
                # self.scatterplot = pg.ScatterPlotItem(xarr,yarr, symbol='o', size=20 ,pencolor="red",hoverable=True,pxMode=True)
                # self.scatterplot.setBrush(pg.mkBrush("red"))
                # self.ui.View.addItem(self.scatterplot)
                # self.scatterplot.sigClicked.connect(self.clickedd)

                return True
            # if (watched == self.ui.View.viewport() and 
            #     event.type() == QtCore.QEvent.le and self.zoomVar==False):
            # if (watched == self.ui.View.viewport() and 
            #     event.type() == QtCore.QEvent.MouseMove):
            #     print("heheheheeh")
            return super().eventFilter(watched, event)

    def clickedd(self, pts):
        print("clicked: %s" % pts)    
    
    def PointsToggle(self):
        if self.pointsVar==False:
            self.pointsVar=True
        elif self.pointsVar==True:
            self.pointsVar=False

    def getPosAxial(self , event):

        """
        Get the position of the user click in the axial view
        """
        
        if self.pointsVar==True:
            x = event.pos().x()
            print(x)
            y = event.pos().y()
            print(y)
            z=self.indexView
            # xarr=[]
            # yarr=[]
            self.pointslst[0].append(x)
            self.pointslst[1].append(y)
            self.pointslst[2].append(z)



            indecies=[i for i,val in enumerate(self.pointslst[2]) if val==z]
            xarr= [self.pointslst[0][i] for i in indecies]
            yarr= [self.pointslst[1][i] for i in indecies]
            self.data=[]
            self.data=np.column_stack([xarr, yarr])
            self.ui.View.removeItem(self.points)
            self.pointsTrue.setData(pos=self.data,symbol='o',size=10, pxMode=True,symbolPen="red",symbolBrush="red")
            self.ui.View.addItem(self.pointsTrue)

            datafake=[]
            xarr.append(xarr[0])
            yarr.append(yarr[0])
            datafake=np.column_stack([xarr, yarr])



            # self.points.setData(pos=self.data,symbol='o',size=7, pxMode=True,symbolPen="red",symbolBrush="red")

            adj=[]
            if(len(self.pointslst[0])>1):
                self.InterpolateData(datafake,xarr,yarr)
                for i in range(len(self.x_after_interpolate)):
                    adj.append([i,i+1])
                adj.append([len(self.x_after_interpolate),0])
            # else :
            #     self.x_after_interpolate.append(self.pointslst[0][0])
            #     self.y_after_interpolate.append(self.pointslst[1][0])


            adj=np.asarray(adj)
            texts = ["Point %d" % i for i in range(1)]
            # self.points=Graph(self.pointslst,self.indexView)
            self.ui.View.removeItem(self.points)
            self.points.setData(pos=self.data,symbol='o',size=1, pxMode=True,symbolPen="blue",symbolBrush="blue")
            self.ui.View.addItem(self.points)
            np.save('pointslst.npy', self.pointslst,allow_pickle=True)



            # self.scatterplot = pg.ScatterPlotItem(xarr,yarr, symbol='o', size=20 ,pencolor="red",hoverable=True,pxMode=True)
            # self.scatterplot.setBrush(pg.mkBrush("red"))
            # self.ui.View.addItem(self.scatterplot)
            # self.scatterplot.sigClicked.connect(self.clickedd)

        else:
            return None
    
    def calc_distance(self,p1, p2):
        return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

    def InterpolateData(self,data,xarr,yarr):
        x=[0]
        for j in range(0,len(xarr)-1):
            
            distance=self.calc_distance(data[j],data[j+1])
            x.append(x[j]+distance)

        range_of_points_artery=[]
        spacing=0.12

        x=np.asarray(x)


        range_of_points_artery =  np.arange(0, max(x),0.1)


        x=np.asarray(x)
        # Xdata=np.asarray(self.pointslst[0])

        cs_x = CubicSpline(x, xarr)
        self.x_after_interpolate=cs_x(range_of_points_artery)

        cs_y = CubicSpline(x, yarr)
        self.y_after_interpolate=cs_y(range_of_points_artery)
        self.data=np.column_stack([self.x_after_interpolate,self.y_after_interpolate])


    def clicked(self, pts):
        print("clicked: %s" % pts)

    def ZoomToogle(self):
        if self.zoomVar==False:
            self.zoomVar=True
            # self.ui.Zoom.setStyleSheet("background-color : green")
            print("True")
        else:
            self.zoomVar=False
            # self.ui.Zoom.setStyleSheet("background-color : red")
            print("False")
    
def main():

    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()
    
    

if __name__ == '__main__':
    main()

