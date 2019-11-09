#!/usr/bin/env python
# coding: utf-8

# # Willowbend DICOM Enhanced
# <img src="Title.png" align="left" width="45%" height="45%">

# A dialog-based DICOM to video converter.
# 
# **DICOM (Digital Imaging and Communications in Medicine)** is a standard for handling, storing, printing, and transmitting information in medical imaging. DICOM files can be exchanged between two entities that are capable of receiving image and patient data in DICOM format by following network communications protocol. DICOM has been widely adopted by hospitals and is making inroads in smaller applications like dentists' and doctors' offices.
# 
# This project is to implement the process of conversion from DICOM format to video format (avi) in order to meet the needs and requirements for universal computer systems (PC, Mac, Linux, etc.). So the ordinary users of such systems can use the converted file to present, communicate and store the universal files. Case reports in medical conferences, educations of clinical medicine will become more convenient to use universal video formats in the slide presentations.

# ## Libraries

# In[1]:


import SimpleITK as sitk
import cv2
import pydicom
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog


# ## Helper Functions

# ### Basic Helper Functions

# In[2]:


def loadFile(filename):
    ds = sitk.ReadImage(filename)
    img_array = sitk.GetArrayFromImage(ds)
    frame_num, width, height = img_array.shape
    return img_array, frame_num, width, height


# In[3]:


def loadFileInformation(filename):
    information = {}
    ds = pydicom.read_file(filename)
    
    information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['PatientBirthDate'] = ds.PatientBirthDate
    information['PatientSex'] =  ds.PatientSex
    information['StudyID'] = ds.StudyID
    information['StudyDate'] = ds.StudyDate
    information['StudyTime'] = ds.StudyTime
    information['InstitutionName'] = ds.InstitutionName
    information['Manufacturer'] = ds.Manufacturer
    information['NumberOfFrames'] = ds.NumberOfFrames
    information['CineRate'] = ds.CineRate # extract the frame per second value
    
    return information # The return type is dictionary


# In[4]:


def autoEqualize(img_array):
    img_array_list = []
    for img in img_array:
        img_array_list.append(cv2.equalizeHist(img))
    img_array_equalized = np.array(img_array_list)
    return img_array_equalized


# In[5]:


def limitedEqualize(img_array, limit):
    img_array_list = []
    for img in img_array:
        clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(8,8))  #CLAHE (Contrast Limited Adaptive Histogram Equalization)
        img_array_list.append(clahe.apply(img))
        
    img_array_limited_equalized = np.array(img_array_list, dtype=np.uint8)
    return img_array_limited_equalized   


# In[6]:


def writeVideo(img_array, filename, directory, targetFormat): # img_array is a single DICOM file
    frame_num, width, height = img_array.shape
    
    if targetFormat == 'AVI':   # If choose the AVI output format   
        filename_output = directory + '/' + filename.split('.')[0].split('/')[-1] + '.avi'  
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G') # Motion-jpeg codec

        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #video = cv2.VideoWriter(filename_output, fourcc, 15, (width, height))
        # Above is for Mac OSX use only./////////////////////////////////////////////////////////////

        
        #fourcc = cv2.VideoWriter_fourcc('M','P','E','G') # MPEG
        
        #fourcc = cv2.VideoWriter_fourcc('Y','4','1','P') # Brooktree YUV 4:1:1
    elif targetFormat == 'MP4': # If choose the MP4 output format
        filename_output = directory + '/' + filename.split('.')[0].split('/')[-1] + '.mp4'
        fourcc = cv2.VideoWriter_fourcc('M','P','4','2') # MPEG-4        
    
    # Key statement: default value is 15./////////////////////////
    cineRate = int(informations[filename]['CineRate'])
    
    video = cv2.VideoWriter(filename_output, fourcc, cineRate, (width, height)) # Initialize Video File 
    # The parameter cineRate is the frame per second. 
    
    for frame in img_array:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        video.write(frame_rgb) # Write video file frame by frame
        
        #cv2.imshow('frame', frame) # Show the videos
        
    video.release()


# ## GUI Helper Function

# In[7]:


def browseFileButton():
    global filenames
    file_list = []
    
    # The variable informations is all the dicom information dictionary, 
    # while the variable information is the first dcm file(filename[0]) dicom information
    
    try:
        filenames = filedialog.askopenfilenames(filetypes=(('DICOM files', '*.dcm'), ('All files', '*.*')))
        
        # Extract the first one's information
        information = loadFileInformation(filenames[0])
        
        
        for filename in filenames:
            item = filename.split('/')[-1]
            file_list.append(item)

            file_list_str = str(file_list) + ' -- ' + str(len(filenames)) + ' files'
        
        # The files picked up are TUPLE!!!!!! ///////////////////////////

        text_filename.delete('1.0', tk.END)
        text_filename.insert('1.0', filenames[0])
        
        text_filenames.delete('1.0', tk.END)
        text_filenames.insert('1.0', file_list_str)

        text_PatientID.delete('1.0', tk.END)
        text_PatientID.insert('1.0', information['PatientID'])

        text_PatientName.delete('1.0', tk.END)
        text_PatientName.insert('1.0', information['PatientName'])

        text_PatientSex.delete('1.0', tk.END)
        text_PatientSex.insert('1.0', information['PatientSex'])

        text_PatientBirthDate.delete('1.0', tk.END)
        text_PatientBirthDate.insert('1.0', information['PatientBirthDate'])

        text_StudyID.delete('1.0', tk.END)
        text_StudyID.insert('1.0', information['StudyID'])

        text_StudyDate.delete('1.0', tk.END)
        text_StudyDate.insert('1.0', information['StudyDate'])

        text_StudyTime.delete('1.0', tk.END)
        text_StudyTime.insert('1.0', information['StudyTime'])

        text_InstitutionName.delete('1.0', tk.END)
        text_InstitutionName.insert('1.0', information['InstitutionName'])

        text_Manufacturer.delete('1.0', tk.END)
        text_Manufacturer.insert('1.0', information['Manufacturer'])

        text_NumberOfFrames.delete('1.0', tk.END)
        text_NumberOfFrames.insert('1.0', information['NumberOfFrames'])        
          
        text_fps.delete('1.0', tk.END)
        text_fps.insert('1.0', information['CineRate'])        
        
        text_file_num.delete('1.0', tk.END)
        text_file_num.insert('1.0', len(filenames))
      
    except:
        filenames = {}


# In[8]:


def loadFileButton():
    global img_array, frame_num, width, height, informations, isLoad
    img_array = {}
    frame_num = {}
    width = {}
    height = {}
    informations = {}
    
    if filenames == ():
        messagebox.showwarning("No File", "Sorry, no file loaded! Please choose DICOM file first.")
    else:
        try:
            for filename in filenames:                
                img_array[filename], frame_num[filename], width[filename], height[filename] = loadFile(filename)
                
                # Extract the all the information including fps(Frame per Second)
                informations[filename] = loadFileInformation(filename) # Return is a dictionary
                # The keys are filenames
                isLoad = 1
            messagebox.showinfo("DICOM File Loaded", "DICOM file successfully loaded!")
        except:
            messagebox.showwarning("File Loading Failed", "Sorry, file loading failed! Please check the file format.")


# In[9]:


def convertVideoButton():
    global isLoad, clipLimit, filename, fps    
             
    if filenames == ():
        messagebox.showwarning("No File to be Converted", "Sorry, no file to be converted! Please choose a DICOM file first.")
    elif isLoad == 0:
        messagebox.showwarning("No File Loaded", "Sorry, no file loaded! Please load the chosen DICOM file.")
    
    else:
        clipLimit = float(text_clipLimit.get('1.0', tk.END))
        targetFormat = combo_target_format.get().rstrip()
            
        directory = filedialog.askdirectory()
        
        if directory == '':
            messagebox.showwarning("No Directory", "Sorry, no directory shown! Please specify the output directory.")
        else:
            for filename in filenames:  
                img_array_limited_equalized = limitedEqualize(img_array[filename], clipLimit)
                writeVideo(img_array_limited_equalized, filename, directory, targetFormat)
                #messagebox.showinfo("Video File Converted", "Video file successfully generated!")
                isLoad = 0
            messagebox.showinfo("Video File Converted", targetFormat + " video(s) successfully converted!")


# In[10]:


def about():
    about_root=tk.Tk()
    
    w = 370 # width for the Tk root
    h = 230 # height for the Tk root

    # get screen width and height
    ws = about_root.winfo_screenwidth() # width of the screen
    hs = about_root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen 
    # and where it is placed
    about_root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    about_root.title('About Willowbend DICOM')  
    about_root.iconbitmap('Heart.ico')

    label_author=tk.Label(about_root,text='Willowbend DICOM Version 2.8', font=('tahoma', 9))
    label_author.place(x=90,y=30)

    label_author=tk.Label(about_root,text='Copyright (C) 2019', font=('tahoma', 9))
    label_author.place(x=125,y=60)
    
    label_author=tk.Label(about_root,text='Author: Chuan Yang', font=('tahoma', 9))
    label_author.place(x=125,y=90)
    
    label_author=tk.Label(about_root,text='Shengjing Hospital of China Medical University', font=('tahoma', 9))
    label_author.place(x=65,y=120)
   

    button_refresh=ttk.Button(about_root, width=15, text='OK', command=about_root.destroy)
    button_refresh.place(x=135, y=170)

    about_root.mainloop()


# ## Main Stream

# In[11]:


# Main Frame////////////////////////////////////////////////////////////////////////////////////////
root = tk.Tk()

w = 949 # width for the Tk root
h = 720 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/4) - (h/4)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#root.attributes('-fullscreen', True)
root.title('Willowbend DICOM Enhanced')
root.iconbitmap('Heart.ico')

isLoad = 0
clipLimit = 1.5
fps = 0
filename = ''
filenames = ()

# //////// Frame /////////////////////////////

label_Patients=tk.Label(root,width=128, height=43, font=('tahoma', 9), relief='raised', borderwidth=2)
label_Patients.place(x=20,y=15)

#///////////Image Title///////////////////////////////
photo=tk.PhotoImage(file='Title.png')
label_photo=tk.Label(root, image=photo, relief='sunken', borderwidth=3)
label_photo.place(x=300,y=35)

#/////////////Text///////////////////////////////////////////////////////////////////

text_PatientID=tk.Text(root, width=26,height=1, font=('tahoma', 9), bd=1)
text_PatientID.place(x=60, y=90)
label_PatientID=tk.Label(root, text='Patient ID', font=('tahoma', 9))
label_PatientID.place(x=60,y=60)

#//////////////////
y_position = 180
text_PatientName=tk.Text(root, width=28,height=1, font=('tahoma', 9), bd=1)
text_PatientName.place(x=60, y=y_position)
label_PatientName=tk.Label(root, text='Patient\'s Name:', font=('tahoma', 9))
label_PatientName.place(x=60,y=y_position-30)

text_PatientSex=tk.Text(root, width=12,height=1, font=('tahoma', 9), bd=1)
text_PatientSex.place(x=340, y=y_position)
label_PatientSex=tk.Label(root, text='Gender:', font=('tahoma', 9))
label_PatientSex.place(x=340,y=y_position-30)

text_PatientBirthDate=tk.Text(root, width=24,height=1, font=('tahoma', 9), bd=1)
text_PatientBirthDate.place(x=500, y=y_position)
label_PatientBirthDate=tk.Label(root, text='Birth Date:', font=('tahoma', 9))
label_PatientBirthDate.place(x=500,y=y_position-30)

text_fps = tk.Text(root, width=6,height=1, font=('tahoma', 9), bd=1)
text_fps.place(x=760, y=y_position)
label_text_fps = tk.Label(root, text='Cine Rate', font=('tahoma', 9))
label_text_fps.place(x=760,y=y_position-30)

label_fps = tk.Label(root, text='fps', font=('tahoma', 9))
label_fps.place(x=830,y=y_position)

text_fps.delete('1.0', tk.END)
text_fps.insert('1.0', fps)

#//////////////////////////////////////////////////////////////////////////////////
y_position = 250
text_StudyID=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_StudyID.place(x=60, y=y_position)
label_StudyID=tk.Label(root, text='Study ID:', font=('tahoma', 9))
label_StudyID.place(x=60,y=y_position-30)

text_StudyDate=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_StudyDate.place(x=340, y=y_position)
label_StudyDate=tk.Label(root, text='Study Date:', font=('tahoma', 9))
label_StudyDate.place(x=340,y=y_position-30)

text_StudyTime=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_StudyTime.place(x=600, y=y_position)
label_StudyTime=tk.Label(root, text='Study Time:', font=('tahoma', 9))
label_StudyTime.place(x=600,y=y_position-30)

#////////////////////////////////////
y_position = 320
text_InstitutionName=tk.Text(root, width=60,height=1, font=('tahoma', 9), bd=1)
text_InstitutionName.place(x=60, y=y_position)
label_InstitutionName=tk.Label(root, text='Institution Name:', font=('tahoma', 9))
label_InstitutionName.place(x=60,y=y_position-30)

text_Manufacturer=tk.Text(root, width=42,height=1, font=('tahoma', 9), bd=1)
text_Manufacturer.place(x=560, y=y_position)
label_Manufacturer=tk.Label(root, text='Manufacturer:', font=('tahoma', 9))
label_Manufacturer.place(x=560,y=y_position-30)

# File Name
y_position = 390
text_filename=tk.Text(root, width=87,height=1, font=('tahoma', 9), bd=1)
text_filename.place(x=60, y=y_position)
label_filename=tk.Label(root, text='DICOM Directory:', font=('tahoma', 9))
label_filename.place(x=60,y=y_position-30)

text_NumberOfFrames=tk.Text(root, width=7,height=1, font=('tahoma', 9), bd=1)
text_NumberOfFrames.place(x=745, y=y_position)
label_NumberOfFrames=tk.Label(root, text='Frames', font=('tahoma', 9))
label_NumberOfFrames.place(x=815,y=y_position)

text_clipLimit=tk.Text(root, width=4,height=1, font=('tahoma', 9), bd=1)
text_clipLimit.place(x=640, y=565)
label_clipLimit=tk.Label(root, text='Clip Limit:', font=('tahoma', 9))
label_clipLimit.place(x=570,y=565)
text_clipLimit.delete('1.0', tk.END)
text_clipLimit.insert('1.0', clipLimit)

text_file_num = tk.Text(root, width=4,height=1, font=('tahoma', 9), bd=1)
text_file_num.place(x=255, y=565)
label_file_num = tk.Label(root, text='files', font=('tahoma', 9))
label_file_num.place(x=305,y=565)

y_position = 429
text_filenames=tk.Text(root, width=115,height=7, font=('tahoma', 9), bd=1)
text_filenames.place(x=60, y=y_position)

text_clipLimit.delete('1.0', tk.END)
text_clipLimit.insert('1.0', clipLimit)

# //////// Combo /////////////////////

y_position = 660

combo_target_format = ttk.Combobox(root, width=7, height=1, font=('tahoma', 8))
combo_target_format.place(x=60, y=y_position+5)
label_target_format = tk.Label(root, text='Output Format:', font=('tahoma', 8))
label_target_format.place(x=60,y=y_position-20)
combo_target_format['values'] = ('AVI', 'MP4')
combo_target_format['state'] = 'readonly'

combo_target_format.set('AVI')

#/////////////Button///////////////////////////////////////////////////////////////
button_browse=ttk.Button(root, text='Browse...', width=20, command=browseFileButton)
button_browse.place(x=60, y=565)

button_load=ttk.Button(root, text='Load', width=20, command=loadFileButton)
button_load.place(x=380, y=565)

button_convert=ttk.Button(root, text='Convert', width=20, command=convertVideoButton)
button_convert.place(x=720, y=565)

button_about=ttk.Button(root, text='About...', width=20, command=about)
button_about.place(x=380, y=660)

button_close=ttk.Button(root, text='Exit', width=20, command=root.destroy)
button_close.place(x=720, y=660)


# In[12]:


cv2.destroyAllWindows()


# In[13]:


root.mainloop()

